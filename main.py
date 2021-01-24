# main.py
# ArchBishop - A basic Discord bot skeleton intended to act as a host for
# Cogs developed for the Church of the Subhackers discord community
#
# 2020 Church of the Subhackers
import os
import sys

import discord

from discord.ext import commands
from discord.ext.tasks import loop
from helpers.config import Config


# Load our tokens
Config().load_config()

intents = discord.Intents.default()
intents.members = True

# Grab discord bot token from dotenv
token = Config().get("BOT_TOKEN")

bot = commands.Bot(command_prefix='~', intents=intents)

# Load all cogs during startup
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        # Using splicing to remove `.py` from filename
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(token)
