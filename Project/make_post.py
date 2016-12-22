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
	definition = get_wordnik_json("word.json/"+word+"/definitions", {})[0]
	data = {
		"message": word+(" - "+definition["partOfSpeech"] if "partOfSpeech" in definition else "")+"\n"+definition["text"],
		"access_token": page_info["access_token"]
	}
	r = requests.post("https://graph.facebook.com/v2.8/"+route, data=data)
	r.raise_for_status()
	return r.json()["id"], definition["text"]

def write_to_log(log_file, message):
	log_file.write("["+time.ctime()+"]:\t"+message+"\n")

# Change working directory to the directory of this script so log files
# are created in this directory no matter where the script is run
os.chdir(os.path.dirname(os.path.abspath(__file__)))
error_log = open("error.log", "a+")

def main():
	# Form a set of all posted words to prevent reposts
	posted_words = Set([post["word"] for post in execute_query("select word from Posts")])

	# Get word to post
	while True:
		word = get_wordnik_json("words.json/randomWords", {"minLength": 0})[0]["word"]
		if word in posted_words:
			write_to_log(error_log, "Word: '"+word+"' already posted, posting another...")
			continue
		break

	# Make a post, insert its data into the database, and log it
	post_id, definition = post_word(page_info["page_id"]+"/feed", word)
	execute_query("insert into Posts values (%s, %s, %s)", (int(ceil(time.time())), post_id, word))
	with open("posts.log", "a+") as posts_log:
		write_to_log(posts_log, "Finished posting word - "+word)

		# If the posted word was plural, post the 
		# definition of the root word as a comment
		plural_word = match("Plural form of (.*?)[.]", definition)
		if plural_word:
			root_word = plural_word.group(1)
			post_word(post_id+"/comments", root_word)
			write_to_log(posts_log, "Posted comment definition of word '"+root_word+"' on post with definition of '"+word+"'")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(error_log, "Unexpected error caught: "+str(e))
