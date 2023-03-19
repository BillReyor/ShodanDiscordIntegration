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

1.  Clone this repository or download the `DiscoDan.py` file.
2.  Install the `requests` module by running `pip install requests`.
3.  Install the `nested-lookup` module by running `pip install nested-lookup`.

Configuration
-------------

1.  Open the `discodan.py' file in a text editor.
2.  Replace `YOUR_SHODAN_API_KEY` with your Shodan API key.
3.  Replace `YOUR_DISCORD_WEBHOOK_URL` with your Discord webhook URL.
4.  Modify the `QUERY` parameter to customize your search query.
5.  Modify the `VERBOSE` parameter to display helpful dignostic information.

Usage
-----

1.  Run the script by running `python3 Discodan.py` in a terminal.
2.  The bot will search for a host with a screenshot in the country specified by the `QUERY` parameter.
3.  The bot will send a random msg containing a link to the Discord webhook (adjust the timing) per hour
4.  The msgs will contain: host's IP address, city, and country and a link to the Shodan hosted image(s).
5.  App will ensure that no duplicate request are sent to the channle
6.  App will proceed to exhaust the contents gathered from the quesy until finished
7.  Next steps ?
