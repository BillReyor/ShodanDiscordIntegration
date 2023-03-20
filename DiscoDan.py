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
        self.verbose = verbose
        self.today = time.strftime("%Y-%m-%d", time.gmtime())
        if self.verbose: print("\n[Initialization] -- ")
        self.api = shodan.Shodan(api_key)
        self.query = query
        self.queryhash = hashlib.md5(self.query.encode('utf-8')).hexdigest()
        self.sent_ips = self.load_sent_ips()
        self.history = self.load_history()
        if self.verbose: print("\t[INIT] Shodan API Key: {}".format(api_key))
        if self.verbose: print("\t[INIT] Shodan query: {}".format(query))
        if self.verbose: print("\t[INIT] Application verbosity: {}".format(True))
        if self.verbose: print("\t[INIT] Request History file: {}".format("./history.json"))
        if self.verbose: print("\t[INIT] Current Day: {}".format(self.today))

    def live_edit_query(self, new_query):
        if self.verbose: fun="live_edit_query"
        detailed_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        if self.verbose: print("\t[{}] Query modified to: {} on: {}".format(fun,detailed_time))
        self.query = new_query
        self.init_query()

    def check_date(self):
        if self.verbose: fun="check_date"
        if self.today not in nested_lookup('date', self.history[self.queryhash]):
            if self.verbose: print("\t[{}] Latest daily run being used: {}".format(fun,self.today))
            return False
        else:
            return True

    def load_history(self):
        if self.verbose: fun="load_history"
        try:
            with open('history.json', 'r') as openfile:
                if self.verbose: print("\t[{}] Loaded history file from disk".format(fun))
                return json.load(openfile)
        except FileNotFoundError:
            if self.verbose: print("\t[{}] History file being created on disk: './history.json'".format(fun))
            self.history = {}
            if self.queryhash not in self.history.keys():
                self.history[self.queryhash] = []
                self.history[self.queryhash].append({'query': self.query})
            self.save_history()
            self.load_history()

    def load_sent_ips(self):
        if self.verbose: fun="load_sent_ips"
        try:
            with open("sentips.txt", "r") as sentIPfile:
                if self.verbose: print("\t[{}] Loading sent IP's file from disk".format(fun))
                return set(line.strip() for line in sentIPfile.readlines())
        except FileNotFoundError:
            if self.verbose: print("\t[{}] Load Sent IP List from disk failed at reading".format(fun))
            return set()

    def save_history(self):
        if self.verbose: fun="save_history"
        try:
            with open("history.json", "w") as historyFile:
                if self.verbose: print("\t[{}] Saving history data to disk".format(fun))
                json.dump(self.history, historyFile)
        except Exception as e:
            if self.verbose: print("\t[{}] Failed to write history.json file.\nPlease check permissions".format(fun))
            pass

    def save_sent_ip(self, ip_address):
        if self.verbose: fun="save_sent_ip"
        try:
            with open("sentips.txt", "a") as sentIPfile:
               if self.verbose: print("\t[{}] Saving Sent IP Address list to disk".format(fun))
               sentIPfile.write(ip_address + "\n")
            self.sent_ips.add(ip_address)
        except Exception as e:
           if self.verbose: print("\t[{}] Failed to save Discord Messages log for {}").format(fun,ip_address)
           pass

    def search_history(self): # future use
        if self.verbose: fun="search_history"
        try:
            if nested_lookup("host", self.history[self.queryhash]):
                if self.verbose: print("\t[{}] This host was already recorded".format(fun))
                pass
        except Exception as e:
           if self.verbose: print("\t[{}] Failed lookup host info\n:Recommended: 'pip3 install nested-lookups'".format(fun))
           return False

    def execute_with_retry(self, func, *args, **kwargs):
        if self.verbose: fun="execute_with_retry"
        retries = 0
        while True:
            try:
                if self.verbose: print("\t[{}] Current execution retry count: {}".format(fun,retries))
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception occurred: {e}")
                logger.error(f"Function: {func.__name__}")
                logger.error(f"Arguments: {args}")
                logger.error(f"Keyword arguments: {kwargs}")
                retries += 1
                time.sleep(60 * retries, 3600)

    def init_query(self):
        if self.verbose: print("\n[ShodanQuery:] -- ")
        if self.verbose: fun="init_query"
        if self.verbose: print("\t[{}] Current date is: {}".format(fun,self.today))
        if not self.check_date():
            if self.verbose: print("\t[{}] Current date was not found in the history file".format(fun))
            if self.verbose: print("\t[{}] Search query keyword used'{}'...".format(fun,self.query))
            response_data = self.execute_with_retry(self.api.search_cursor, self.query)
            self.parse_content(response_data)
        else:
            if self.verbose: print("\t[{}] Using current DB from {} search".format(fun, self.today))
            if self.verbose: print("\t[{}] Sending request to [random_host]".format(fun))
            self.random_host()

    def parse_content(self, response_data):
        if self.verbose: fun="parse_content"
        if response_data:
            if self.verbose: print("\t[{}] Response data being processed".format(fun))
            for host in response_data:
                ip_address = host["ip_str"]
                if self.verbose: print("\t[{}] Processing host: {}".format(fun,ip_address))
                if ip_address not in nested_lookup('host', self.history[self.queryhash]):
                    if self.verbose: print("\t[{}] Host '{}' was not found in the history file".format(fun,ip_address))
                    port = host["port"]
                    country_name = host.get("location", {}).get("country_name", "Unknown country")
                    city_name = host.get("location", {}).get("city", "Unknown city")
                    image_url = "https://www.shodan.io/host/{}/image".format(ip_address)
                    self.history[self.queryhash].append({
                        'host':ip_address,
                        'port':port,
                        'city': city_name,
                        'country':country_name,
                        'url':image_url,
                    })
                    if self.verbose: print("\t[{}] Building history entry {}:{} in {}, {}: {}".format(
                        fun,
                        ip_address,
                        port,
                        city_name,
                        country_name,
                        image_url
                    ))
                else:
                    if self.verbose: print("\t[{}] Host {} already been processed: skipping".format(fun,ip_address))
                    continue
            self.history[self.queryhash].append({'date': self.today})
            if self.verbose: print("\t[{}] Saving history file to disk".format(fun))
            self.save_history()
            if self.verbose: print("\t[{}] Loading recently saved history file to to memory".format(fun))
            self.history = self.load_history()
        else:
            if self.verbose: print("\t[{}] Unable to parse request, restarting from [init_query]".format(fun))
            self.init_query()
        if self.verbose: print("\t[{}] Selecting random host from known targets".format(fun))
        self.random_host()

    def host_information(self, hostIPAddress): # planned for future use
        return self.api.host(hostIPAddress)

    def random_host(self):
        if self.verbose: fun="parse_content"
        history_len = len(self.history[self.queryhash])
        if self.verbose: print("\t[{}] Length of known host is: {}".format(fun,history_len))
        choice = random.randint(2,history_len)
        if self.verbose: print("\t[{}] Random number selcted is: {}".format(fun,choice))
        ranpick = self.history[self.queryhash][choice]
        if self.verbose: print("\t[{}] Random host from list selected: {}".format(fun,ranpick['host']))
        if ranpick['host'] not in self.sent_ips:
            if self.verbose: print("\t[{}] Host has not been seen at discord before, generating new msg".format(fun))
            message = "Here's a Shodan image of {}:{} in {}, {}: {}".format(
                ranpick['host'],
                ranpick['port'],
                ranpick['city'],
                ranpick['country'],
                ranpick['url']
            )
            if self.verbose: print("\t[{}] MSG being sent onto [DiscordWebhookSender]".format(fun))
            self.save_sent_ip(ranpick['host'])
            self.sent_ips = self.load_sent_ips()
            DiscordWebhookSender.send_message(message, self.verbose)
        else:
            if self.verbose: print("\t[{}] Repeat host selection cause: 'duplication'".format(fun))
            self.random_host()

class DiscordWebhookSender:
    @staticmethod
    def send_message(message, verbose):
        if verbose: print("\n[DiscordWebhookSender] --\n\t[send_message] Sending message to Discord channle:")
        if verbose: print("\t\t[raw_data]: {}".format(message))
        response = shodan_query.execute_with_retry(
            requests.post,
            DISCORD_WEBHOOK_URL,
            json={
                "content": message
            },
            timeout=1000
        )
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
            DiscordWebhookSender.send_message(message, verbose)

if __name__ == "__main__":
    shodan_query = ShodanQuery(SHODAN_API_KEY, QUERY, VERBOSE)
    while True:
        shodan_query.init_query()
