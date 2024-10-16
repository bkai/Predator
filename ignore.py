# Copyright (C) 2024 V0LT - Conner Vieira

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.





# This library is responsible for handling 'ignore lists', which allow administrators to define a list of license plates that should be ignored.

# Ignore lists might be used to prevent common vehicles from being recorded in order to keep logs organized, or to prevent privacy-concerned visitors from having their license plate processed.

# Custom ignore lists can be enabled and disabled in the configuration.


import os # Required to interact with certain operating system functions.
import json # Required to process JSON data.
import time # Required to manage delays.
import validators # Required to validate URLs.

import utils
style = utils.style
display_message = utils.display_message

predator_root_directory = str(os.path.dirname(os.path.realpath(__file__))) # This variable determines the folder path of the root Predator directory. This should usually automatically recognize itself, but it if it doesn't, you can change it manually.

try:
    if (os.path.exists(predator_root_directory + "/config.json")):
        config = json.load(open(predator_root_directory + "/config.json")) # Load the configuration database from config.json
    else:
        print("The configuration file doesn't appear to exist at " + predator_root_directory + "/config.json.")
        exit()
except:
    print("The configuration database couldn't be loaded. It may be corrupted.")
    exit()



if (config["developer"]["offline"] == False): # Only import networking libraries if offline mode is turned off.
    import requests # Required to fetch information from network hosts.


def fetch_ignore_list():
    predator_root_directory = str(os.path.dirname(os.path.realpath(__file__))) # This variable determines the folder path of the root Predator directory. This should usually automatically recognize itself, but it if it doesn't, you can change it manually.

    config = json.load(open(predator_root_directory + "/config.json")) # Load the configuration database from config.json



    complete_ignore_list = [] # This will hold the complete list of plates to ignore, after all ignore list sources have been loaded.

    if (config["developer"]["ignore_list"]["enabled"] == True): # Only load the local ignore list file if the ignore list is enabled in the configuration.

        local_ignore_list_file = config["developer"]["ignore_list"]["local_file"]
        if (local_ignore_list_file != ""): # Only load the local ignore list file if it exists.
            if (os.path.exists(local_ignore_list_file) == True):
                loaded_local_ignore_list_file = open(local_ignore_list_file, "r") # Open the local ignore list file.
                local_ignore_list = json.loads(loaded_local_ignore_list_file.read()) # Read the contents of the file.
                loaded_local_ignore_list_file.close() # Close the file.

                for entry in local_ignore_list: # Iterate through each entry in the local ignore list, and add it to the complete ignore list.
                    complete_ignore_list.append(entry)
            else:
                display_message("The local ignore list file does not exist. The local ignore list is effectively disabled.", 3)


    remote_ignore_sources = ["https://v0lttech.com/predator/manifest/serve.php?type=ignore&user=cvieira&list=publicignorelist"] # This holds a list of hard-coded remote sources that ignore lists will be fetched from. Developers who want to deploy Predator to devices can add remote sources for ignore lists here to make them easier to manage. This allows administrators to automatically issue ignore lists from an external services. Administrators can maintain ignore lists without needing to manually modify the local ignore list for all their devices. Remote sources don't receive any telemetry from Predator, only a simple JSON list is fetched. Custom remote sources from the configuration are added in the next steps.

    if (config["developer"]["ignore_list"]["enabled"] == True): # Only add custom remote sources if custom ignore lists are enabled in the configuration
        for source in config["developer"]["ignore_list"]["remote_sources"]: # Iterate through each source in the list of remote ignore list sources.
            remote_ignore_sources.append(source) # Add the remote source to the list of remote sources.

    if (config["developer"]["offline"] == True): # If offline mode is enabled, then remove all remote ignore list sources.
        remote_ignore_sources = [] # Set this list of remote ignore list sources to a blank list.

    for host in remote_ignore_sources: # Iterate through all of the hosts specified in the list of remote ignore list sources.
        if (validators.url(host)): # Verify that this 'host' value is a valid URL.
            try: # Run the network request in a try block so the entire program doesn't fail if something goes wrong.
                response = requests.get(host, timeout=2.0) # Make a request to this host that times out after 2 seconds.
                response_content = response.text # Grab the text from the response.
            except: # If the network request fails, do the following steps instead.
                response_content = "[]" # Use a blank placeholder response database.

            try: # Run the JSON load function in a 'try' block to prevent fatal crashes if the data returned by the remote source isn't valid JSON.
                remote_ignore_list = json.loads(response_content)
            except: # If the list fails to load, it's likely because it's not valid JSON data.
                remote_ignore_list = [] # Set the loaded list to a blank placeholder list.

            for entry in remote_ignore_list: # Iterate through each entry in this remote ignore list, and add it to the complete ignore list.
                complete_ignore_list.append(entry)

        else: # This remote ignore list source is not a valid URL.
            pass



    sanitized_ignore_list = []
    for entry in complete_ignore_list:
        if (len(entry) < 25): # Verify that this entry is a reasonable length.
            sanitized_ignore_list.append(entry.upper()) # Convert this entry to all uppercase letters, and add it to the sanitized list.


    final_ignore_list = list(dict.fromkeys(sanitized_ignore_list)) # De-duplicate the ignore list to make processing more efficient.
    return final_ignore_list
