import shodan
import random
import time
import requests
import logging

SHODAN_API_KEY = ""
DISCORD_WEBHOOK_URL = ""
query = "has_screenshot:true ssl:edu"

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ShodanQuery:
    def __init__(self, api_key, query):
        self.api = shodan.Shodan(api_key)
        self.query = query
        self.sent_ips = self.load_sent_ips()

    def load_sent_ips(self):
        try:
            with open("sentips.txt", "r") as f:
                return set(line.strip() for line in f.readlines())
        except FileNotFoundError:
            return set()

    def save_sent_ip(self, ip_address):
        with open("sentips.txt", "a") as f:
            f.write(ip_address + "\n")
        self.sent_ips.add(ip_address)

    def execute_with_retry(self, func, *args, **kwargs):
        retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception occurred: {e}")
                logger.error(f"Function: {func.__name__}")
                logger.error(f"Arguments: {args}")
                logger.error(f"Keyword arguments: {kwargs}")
                time.sleep(60)
                retries += 1
                time.sleep(min(60 * retries, 3600))
                
    def init_query(self):
        print("Searching for hosts with keyword '{}'...".format(self.query))
        response_data = self.execute_with_retry(self.api.search, self.query)
        self.parse_content(response_data)

    def parse_content(self, response_data):
        hosts = response_data.get("matches")

        if hosts:
            while True:
                host = random.choice(hosts)
                ip_address = host["ip_str"]
                if ip_address not in self.sent_ips:
                    break

            self.save_sent_ip(ip_address)
            port = host["port"]
            country_name = host.get("location", {}).get("country_name", "Unknown country")
            city_name = host.get("location", {}).get("city", "Unknown city")
            image_url = "https://www.shodan.io/host/{}/image".format(ip_address)
            message = "Here's a Shodan image of {}:{} in {}, {}: {}".format(ip_address, port, city_name, country_name, image_url)
            DiscordWebhookSender.send_message(message)
        else:
            self.init_query()

class DiscordWebhookSender:
    @staticmethod
    def send_message(message):
        print("Sending message to Discord: {}".format(message))
        response = shodan_query.execute_with_retry(requests.post, DISCORD_WEBHOOK_URL, json={"content": message}, timeout=1000)

        if response.status_code == 204:
            print("Message sent successfully.")
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print("Timestamp: {}".format(current_time))
            print("Sleeping 8 hours")
            time.sleep(60 * 60 * 8)
            shodan_query.init_query()
        else:
            print("Message was UNSUCCESSFUL. Waiting...")
            time.sleep(60)
            DiscordWebhookSender.send_message(message)

if __name__ == "__main__":
    shodan_query = ShodanQuery(SHODAN_API_KEY, query)
    while True:
        shodan_query.init_query()
