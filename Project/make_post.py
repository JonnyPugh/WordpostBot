#!/usr/bin/env python

from extensions import *
from config import *
from sets import Set
from re import match

def get_wordnik_json(route, extra_params):
	params = {
		"limit": 1,
		"api_key": wordnik_key
	}
	params.update(extra_params)
	request_json = []
	while not request_json:
		request_json = get_request_json("https://api.wordnik.com/v4/"+route, params)
	return request_json

def post_word(route, word):
	word_info = get_wordnik_json("word.json/"+word+"/definitions", {})[0]
	definition = word_info["text"]
	return post_to_page(route, word+(" - "+word_info["partOfSpeech"] if "partOfSpeech" in word_info else "")+"\n"+definition), definition

def post_root_word(post_id, word, definition):
	# If the definition matches any of these patterns, post
	# the word that is referenced in the definition
	for pattern in [s + " ([^ ]*)[.]" for s in [".* form of", ".* participle of", "See", "Variant of", ".*[.] See Synonyms at", "Alternative spelling of", "Relating to", "An abbreviation of", "Common misspelling of", "Of or pertaining to", "Superlative of", "Obsolete spelling of", "Informal", "To", "The act or process of", "One who believes in"]] + ["([^ .]*)[.]?", "Alternative capitalization of ([^ ]*)", "In an? ([^ ]*) manner."]:
		reference_word = match("^"+pattern+"$", definition)
		if reference_word:
			root_word = reference_word.group(1)

			# If the definition is a single word, make it lowercase because
			# the wordnik API is case sensitive and single word definitions
			# may have been capitalized
			if pattern == "([^ .]*)[.]?":
				root_word = root_word.lower()

			# Post the root word and write to the log
			post_id, new_definition = post_word(post_id+"/comments", root_word)
			write_to_log(posts_log, "Posted comment definition of word '"+root_word+"' on post with definition of '"+word+"'")

			# Save off the id of the first posted comment because all subsequent
			# comments should be replies to this initial comment
			if not post_root_word.comment_id:
				post_root_word.comment_id = post_id

			# Check the root word's definition for other referenced words
			post_root_word(post_root_word.comment_id, root_word, new_definition)
post_root_word.comment_id = None

def main():
	# Get a random word that has not been posted yet
	posted_words = Set([post["word"] for post in execute_query("select word from Posts")])
	while True:
		word = get_wordnik_json("words.json/randomWords", {"minLength": 0})[0]["word"]
		if word not in posted_words:
			break
		write_to_log(error_log, "Word: '"+word+"' already posted, posting another...")

	# Make a post, insert its data into the database, and log it
	post_id, definition = post_word(page_info["page_id"]+"/feed", word)
	execute_query("insert into Posts (id, word) values (%s, %s)", (post_id, word))
	write_to_log(posts_log, "Finished posting word - "+word)

	# If the posted word references a root word, post the 
	# definition of the root word as a comment
	post_root_word(post_id, word, definition)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(error_log, "Unexpected error caught while making a post: "+str(e))
