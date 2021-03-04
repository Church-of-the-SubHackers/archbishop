import asyncio
import re
import os
import os.path
import feedparser
import sqlite3
import time

import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta

from helpers.config import Config


class Feeder(commands.Cog):
    """
    RSS feed parsing script to check subhacker forums and announce about new posts
    """

    dbConn = None
    DB_NAME = "feeder.db"
    ignoreUsers = []
    channels = []
    
    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        Config().load_config()
        self.ignoreUsers = Config().get("FEEDER_IGNORE_USERS").lower().split(",")


    @commands.Cog.listener()
    async def on_ready(self):
        # check if config and quit if not set up
        if (not self.isConfigValid()):
            print("Feeder config is invalid. Not loaded.")
            return
        for channelStr in Config().get("FEEDER_CHANNELS").split(","):
            chan = discord.utils.get(self.bot.guilds[0].channels, name=channelStr)
            if (chan is not None):
                self.channels.append(chan)
        self.prepDb()
        await self.run(True)
    
    def isConfigValid(self):
        return (
            (Config().get("FEEDER_CHECK_FREQ").strip() != "") and
            (Config().get("FEEDER_FEED_URL").strip() != "") and
            (Config().get("FEEDER_CHANNELS").strip() != "")
        )
    
    def prepDb(self):
        # delete the db file and start fresh
        if (os.path.isfile(self.DB_NAME)):
            os.remove(self.DB_NAME)
        self.dbConn = sqlite3.connect(self.DB_NAME)
        self.dbConn.text_factory = str
        self.dbConn.cursor().execute("CREATE TABLE feeds (feed_id text, time text, parsed_feed text, sent integer)")
        self.dbConn.commit()
    
    def feedExistsInDb(self, id):
        return (
            self.dbConn.cursor().execute(
                "SELECT * FROM feeds WHERE feed_id = ?", (id,)
            ).fetchone() is not None
        )
    
    def insertIntoDb(self, data):
        self.dbConn.cursor().execute(
            "INSERT INTO feeds VALUES (?, ?, ?, ?)", (data["feed_id"], data["time"], data["parsed_feed"], data["sent"])
        )
        self.dbConn.commit()
    
    def getForumFeeds(self, isFirstRun):
        feeds = feedparser.parse(Config().get("FEEDER_FEED_URL"))
        feedData = {}
        for entry in feeds.entries:
            cleanTitle = re.sub(u".+\u2022\s", "", entry.title)
            if (not cleanTitle.startswith("Re:")):
                if ((entry.author.lower() not in self.ignoreUsers) and (not self.feedExistsInDb(entry.id))):
                    feedData["feed_id"] = entry.id
                    feedData["time"] = int(datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%S").timestamp())
                    parsed_feed = "Heads up! _{author}_ posted something on the forums:\n**{title}**\n{url}".format(
                        author=entry.author, title=cleanTitle, url=entry.link
                    )
                    feedData["parsed_feed"] = parsed_feed
                    feedData["sent"] = isFirstRun
                    self.insertIntoDb(feedData)
    
    async def sendFeed(self):
        # we print one feed at a time so that we don't spam the channel
        feed = self.dbConn.cursor().execute("SELECT * FROM feeds WHERE sent = 0 ORDER BY time ASC").fetchone()
        if (feed is not None):
            for channel in self.channels:
                await channel.send(feed[2])
            self.dbConn.cursor().execute("UPDATE feeds SET sent = 1 WHERE feed_id = ?", (feed[0],))
            self.dbConn.commit()
    
    def cleanDb(self):
        rmPeriod = int(time.time() - timedelta(days=3).total_seconds())
        self.dbConn.cursor().execute("DELETE FROM feeds WHERE sent = 1 AND time <= ?", (rmPeriod,))
        self.dbConn.commit()
    
    async def run(self, isFirstRun):
        while (True):
            self.cleanDb()
            self.getForumFeeds(isFirstRun)
            await self.sendFeed()
            isFirstRun = False
            # print("ran, sleeping")
            await asyncio.sleep(int(Config().get("FEEDER_CHECK_FREQ"))*60)

def setup(bot):
    bot.add_cog(Feeder(bot))
