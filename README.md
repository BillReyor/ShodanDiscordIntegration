Shodan Discord Bot
==================

This is a Python script that uses the Shodan API to search for hosts with screenshots in a specific country, and sends a random screenshot to a Discord webhook once per hour.

Prerequisites
-------------

-   Python 3.6 or later
-   A Shodan API key
-   A Discord webhook URL

Installation
------------

1.  Clone this repository or download the 'shodan.py' file.
2.  Install the `requests` module by running `pip install requests`.

Configuration
-------------

1.  Open the `shodan.py' file in a text editor.
2.  Replace `YOUR_SHODAN_API_KEY` with your Shodan API key.
3.  Replace `YOUR_DISCORD_WEBHOOK_URL` with your Discord webhook URL.
4.  Modify the `query` parameter to customize your search query.

Usage
-----

1.  Run the script by running `shodan.py` in a terminal.
2.  The bot will search for a host with a screenshot in the country specified by the `query` parameter.
3.  The bot will send a random screenshot to the Discord webhook once per hour, along with the host's IP address, city, and country.
