#######################################################################################
# Yourname: Phuriphat Arunphaisan
# Your student ID: 66070305
# Your GitHub Repo: https://github.com/NonsanXX/IPA2025-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import restconf_final, netconf_final, netmiko_final, ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv
import re

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
method = None

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
    try:
        message = messages[0]["text"]
    except KeyError:
        print("Message text not found.")
        continue
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/66070305"):

        # parse message tokens
        parts = message.split()
        ip = None
        command = None
        print(parts)

        # Reset responseMessage for this loop
        responseMessage = None 

        # Case 1: Full command /66070305 <ip> <command>
        if len(parts) >= 3:
            ip = parts[1]
            command = parts[2]
            print("IP: {}, Command: {}".format(ip, command))
            # Validate IP format
            if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
                responseMessage = f"Error: Invalid IP address '{ip}'"
        
        # Case 2: Partial command /66070305 <argument>
        elif len(parts) == 2:
            arg = parts[1]
            # Check if it's a method-setting command
            if arg in ["restconf", "netconf"]:
                method = arg
                responseMessage = f"Ok: {method.title()}"
                print(f"Method set to: {method}")
            # Check if it's an IP (missing a command)
            elif not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", arg):
                responseMessage = "Error: No IP specified"
                print("No IP specified")
            # Otherwise, it's a command (missing an IP)
            else:
                command = arg # ip remains None

        # 5. Complete the logic for each command
        try:
            # If responseMessage was already set (e.g., "Ok: Restconf" or "Invalid IP"), skip command execution
            if method is None:
                print("No method selected.")
                responseMessage = "Error: No method specified"
            
            elif responseMessage:
                pass
            
            # --- Method-based command execution ---
            elif method == "restconf":
                if command == "create":
                    responseMessage = restconf_final.create(ip)
                elif command == "delete":
                    responseMessage = restconf_final.delete(ip)
                elif command == "enable":
                    responseMessage = restconf_final.enable(ip)
                elif command == "disable":
                    responseMessage = restconf_final.disable(ip)
                elif command == "status":
                    responseMessage = restconf_final.status(ip)
                elif command == "gigabit_status":
                    responseMessage = netmiko_final.gigabit_status(ip)
                elif command == "showrun":
                    responseMessage = ansible_final.showrun(ip)
                else:
                    print("No command found.")
                    responseMessage = "Error: No command found."
            
            elif method == "netconf":
                if command == "create":
                    responseMessage = netconf_final.create(ip)
                elif command == "delete":
                    responseMessage = netconf_final.delete(ip)
                elif command == "enable":
                    responseMessage = netconf_final.enable(ip)
                    responseMessage = netconf_final.enable(ip)
                elif command == "disable":
                    responseMessage = netconf_final.disable(ip)
                elif command == "status":
                    responseMessage = netconf_final.status(ip)
                elif command == "gigabit_status":
                    responseMessage = netmiko_final.gigabit_status(ip)
                elif command == "showrun":
                    responseMessage = ansible_final.showrun(ip)
                else:
                    print("No command found.")
                    responseMessage = "Error: No command found."

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
        
        # Check if responseMessage is a dictionary (from ansible_final.showrun) and has status 'ok'
        if command == "showrun" and isinstance(responseMessage, dict) and responseMessage.get("status") == "ok":

            hostname = str(responseMessage.get('hostname')).strip('"').strip()
            filepath = f"backups/show_run_66070305_{hostname}.txt"
            filename = f"show_run_66070305_{hostname}.txt"
            
            try:
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
            except FileNotFoundError:
                print(f"Error: Backup file not found at {filepath}")
                responseMessage = f"Error: Ansible OK, but backup file '{filename}' not found."
                # Fall through to the 'else' block to send this new error as text
            except Exception as e:
                print(f"Error preparing file attachment: {e}")
                responseMessage = f"Error: Could not attach file. {e}"
                # Fall through to the 'else' block

        # other commands only send text, or no attached file.
        # This 'if' condition is crucial to avoid re-entering the block above
        if not (command == "showrun" and isinstance(responseMessage, dict) and responseMessage.get("status") == "ok"):
            postData = {"roomId": roomIdToGetMessages, "text": str(responseMessage)} # Ensure response is a string
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
