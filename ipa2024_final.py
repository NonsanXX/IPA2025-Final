#######################################################################################
# Yourname: Phuriphat Arunphaisan
# Your student ID: 66070305
# Your GitHub Repo: https://github.com/NonsanXX/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import restconf_final, netmiko_final, ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"

# Get room title once before the loop
r = requests.get(
    "https://webexapis.com/v1/rooms/{}".format(roomIdToGetMessages),
    headers={"Authorization": "Bearer " + ACCESS_TOKEN}
)

if not r.status_code == 200:
    raise Exception(
        "Incorrect reply from Webex Teams API. Status code: {}".format(
            r.status_code
        )
    )

json_data = r.json()
roomTitle = json_data["title"]
print("Room Title: " + roomTitle)

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": "Bearer " + ACCESS_TOKEN}

    # 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.

    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(
                r.status_code
            )
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]

    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/66070305"):

        # extract the command
        try:
            command = message.split(" ")[1]
            print(command)
        except IndexError:
            command = None
            print("No command found.")

        # 5. Complete the logic for each command

        try:
            if command == "create":
                responseMessage = restconf_final.create()
            elif command == "delete":
                responseMessage = restconf_final.delete()
            elif command == "enable":
                responseMessage = restconf_final.enable()
            elif command == "disable":
                responseMessage = restconf_final.disable()
            elif command == "status":
                responseMessage = restconf_final.status()
            elif command == "gigabit_status":
                responseMessage = netmiko_final.gigabit_status()
            elif command == "showrun":
                responseMessage = ansible_final.showrun()
            else:
                responseMessage = "Error: No command or unknown command"
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
            responseMessage = f"Error: Failed to execute command '{command}'"

        # 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type

        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok';
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail
        

        if command == "showrun" and responseMessage == "ok":

            filepath = "backups/show_run_66070305_R1-Exam.txt"
            filename = "show_run_66070305_R1-Exam.txt"
            fileobject = open(filepath, "rb")
            filetype = "text/plain"
            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
            "Authorization": "Bearer " + ACCESS_TOKEN,
            "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(
                    r.status_code
                )
            )
