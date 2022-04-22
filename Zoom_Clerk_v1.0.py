import jwt
import requests
import json
import datetime
from csv import reader
from csv import writer, DictWriter

#get the authentications via jwt
headers={"alg": "HS256","typ": "JWT"}

def generateToken(expiration_time):
	# we want our token to expire after 5 minutes
	current_time=datetime.datetime.now()
	expiration=current_time+datetime.timedelta(seconds=expiration_time)
	converted_expiration= round(expiration.timestamp())
	# generate payload using ApiKey and set expiration time
	payload={"iss": "API Key","exp": converted_expiration}
	encoded_jwt = jwt.encode(payload,"API Secret", algorithm="HS256")
	return encoded_jwt

# schedule the meeting
def schedule_meeting(user_email_address,meeting_info_formatted,encoded_jwt):
	url= f"https://api.zoom.us/v2/users/{user_email_address}/meetings"
	header={"authorization":f"Bearer {encoded_jwt}"}
	request=requests.post(url, json=meeting_info_formatted, headers=header)
	meet_details=request.json()
	join_url=meet_details["join_url"]
	password=meet_details["password"]
	print(f"The meeting url of zoom meeting is {join_url},and the password is {password}.")
	return join_url, password


def generate_meeting_info(topic_title,start_time,duration):
	start_time_converted=datetime.datetime(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4]).strftime("%Y-%m-%dT%H:%M:%SZ")
	meeting_info={"topic":topic_title,
		"type":2, #type 2 means scheduled meeting
		"start_time":start_time_converted,
		"duration":duration,
		"timezone":"America/New_York",
		"settings":{"mute_upon_entry":True, "join_before_host":False,"auto_recording": "local"}
	}
	return meeting_info

# this function is used to adapt a specific time and date format we use in csv into the required format
def format_time_and_date(time_and_date):
	time0=time_and_date[2].split(" ")[0].split("/")
	time1=time_and_date[2].split(" ")[1].split(":")
	time0.extend(time1)
	start_time=[int(i) for i in time0]
	start_time.insert(0,start_time[2]+2000)
	start_time.pop(3)
	return start_time


encoded_jwt1=generateToken(300)

with open("SampleZoomAssignment.csv") as file:
	csv_reader=reader(file)
	next(csv_reader) #skip headers
	data=list(csv_reader)
	file.seek(0)
	csv_reader1=reader(file)
	data_full=list(csv_reader1)
	csv_headers=data_full[0]


for row in data:
	topic_title=row[0]
	user=row[1]
	start_time=format_time_and_date(row)
	duration=row[3]
	request_meeting_info=generate_meeting_info(topic_title,start_time,duration)
	response=schedule_meeting(user,request_meeting_info,encoded_jwt1)
	row[4]=response[0]
	row[5]=response[1]

# record the join_urls and passcodes into csv files
with open("SampleZoomAssignment.csv","w", newline='') as file:
	csv_writer=writer(file)
	csv_writer.writerow(csv_headers)
	for row in data:
		csv_writer.writerow(row)












