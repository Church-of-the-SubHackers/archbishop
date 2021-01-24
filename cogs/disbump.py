import asyncio

import discord
from discord.ext import commands

from helpers.config import Config


class Disbump(commands.Cog):
    """
    Implements a smart notifier for Disboard bumping

    """

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        self.is_waiting = False
        self.bumper_role = discord.guild.Role
        Config().load_config()

        # reminder_channel gets calculated on init to save time later
        self.reminder_channel = discord.channel.TextChannel

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """on_message executes whenever a message is posted"""
        if (message.content == "!d bump"
                and message.channel.name == Config().get("DISBUMP_CHANNEL")):
            # Set our reminder channel and bumper role attributes for use later
            #
            # There is probably a much more elegant solution to this
            self.reminder_channel = message.channel
            for r in message.channel.guild.roles:
                if r.name == Config().get("DISBUMP_ROLE"):
                    self.bumper_role = r

            if self.is_waiting is not True:
                self.is_waiting = True
                await self.remind()

    async def remind(self):
        # Sleep for 7200 seconds (2 hours) then remind bumpers
        await asyncio.sleep(7200)

        bumper_role = self.bumper_role
        await self.reminder_channel.send(
            f"It's that time again "
            f"{bumper_role.mention} "
            f"`!d bump` the server for ultimate justice!"
        )
        self.is_waiting = False


def setup(bot):
    bot.add_cog(Disbump(bot))
