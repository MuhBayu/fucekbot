from dotenv import load_dotenv
load_dotenv()
import os
import tweepy
import schedule
import time
import re
import datetime
from util.Mongo import tweet_collection

def app():
	dms = api.list_direct_messages()
	for i,dm in enumerate(dms):
		if i > 4:
			break
		sender_id = dm.message_create['sender_id']
		message_data = dm.message_create['message_data']
		text = message_data['text']
		find_tco_url = re.findall('http[s]?://t.co/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
		if find_tco_url:
			text = [text.replace(w, "") for w in find_tco_url]
			text = re.sub("\s\s+", " ", text[0])

		check_double_tweet = tweet_collection.find_one({
			"sender_id": sender_id,
			"text": text
		})
		if check_double_tweet:
			api.send_direct_message(recipient_id=sender_id, text="Anda udah pernah ngirim ini!! Jangan ngirim lagi")
		else:
			if text[0:6].lower() == 'fucek ':
				update = api.update_status(status=text)
				print("------------------------------------")
				print(f"| Text: {text}")
				print(f"| Sender ID: {sender_id}")
				print("------------------------------------")
				if update:
					tweet_collection.insert_one({
						"sender_id": sender_id,
						"text": text,
						"tweet_id": update._json['id_str'],
						"created_timestamp": dm.created_timestamp,
						"last_modified": datetime.datetime.utcnow()
					})
		api.destroy_direct_message(dm.id)

if __name__ == "__main__":
	pid = str(os.getpid())
	pidfile = "worker.pid"
	f = open(pidfile, "w")
	f.write(pid)
	f.close()
	auth = tweepy.OAuthHandler(os.getenv('TWIT_CONSUMER_TOKEN'), os.getenv('TWIT_CONSUMER_SECRET'))
	auth.secure = True
	auth.set_access_token(os.getenv('TWIT_ACCESS_TOKEN'), os.getenv('TWIT_ACCESS_TOKEN_SECRET'))
	api = tweepy.API(auth)

	schedule.every(1).minutes.do(app)
	try:
		print("Service running, CTRL+C to stop")
		while True:
			schedule.run_pending()
			time.sleep(1)
	except Exception as e:
		print(str(e))
	except KeyboardInterrupt:
		print("Stopped.")
	finally:
		if os.path.isfile(pidfile):
			os.unlink(pidfile)
		print('Done.')