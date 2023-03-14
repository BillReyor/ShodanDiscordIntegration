import requests
import random
import time
import json

# Shodan API key
SHODAN_API_KEY = ""

# Discord webhook URL
DISCORD_WEBHOOK_URL = ""

# Set up the Shodan API with a query parameter
query = "has_screenshot:true country:\"RU\""
shodan_api_url = "https://api.shodan.io/shodan/host/search?key={}&query={}".format(SHODAN_API_KEY, query)

# Set up a counter to keep track of the number of results returned
result_count = 0

# Loop until we have returned two results
while True:
    print("Searching for hosts with keyword '{}'...".format(query))
    # Send a search request to the Shodan API, added timeout
    response = requests.get(shodan_api_url, timeout=1000)
    if response.status_code == 200:
        # Parse the response JSON to get the list of hosts
        response_json = json.loads(response.content)
        hosts = response_json.get("matches")
        if hosts:
            # Pick a random host from the list of hosts
            host = random.choice(hosts)
            # Get the IP address of the host
            ip_address = host["ip_str"]
            # Get the port of the host
            port = host["port"]
            # Get the country and city of the host
            country_name = host.get("location", {}).get("country_name", "Unknown country")
            city_name = host.get("location", {}).get("city", "Unknown city")
            # Get the image URL from the host
            image_url = "https://www.shodan.io/host/{}/image".format(ip_address)
            # Format the message for Discord
            message = "Here's a Shodan image of {}:{} in {}, {}: {}".format(ip_address, port, city_name, country_name, image_url)
            print("Sending message to Discord: {}".format(message))
            # Send the message to the Discord webhook, added timeout
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=1000)
            if response.status_code == 204:
                # Increment the result count if the message was sent successfully
                result_count += 1
                print("Message sent successfully. Total results returned: {}".format(result_count))
                # Wait for an hour before searching for the next image
                time.sleep(60 * 60 * 8)# created an 8 hour wait - under 100 credits monthly
        else:
            # Wait for a few seconds if no hosts were found
            print("No hosts found with keyword '{}'. Waiting...".format(query))
            time.sleep(5)
    else:
        # Wait for a few seconds if there was an error with the Shodan API
        print("Error searching for hosts with keyword '{}'. Status code: {}. Waiting...".format(query, response.status_code))
        time.sleep(5)
