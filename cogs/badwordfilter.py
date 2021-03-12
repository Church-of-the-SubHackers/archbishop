from discord.ext import commands

from helpers.config import Config


class BadWordFilter(commands.Cog):
    """

    Deletes The bad words from chat

    """

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        self.bad_words = Config().get("BAD_WORDS").split(",")
        self.ignore_chans = Config().get("IGNORE_CHANNELS").split(",")
        Config().load_config()

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """on_message executes whenever a message is posted"""
        if not self.ignore_chans.__contains__(message.channel.name):
            words = message.content.split()
            for word in words:
                if self.bad_words.__contains__(word.lower()):
                    await message.delete()


def setup(bot):
    bot.add_cog(BadWordFilter(bot))
