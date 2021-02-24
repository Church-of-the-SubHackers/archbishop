import asyncio
import re

import discord
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
        if (message.content.startswith("!ud")):
            msgParts = message.content.split(" ", 1)
            if (len(msgParts) > 1):
                await self.lookupAndSend(message.channel, msgParts[1].strip())

    async def lookupAndSend(self, channel, usrInput):
        defs = self.uClient.get_definition(usrInput)
        if (len(defs) > 0):
            singleDef = None
            for d in defs:
                # pick an object that has less than N symbols in text
                if ((len(d.definition) <= 200) and (len(d.example) <= 200)):
                    singleDef = d
                    break
            if (singleDef is not None):
                singleDef.definition = re.sub("[\[\]]", "", singleDef.definition)
                singleDef.example = re.sub("[\[\]]", "", singleDef.example)
                singleDef.example = re.sub("\n+", "\n> ", singleDef.example)
                await channel.send(
                    "**{word}**:\n{definition}\n> {example}\n\n:arrow_up:: {upvotes}  :arrow_down:: {downvotes}"
                    .format(
                        word=singleDef.word, definition=singleDef.definition, example=singleDef.example,
                        upvotes=singleDef.upvotes, downvotes=singleDef.downvotes
                    )
                )
            else:
                await channel.send("No definition found for **%s**" % (usrInput,))
        else:
            await channel.send("No definition found for **%s**" % (usrInput,))

def setup(bot):
    bot.add_cog(UrbanDicto(bot))
