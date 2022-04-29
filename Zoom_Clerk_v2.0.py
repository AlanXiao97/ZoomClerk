import jwt
import requests
import json
import datetime
from csv import reader
from csv import writer, DictWriter

#get the authentications via jwt
headers={"alg": "HS256","typ": "JWT"}

def read_auth_info(filename):
	with open(filename) as file:
		csv_reader=reader(file)
		next(csv_reader) #skip header
		data=list(csv_reader)
		return data

def generateToken(expiration_time,api_key,api_secret):
	# we want our token to expire after 5 minutes
	current_time=datetime.datetime.now()
	expiration=current_time+datetime.timedelta(seconds=expiration_time)
	converted_expiration= round(expiration.timestamp())
	# generate payload using ApiKey and set expiration time
	payload={"iss": api_key,"exp": converted_expiration}
	encoded_jwt = jwt.encode(payload,api_secret, algorithm="HS256")
	return encoded_jwt

# schedule the meeting
# this function is used to adapt a specific time and date format we use in csv into the required format
def format_time_and_date(time_and_date):
	time0=time_and_date[2].split(" ")[0].split("/")
	time1=time_and_date[2].split(" ")[1].split(":")
	time0.extend(time1)
	start_time=[int(i) for i in time0]
	start_time.insert(0,start_time[2])
	start_time.pop(3)
	return start_time

def generate_meeting_info(topic_title,start_time,duration):
	start_time_converted=datetime.datetime(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4]).strftime("%Y-%m-%dT%H:%M:%S")
	meeting_info={"topic":topic_title,
		"type":2, #type 2 means scheduled meeting
		"start_time":start_time_converted,
		"duration":duration,
		"timezone":"America/New_York",
		"settings":{"mute_upon_entry":True, 
					"join_before_host":False,
					"auto_recording": "cloud",
					"approval_type":0
					}
	}
	return meeting_info

def schedule_meeting(user_email_address,meeting_info_formatted,encoded_jwt):
	url= f"https://api.zoom.us/v2/users/{user_email_address}/meetings"
	header={"authorization":f"Bearer {encoded_jwt}"}
	request=requests.post(url, json=meeting_info_formatted, headers=header)
	meet_details=request.json()
	join_url=meet_details["join_url"]
	meetingID=meet_details["id"]
	print(f"The meeting url of zoom meeting is {join_url}.")
	return join_url,meetingID

def update_registration_question(meetingID,encoded_jwt):
	url= f"https://api.zoom.us/v2/meetings/{meetingID}/registrants/questions"
	header={"authorization":f"Bearer {encoded_jwt}"}
	registration_info={"custom_questions":[{"required":True,"title":"What's your order number?","type":"short"}],"questions":[{"field_name":"last_name","required":True},{"field_name":"phone","required":True}]}
	request=requests.patch(url, json=registration_info, headers=header)

#COMMAND
api_credential=input("Input the name of the csv file with API key and secret pair (exclude .csv extension). ")

api_data=read_auth_info(f"{api_credential}.csv")
api_key=api_data[0][1]
api_secret=api_data[0][2]
encoded_jwt1=generateToken(300,api_key,api_secret)

name_of_meeting_csv=input("Input the name of the csv file with meeting information (exclude .csv extension). ")

with open(f"{name_of_meeting_csv}.csv") as file:
	csv_reader=reader(file)
	next(csv_reader) #skip headers
	meeting_details=list(csv_reader)
	file.seek(0)
	csv_reader1=reader(file)
	meeting_details_with_title=list(csv_reader1)
	csv_headers=meeting_details_with_title[0]

for row in meeting_details:
	topic_title=row[0]
	user=row[1]
	start_time=format_time_and_date(row)
	# print(start_time)
	duration=row[3]
	request_meeting_info=generate_meeting_info(topic_title,start_time,duration)
	response=schedule_meeting(user,request_meeting_info,encoded_jwt1)
	row[4]=response[0] #join_url
	row[5]=response[1] #meetingID
	# update the registration question using the meetingID just generated
	update_registration_question(response[1],encoded_jwt1)

# record the join_urls and passcodes into csv files
with open(f"{name_of_meeting_csv}1.csv","w", newline='') as file:
	csv_writer=writer(file)
	csv_writer.writerow(csv_headers)
	for row in meeting_details:
		csv_writer.writerow(row)














