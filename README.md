# WordpostBot: Facebook post bot

## Functionality:
  Make posts to a Facebook page containing a word and the definition of that word.

## Setup:
  These instructions are written for a linux environment because that is the environment in which WordpostBot was developed and is used. It is assumed that Python 2, virtualenv, pip, and MySQL are already installed.

  After pulling this repository, set up a virtualenv environment for this project and install the packages that are specified in requirements.txt in that environment:
```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
  Next, create the database that you want to use to store the Posts in MySQL and then run tbl_create.sql on this database to create the Posts table within that database:
```bash
$ # After creating the database (WordpostBot uses a UTF-8 database)
$ mysql <database> -u <username> -p < tbl_create.sql
``` 
  Then, create a file in the Project directory called config.py with definitions of some data. Here is an example config file to fill out (**the names of the variables and key mappings inside the dictionaries must match these to work with the make_post.py script**):
```python
# Do NOT commit this file to github
# This file contains your wordnik api key, the private 
# access token for the Facebook page, and private database info

wordnik_key = "<Your wordnik api key>"

page_info = {
	"page_id": "<Your facebook page id>",
	"access_token": "<Your access token to post to your page via the Facebook graph API>"
}

db_info = {
	"host": "<Host of the database; probably 'localhost' if the database is on the machine that will run the make_post.py script>",
	"user": "<MySQL user that can modify the database>", 
	"password": "<MySQL password for that user",
	"db": "<Database name>",
}
```

  Once the database is created, the Posts table is created in that database, and the config.py file is populated with correct info, you can make a post to the specified Facebook page by running make_post.py:
```bash
$ python make_post.py
```

## Usage
  The make_post.py script is meant to be automated to run in time intervals. For example, WordpostBot runs this script every 30 minutes.
  
  The error log for the script will be created at Project/error.log and will document any errors.
  A log file for posts will be created at Project/posts.log and will document posts that are successfully completed and comments that are added on those posts by the bot.

## [Facebook Page](https://www.facebook.com/WordpostBot)
