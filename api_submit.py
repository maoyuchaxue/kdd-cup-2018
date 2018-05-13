# coding: utf-8
import private_config
import requests
 
files={'files': open(private_config.submit_file,'rb')}

data = {
    "user_id": private_config.userid,   #user_id is your username which can be found on the top-right corner on our website when you logged in.
    "team_token": private_config.team_token, #your team_token.
    "description": private_config.description,  #no more than 40 chars.
    "filename": private_config.filename, #your filename
}
 
url = 'https://biendata.com/competition/kdd_2018_submit/'
 
response = requests.post(url, files=files, data=data)
 
print(response.text)