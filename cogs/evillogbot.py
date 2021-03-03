import asyncio
import time
import sqlite3
import re
import emoji
import html
import sys
import traceback

import discord
from discord.ext import commands

from helpers.config import Config
from datetime import timedelta
from sys import argv

#======================================================================
class EvilLogBot(commands.Cog):
    """
    A bot that logs chat messages in a channel to a SQLite DB
    and exports them for PISG processing.
    Ported from a script by Kulverstukas. More info:
    http://9v.lt/blog/evillogbot-python-irc-channel-logger/
    """

    dbManager = None
    ignoredNicks = []
    threadStarted = False
    configValid = False

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot
        Config().load_config()
        # check if config and quit if not set up
        self.configValid = self.isConfigValid()
        if (not self.configValid):
            print("EvilLogBot config is invalid. Not loaded.")
            return
        self.ignoredNicks = Config().get("ELB_IGNORE_NICKS").lower().split(",")
        self.dbManager = DB_module()
        self.dbManager.prepareDb()

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        """on_message executes whenever a message is posted"""
        if (not self.configValid): return
        if (not self.threadStarted):
            self.threadStarted = True
            await self.exportLog()
        # check if the message we got was from the channel we are logging and if it's not a system msg
        if ((message.channel.name == Config().get("ELB_CHANNEL")) and (not message.is_system())):
            # skip gifs
            if ("tenor.com" in message.content): return
            # get rid of all emojis
            msg = self.stripEmoji(message.content).strip()
            if ((len(msg) >= int(Config().get("ELB_MIN_MSG_LEN"))) and (message.author.name.lower() not in self.ignoredNicks)):
                # print("%s %s %s" % (int(message.created_at.timestamp()), message.author.name, msg))
                self.dbManager.insertLog(int(message.created_at.timestamp()), message.author.name, msg)
    
    def stripEmoji(self, text):
        return re.sub(emoji.get_emoji_regexp(), r"", text)
    
    def isConfigValid(self):
        return (
            (Config().get("ELB_DB_NAME").strip() != "") and
            (Config().get("ELB_LOG_TABLE_NAME").strip() != "") and
            (Config().get("ELB_CHANNEL").strip() != "") and
            (Config().get("ELB_LOG_NAME").strip() != "") and
            (Config().get("ELB_LOG_AGE").strip() != "") and
            (Config().get("ELB_IGNORE_NICKS").strip() != "") and
            (Config().get("ELB_MIN_MSG_LEN").strip() != "") and
            (Config().get("ELB_EXPORT_LOG_TIME").strip() != "")
        )
    
    async def exportLog(self):
        self.dbManager.cleanDb(Config().get("ELB_LOG_AGE"))
        logs = self.dbManager.getLogs(Config().get("ELB_LOG_AGE"))
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        with open(Config().get("ELB_LOG_NAME"), "w") as f:
            for row in logs:
                rowLines = row[2].split("\n")
                for line in rowLines:
                    try:
                        t = time.strftime("%a %d %b %H:%M:%S", time.gmtime(float(row[0])))
                        stripped = html.escape(tag_re.sub("", line).strip())
                        f.write("[%s] <%s> %s\n" % (t, row[1], stripped))
                    except:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        with open("parse_errors.txt", "a") as g:
                            g.write(''.join(line for line in lines))
                            g.write("\r\n")
                        continue
        secsToSleep = (int(Config().get("ELB_EXPORT_LOG_TIME"))*60)*60
        await asyncio.sleep(secsToSleep)
        self.threadStarted = False
    
#======================================================================
class DB_module():
    
    dbConn = None
    configs = {
        "db_name": "",
        "log_table_name": ""
    }
    
    def __init__(self):
        self.configs["db_name"] = Config().get("ELB_DB_NAME")
        self.configs["log_table_name"] = Config().get("ELB_LOG_TABLE_NAME")
    
    ''' Prepares the database for usage and returns a connection object '''
    def prepareDb(self):
        if (self.dbConn == None):
            self.dbConn = sqlite3.connect(self.configs["db_name"])
            self.dbConn.text_factory = str
            self.dbConn.cursor().execute("CREATE TABLE IF NOT EXISTS {0} (time text, nickname text, log text)".format(self.configs["log_table_name"]))
            self.dbConn.commit()
        return self.dbConn
    
    ''' Inserts given text into the database '''
    def insertLog(self, time, nickname, text):
        self.dbConn.cursor().execute("INSERT INTO {0} VALUES (?, ?, ?)".format(self.configs["log_table_name"]), (time, nickname, text))
        self.dbConn.commit()
    
    '''
        Function that removes rows that are older than
        defined number of days - 1 (justin case).
        This is some serious logrotate shit bruh.
    '''
    def cleanDb(self, logAge):
        rmPeriod = int(time.time() - timedelta(days=(int(logAge)+1)).total_seconds())
        self.dbConn.cursor().execute("DELETE FROM {0} WHERE time <= ?".format(self.configs["log_table_name"]), (rmPeriod,))
        self.dbConn.commit()

    def getLogs(self, logAge):
        logPeriod = int(time.time() - timedelta(days=int(logAge)).total_seconds())
        return self.dbConn.cursor().execute("SELECT * FROM {0} WHERE time > ?".format(self.configs["log_table_name"]), (str(logPeriod),)).fetchall()
        
#======================================================================

def setup(bot):
    bot.add_cog(EvilLogBot(bot))