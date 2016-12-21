### WordpostBot: Facebook post bot

### Functionality:
  Make posts to a Facebook page containing a word and the definition of that word

### Setup:
  These instructions are written for a linux environment because that is the environment in which it was developed and is used.
  After pulling this repository, set up a virtualenv environment for this project and install the packages that are specified in requirements.txt in that environment.
  Next, create the database in MySQL that you want to use to store the Posts and then run tbl_create.sql on this database to create the Posts table within that database. 
  Then, create a file in the Project directory called config.py with definitions of some data. Here is an example config file (the names of the variables and key mappings inside the dictionaries must match these to work with the make_post.py script):
```
# Do NOT commit this file to github
# This file contains your wordnik api key, the private 
# access token for the Facebook page, and private database info

wordnik_key = "<Your wordnik api key>"

page_info = {
	"page_id": "<Your facebook page id>",
	"access_token": "<Your access token to post to your page via the Facebook graph API>"
}

db_info = {
	"host": "<Host of the database, probably 'localhost' if the database is on the machine that will run the make_post.py script>",
	"user": "<User that owns the database>", 
	"password": "<MySQL password for that user",
	"db": "<Database name>",
}
```

  Once the database is created, the Posts table is created in that database, and the config.py file is populated with correct info, make posts to the specified Facebook page by running make_post.py.
```
python make_post.py
```

### Facebook Page:
  https://www.facebook.com/WordpostBot
