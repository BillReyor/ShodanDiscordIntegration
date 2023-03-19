from nested_lookup import nested_lookup
import shodan
import random
import time
import requests
import logging
import json

# Shodan API key
SHODAN_API_KEY = ""

# Discord webhook URL
DISCORD_WEBHOOK_URL = ""

# The query to send to Shodan
QUERY = "has_screenshot:true ssl:edu"

# Display verbose content from application
VERBOSE = False #True

# Enable logging of error level events
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ShodanQuery:
    def __init__(self, api_key, query, verbose):
        self.api = shodan.Shodan(api_key)
        self.query = query
        self.verbose = verbose
        self.sent_ips = self.load_sent_ips()
        self.history = self.load_history()
        self.today = current_time = time.strftime("%Y-%m-%d", time.gmtime())
        if self.verbose: print("\n[ShodanQuery][INIT] -- ")
        if self.verbose: print("\t[INIT] Shodan API Key: {}".format(api_key))
        if self.verbose: print("\t[INIT] Shodan query: {}".format(query))
        if self.verbose: print("\t[INIT] Application verbosity: {}".format(True))
        if self.verbose: print("\t[INIT] Request History file: {}".format("./history.json"))
        if self.verbose: print("\t[INIT] Current Date: {}".format(self.today))

    def check_date(self):
        if self.verbose: print("\n[ShodanQuery][check_date] -- ")
        if self.today in nested_lookup('date', self.history):
            if self.verbose: print("\t[check_date] Latest daily run being used: {}".format(self.today))
            return True

    def load_history(self):
        if self.verbose: print("\n[ShodanQuery][load_history] -- ")
        try:
            with open('history.json', 'r') as openfile:
                if self.verbose: print("\t[load_history] Loaded history file from disk")
                return json.load(openfile)
        except FileNotFoundError:
            if self.verbose: print("\t[load_history] History file being created on disk: './history.json'")
            self.history = json.load([])
            self.save_history()
            self.load_history()

    def load_sent_ips(self):
        if self.verbose: print("\n[ShodanQuery][load_sent_ips] -- ")
        try:
            with open("sentips.txt", "r") as sentIPfile:
                if self.verbose: print("\t[load_sent_ips] Loading sent IP's file from disk")
                return set(line.strip() for line in sentIPfile.readlines())
        except FileNotFoundError:
            if self.verbose: print("\t[load_sent_ips] Load Sent IP List from disk failed at reading")
            return set()

    def save_history(self):
        if self.verbose: print("\n[ShodanQuery][save_history] -- ")
        try:
            with open("history.json", "w") as historyFile:
                if self.verbose: print("\t[save_history] Saving history data to disk")
                json.dump(self.history, historyFile)
        except Exception as e:
            if self.verbose: print("\t[save_history] Failed to write history.json file.\nPlease check permissions of filesystem or user")
            pass

    def save_sent_ip(self, ip_address):
        if self.verbose: print("\n[ShodanQuery][save_sent_ip] -- ")
        try:
            with open("sentips.txt", "a") as sentIPfile:
               if self.verbose: print("\t[save_sent_ip] Saving Sent IP Address list to disk")
               sentIPfile.write(ip_address + "\n")
            self.sent_ips.add(ip_address)
        except Exception as e:
           if self.verbose: print("\t[save_sent_ip] Failed to save Discord Messages log for {}").format(ip_address)
           pass

    def search_history(self):
        if self.verbose: print("\n[ShodanQuery][search_history] -- ")
        try:
            if nested_lookup("host", self.history):
                if self.verbose: print("\t[search_history] This host was already recorded")
                pass
        except Exception as e:
           if self.verbose: print("\t[search_history] Failed to process nested list dictionaries\n:Recommended: 'pip3 install nested-lookups'")
           return False

    def execute_with_retry(self, func, *args, **kwargs):
        if self.verbose: print("\n[ShodanQuery][execute_with_retry] -- ")
        if self.verbose: print("\t[init_query] Current date was not found in the history file")
        retries = 0
        while True:
            try:
                if self.verbose: print("\t[execute_with_retry] Current execution retry count: {}".format(retries))
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception occurred: {e}")
                logger.error(f"Function: {func.__name__}")
                logger.error(f"Arguments: {args}")
                logger.error(f"Keyword arguments: {kwargs}")
                retries += 1
                time.sleep(60 * retries, 3600)

    def init_query(self):
        if self.verbose: print("\n[ShodanQuery][init_query] -- ")
        if self.verbose: print("\t[init_query] Current date is: {}".format(self.today))
        if not self.check_date():
            if self.verbose: print("\t[init_query] Current date was not found in the history file")
            if self.verbose: print("\t[init_query] Searching for hosts with keyword '{}'...".format(self.query))
            response_data = self.execute_with_retry(self.api.search_cursor, self.query)
            self.parse_content(response_data)
        else:
            if self.verbose: print("\t[init_query] Current date found within the history file, using previous content")
            if self.verbose: print("\t[init_query] Sending request to [random_host]")
            self.random_host()

    def parse_content(self, response_data):
        if self.verbose: print("\n[ShodanQuery][parse_content] -- ")
        if response_data:
            if self.verbose: print("\t[parse_content] Response data being processed")
            for host in response_data:
                ip_address = host["ip_str"]
                if self.verbose: print("\t[parse_content] Processing host: {}".format(ip_address))
                if ip_address not in nested_lookup('host', self.history):
                    current_time = time.strftime("%Y-%m-%d", time.gmtime())
                    if self.verbose: print("\t[parse_content] Host '{}' was not found in the history file".format(ip_address))
                    port = host["port"]
                    country_name = host.get("location", {}).get("country_name", "Unknown country")
                    city_name = host.get("location", {}).get("city", "Unknown city")
                    image_url = "https://www.shodan.io/host/{}/image".format(ip_address)
                    self.history.append({'host':ip_address, 'port':port, 'city': city_name, 'country':country_name, 'url':image_url, 'date': current_time})
                    if self.verbose: print("\t[parse_content] Building history entry {}:{} in {}, {}: {}".format(ip_address, port, city_name, country_name, image_url))
                else:
                    if self.verbose: print("\t[parse_content] Host {} already been processed: skipping".format(ip_address))
                    continue
        else:
            if self.verbose: print("\t[parse_content] Unable to parse request, restarting from [init_query]")
            self.init_query()
        if self.verbose: print("\t[parse_content] Saving history file to disk")
        self.save_history()
        if self.verbose: print("\t[parse_content] Loading recently saved history file to to memory")
        self.history = self.load_history()
        if self.verbose: print("\t[parse_content] Selecting random host from known targets")
        self.random_host()

    def host_information(self, hostIPAddress):
        return self.api.host(hostIPAddress)

    def random_host(self):
        if self.verbose: print("\n[ShodanQuery][random_host] -- ")
        history_len = len(self.history)
        if self.verbose: print("\t[random_host] Length of known host is: {}".format(history_len))
        choice = random.randint(0,history_len)
        if self.verbose: print("\t[random_host] Random number selcted is: {}".format(choice))
        random_pick = self.history[choice]
        if self.verbose: print("\t[random_host] Random host from list selected: {}".format(random_pick['host']))
        if random_pick['host'] not in self.sent_ips:
            if self.verbose: print("\t[random_host] Host has not been seen at discord before, generating new msg")
            message = "Here's a Shodan image of {}:{} in {}, {}: {}".format(random_pick['host'],random_pick['port'],random_pick['city'],random_pick['country'],random_pick['url'])
            if self.verbose: print("\t[random_host] MSG being sent onto [DiscordWebhookSender]")
            self.save_sent_ip(random_pick['host'])
            self.sent_ips = self.load_sent_ips()
            DiscordWebhookSender.send_message(message, self.verbose)
        else:
            if self.verbose: print("\t[random_host] Host choice attempting again due to previous sent msg 'duplication'.")
            self.random_host()

class DiscordWebhookSender:
    @staticmethod
    def send_message(message, verbose):
        if verbose: print("\n[DiscordWebhookSender] --\n\t[send_message] Sending message to Discord channle:")
        if verbose: print("\t\t[raw_data]: {}".format(message))
        response = shodan_query.execute_with_retry(requests.post, DISCORD_WEBHOOK_URL, json={"content": message}, timeout=1000)
        if response.status_code == 204:
            if verbose: print("\t[send_message] Message sent successfully.")
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            if verbose: print("\t[send_message] Timestamp: {}".format(current_time))
            if verbose: print("\t[send_message] Sleeping for '60' seconds")
            time.sleep(60)
            shodan_query.init_query()
        else:
            if verbose: print("\t[send_message] Message was UNSUCCESSFUL, waiting 60 seconds, attempting again")
            time.sleep(60)
            if verbose: print("\t[send_message] Attempting to resend message to Discord")
            DiscordWebhookSender.send_message(message)

if __name__ == "__main__":
    shodan_query = ShodanQuery(SHODAN_API_KEY, QUERY, VERBOSE)
    while True:
        shodan_query.init_query()
