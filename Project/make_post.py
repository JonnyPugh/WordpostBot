#!/usr/bin/env python

from config import *
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from math import ceil
from sets import Set
from re import match
import requests
import time
import os
import codecs

def connect_to_database():
    options = {
        "host": db_info["host"],
        "user": db_info["user"],
        "passwd": db_info["password"],
        "db": db_info["db"],
        "cursorclass" : DictCursor
    }
    db = connect(**options)
    db.autocommit(True)
    return db
db = connect_to_database()

def execute_query(query, params=None):
    cursor = db.cursor()
    cursor.execute(query, params)
    query_results = cursor.fetchall()
    cursor.close()
    return query_results

def get_wordnik_json(route, extra_params):
	params = {
		"limit": 1,
		"api_key": wordnik_key
	}
	params.update(extra_params)
	request_json = []
	while not request_json:
		request = requests.get("https://api.wordnik.com/v4/"+route, params=params)
		request.raise_for_status()
		request_json = request.json()
	return request_json

def post_word(route, word):
	word_info = get_wordnik_json("word.json/"+word+"/definitions", {})[0]
	definition = word_info["text"]
	data = {
		"message": word+(" - "+word_info["partOfSpeech"] if "partOfSpeech" in word_info else "")+"\n"+definition,
		"access_token": page_info["access_token"]
	}
	r = requests.post("https://graph.facebook.com/v2.8/"+route, data=data)
	r.raise_for_status()
	return r.json()["id"], definition

def post_root_word(post_id, word, definition):
	for pattern in [".*? form of", ".*? participle of", "See", "Variant of", ".*?[.] See Synonyms at", "Alternative spelling of", "Relating to", "An abbreviation of", "Common misspelling of", "Of or pertaining to"]:
		reference_word = match(pattern+" ([^ ]*?)[.]", definition)
		if reference_word:
			root_word = reference_word.group(1)
			post_id, new_definition = post_word(post_id+"/comments", root_word)
			write_to_log(posts_log, "Posted comment definition of word '"+root_word+"' on post with definition of '"+word+"'")
			post_root_word(post_id, root_word, new_definition)

def write_to_log(log_file, message):
	log_file.write("["+time.ctime()+"]:\t"+message+"\n")

# Change working directory to the directory of this script so log files
# are created in this directory no matter where the script is run
os.chdir(os.path.dirname(os.path.abspath(__file__)))
error_log = codecs.open("error.log", "a+", "utf-8")
posts_log = codecs.open("posts.log", "a+", "utf-8")

def main():
	# Get a random word that has not been posted yet
	posted_words = Set([post["word"] for post in execute_query("select word from Posts")])
	while True:
		word = get_wordnik_json("words.json/randomWords", {"minLength": 0})[0]["word"]
		if word in posted_words:
			write_to_log(error_log, "Word: '"+word+"' already posted, posting another...")
			continue
		break

	# Make a post, insert its data into the database, and log it
	post_id, definition = post_word(page_info["page_id"]+"/feed", word)
	execute_query("insert into Posts values (%s, %s, %s)", (int(ceil(time.time())), post_id, word))
	write_to_log(posts_log, "Finished posting word - "+word)

	# If the posted word references a root word, post the 
	# definition of the root word as a comment
	post_root_word(post_id, word, definition)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(error_log, "Unexpected error caught: "+str(e))
