import requests
import random
import time
import json

# enable diagnostics
DIAG=True

# Shodan API key
SHODAN_API_KEY = ""

# Discord webhook URL
DISCORD_WEBHOOK_URL = ""


# Set up the Shodan API with a query parameter
query = "has_screenshot:true ssl:edu"
shodan_api_url = "https://api.shodan.io/shodan/host/search?key={}&query={}".format(SHODAN_API_KEY, query)

def init_query(shodan_api_url, query):
    print("Searching for hosts with keyword '{}'...".format(query))
    # Send a search request to the Shodan API

    try:
        response = requests.get(shodan_api_url, timeout=1000)
    except Exception as e: # catch exceptions
        if DIAG: print(e) # enabled diagnostics
        time.sleep(60) # sleep, failsafe initiated
        init_query(shodan_api_url, query) # start from initial query
    if response.status_code == 200: # continue if 200 on GET
        # returns JSON content from request, calls next function
        try:
            parse_content(json.loads(response.content))
        except Exception as e: # catch exceptions
            if DIAG: print(e) # enabled diagnostics
            time.sleep(60) # sleep, failsafe initiated
            init_query(shodan_api_url, query) # start from initial query
    else:
        try:
            init_query(shodan_api_url, query) # start from initial query
        except Exception as e: # catch exceptions
            if DIAG: print(e) # enabled diagnostics
            time.sleep(60) # sleep, failsafe initiated
            init_query(shodan_api_url, query) # start from initial query

def parse_content(response_data):
    hosts = response_data.get("matches")
    if hosts:
        host = random.choice(hosts) # Pick a random host from the list of hosts
        ip_address = host["ip_str"] # Get the IP address of the host
        port = host["port"] # Get the port of the host
        # Get the country and city of the host
        country_name = host.get("location", {}).get("country_name", "Unknown country")
        city_name = host.get("location", {}).get("city", "Unknown city")
        # Get the image URL from the host
        image_url = "https://www.shodan.io/host/{}/image".format(ip_address)
        # Format the message for Discord
        message = "Here's a Shodan image of {}:{} in {}, {}: {}".format(ip_address, port, city_name, country_name, image_url)
        try:
            discord_sender(message) # send msg to discord
        except Exception as e: # catch exceptions
            if DIAG: print(e) # enabled diagnostics
            time.sleep(60) # sleep, failsafe initiated
            try:
                discord_sender(message) # send msg to discord
            except Exception as e: # catch exceptions
                if DIAG: print(e) # enabled diagnostics
                time.sleep(60) # sleep, failsafe initiated
                init_query(shodan_api_url, query) # start from initial query
    else:
        init_query(shodan_api_url, query) # start from initial query

def discord_sender(message):
        print("Sending message to Discord: {}".format(message))
        # Send the message to the Discord webhook
        result_count = 0
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=1000)
            if response.status_code == 204: # continue if 204 on POST
                # Increment the result count if the message was sent successfully
                result_count += 1
                print("Message sent successfully. Total results returned: {}".format(result_count))
                # Wait for an hour before searching for the next image
                print("sleeping 8 hours")
                time.sleep(60 * 60 * 8) # Sleep for 8 hours
                init_query(shodan_api_url, query) # start from initial query
            else:
                # Wait for a few seconds if no hosts were found
                print("Message was UNSUCCESSFUL'{}'. Waiting...".format(timeout))
                time.sleep(60) # sleep, failsafe initiated
                discord_sender(message) # send msg to discord
        except Exception as e: # catch exceptions
            if DIAG: print(e) # enabled diagnostics
            time.sleep(60) # sleep, failsafe initiated
            try:
                discord_sender(message) # send msg to discord
            except Exception as e: # catch exceptions
                if DIAG: print(e) # enabled diagnostics
                time.sleep(60) # sleep, failsafe initiated
                init_query(shodan_api_url, query) # start from initial query

while True:
    init_query(shodan_api_url, query)
