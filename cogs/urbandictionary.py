import re

from discord.ext import commands

from helpers.config import Config
from udpy import UrbanClient


class UrbanDicto(commands.Cog):
    """
    Urban dictionary lookup script. Use with command !ud <word or phrase>
    """

    uClient = None

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        Config().load_config()
        self.uClient = UrbanClient()

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """on_message executes whenever a message is posted"""
        if message.content.startswith("!ud"):
            msg_parts = message.content.split(" ", 1)
            if len(msg_parts) > 1:
                await self.lookup_and_send(message.channel, msg_parts[1].strip())

    async def lookup_and_send(self, channel, usr_input):
        defs = self.uClient.get_definition(usr_input)
        if len(defs) > 0:
            single_def = None
            for d in defs:
                # pick an object that has less than N symbols in text
                if (len(d.definition) <= 300) and (len(d.example) <= 300):
                    single_def = d
                    break
            if single_def is not None:
                single_def.definition = single_def.definition.strip()
                single_def.definition = re.sub("[\[\]]", "", single_def.definition)
                single_def.example = single_def.example.strip()
                single_def.example = re.sub("[\[\]]", "", single_def.example)
                single_def.example = re.sub("\r\n", "\n", single_def.example)
                single_def.example = re.sub("\n+", "\n> ", single_def.example)
                if single_def.example != "":
                    await channel.send(
                        f"**{single_def.word}**:\n{single_def.definition}\n> {single_def.example}\n\n"
                        f":arrow_up:: {single_def.upvotes}  :arrow_down:: {single_def.downvotes}"
                    )
                else:
                    await channel.send(
                        f"**{single_def.word}**:\n{single_def.definition}\n\n:arrow_up:: {single_def.upvotes}"
                        f"  :arrow_down:: {single_def.downvotes}"
                    )
            else:
                await channel.send("No definition found for **%s**" % (usr_input,))
        else:
            await channel.send("No definition found for **%s**" % (usr_input,))


def setup(bot):
    bot.add_cog(UrbanDicto(bot))
