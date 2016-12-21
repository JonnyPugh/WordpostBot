from config import *
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from math import ceil
from sets import Set
import requests
import time

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

def write_to_log(log_file, message):
	log_file.write("["+time.ctime()+"]:\t"+message+"\n")

error_log = open("error.log", "a+")

def main():
	# Form a set of all posted words to prevent reposts
	posted_words = Set([post["word"] for post in execute_query("select word from Posts")])

	# Get word data to post
	while True:
		word = get_wordnik_json("words.json/randomWords", {"minLength": 0})[0]["word"]
		if word in posted_words:
			write_to_log(error_log, "Word: '"+word+"' already posted, posting another...")
			continue
		break
	definition = get_wordnik_json("word.json/"+word+"/definitions", {})[0]

	# Make a post, insert its data into the database, and log it
	data = {
		"message": word+(" - "+definition["partOfSpeech"] if "partOfSpeech" in definition else "")+"\n"+definition["text"],
		"access_token": page_info["access_token"]
	}
	r = requests.post("https://graph.facebook.com/v2.8/"+page_info["page_id"]+"/feed", data=data)
	r.raise_for_status()
	execute_query("insert into Posts values (%s, %s, %s)", (int(ceil(time.time())), r.json()["id"], word))
	with open("posts.log", "a+") as posts_log:
		write_to_log(posts_log, "Finished posting word - "+word)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(error_log, "Unexpected error caught: "+str(e))
