import wikipediaapi

from discord.ext import commands

from helpers.config import Config


class Wikipedia(commands.Cog):
    """
    Wikipedia lookup script. Use with command !wiki <word or phrase>
    """

    wClient = None

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        Config().load_config()
        self.wClient = wikipediaapi.Wikipedia('en')

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """on_message executes whenever a message is posted"""
        if message.content.startswith("!wiki"):
            msg_parts = message.content.split(" ", 1)
            if len(msg_parts) > 1:
                await self.lookup_and_send(message.channel, msg_parts[1].strip())

    async def lookup_and_send(self, channel, usr_input):
        page = self.wClient.page(usr_input.strip())
        if page.exists():
            summary = page.summary[:1000]
            if len(page.summary) > 1000: summary += "..."
            await channel.send(
                "**{usrinput}**:\n{summary}\n{url}".format(usrinput=page.title, summary=summary, url=page.fullurl)
            )
        else:
            await channel.send("No pages found for **%s**" % (usr_input,))


def setup(bot):
    bot.add_cog(Wikipedia(bot))
