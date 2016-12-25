#!/usr/bin/env python

from extensions import *
from config import page_info
from operator import itemgetter

def main():
	# Form list of IDs of all posts made to the page
	post_ids = [post["id"] for post in execute_query("select id from Posts")]

	# Form reaction info for each post made to the page
	users = {}
	user_names = {}
	for post_id in post_ids:
		json = get_request_json("https://graph.facebook.com/v2.8/"+post_id+"/reactions", {"access_token": page_info["access_token"]})
		while json["data"]:
			for reaction in json["data"]:
				user_id = reaction["id"]
				user_names[user_id] = reaction["name"]
				if user_id not in users:
					users[user_id] = {}
				reaction_type = reaction["type"].lower()
				if reaction_type not in users[user_id]:
					users[user_id][reaction_type] = 0
				users[user_id][reaction_type] += 1
			if "next" not in json["paging"]:
				break
			json = get_request_json(json["paging"]["next"])

	# Form the reaction info strings for all users
	overall_total_reactions = 0
	users_info = []
	for user_id, user_info in users.items():
		reactions_breakdown = ", ".join(["%s %s" % (value, key) for (key, value) in sorted(user_info.items(), key=itemgetter(1), reverse=True)])+" reactions"
		total_reactions = sum([value for value in user_info.values()])
		users_info.append((total_reactions, user_names[user_id]+" "+str(total_reactions)+": "+reactions_breakdown))
		overall_total_reactions += total_reactions

	# Form the message to post to the page
	number_of_reactors = 10
	message = "***Top "+str(number_of_reactors)+" reactors***\nFormat: '<rank>. <name> <total reactions>: <individual reactions>'\n"
	ranking = 1
	for reactions_info in sorted(users_info, key=lambda x: x[0], reverse=True)[:number_of_reactors]:
		message += str(ranking)+". "+reactions_info[1]+"\n"
		ranking += 1
	message += "Average reactions per post: "+str(float(overall_total_reactions) / len(post_ids))

	# Post the message to the page and log it
	post_to_page(page_info["page_id"]+"/feed", message)
	write_to_log(posts_log, "Finished posting statistics")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(error_log, "Unexpected error caught while posting statistics: "+str(e))
