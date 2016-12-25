from config import *
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from time import ctime
import os
import codecs
import requests

# Change working directory to the directory of this script so log files
# are created in this directory no matter where the script is run
os.chdir(os.path.dirname(os.path.abspath(__file__)))
error_log = codecs.open("error.log", "a+", "utf-8")
posts_log = codecs.open("posts.log", "a+", "utf-8")

def write_to_log(log_file, message):
	log_file.write("["+ctime()+"]:\t"+message+"\n")

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

def get_request_json(url, params=None):
	r = requests.get(url, params)
	r.raise_for_status()
	return r.json()

def post_to_page(route, message):
	data = {
		"message": message,
		"access_token": page_info["access_token"]
	}
	r = requests.post("https://graph.facebook.com/v2.8/"+route, data=data)
	r.raise_for_status()
	return r.json()["id"]
