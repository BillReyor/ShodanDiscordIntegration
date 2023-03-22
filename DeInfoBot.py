import discord
import shodan
import json
from discord.ext import commands

class ShodanSearchBot(discord.Client):
    def __init__(self, shodan_api_key):
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)
        self.api = shodan.Shodan(shodan_api_key)
        self.history = []

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("!search"):
            query = message.content[7:].strip()

            try:
                results = self.api.search(query)

                # Save results to history
                self.history.append(results["matches"])

                # Send response to Discord channel
                response = f"Showing {len(results['matches'])} results for '{query}':\n\n"
                for match in results["matches"]:
                    response += f"{match['ip_str']}:{match['port']}\n"

                await message.channel.send(response)

            except shodan.APIError as e:
                await message.channel.send(f"Error: {e}")

        elif message.content.startswith("!history"):
            try:
                num_results = int(message.content[9:].strip())
            except ValueError:
                await message.channel.send("Invalid number specified")

            # Ensure num_results is within the bounds of the history list
            num_results = min(num_results, len(self.history))

            # Construct response
            response = f"Showing last {num_results} search results:\n\n"
            for matches in self.history[-num_results:]:
                for match in matches:
                    response += f"{match['ip_str']}:{match['port']}\n"
                response += "\n"

            await message.channel.send(response)

            
# Insert your Shodan API key here
SHODAN_API_KEY = "YOUR_SHODAN_API_KEY"

# Insert your discord token here
DISCORD_TOKEN = "YOUR_DISCORD_TOKEN_HERE"

bot = ShodanSearchBot(SHODAN_API_KEY)
bot.run(DISCORD_TOKEN)
