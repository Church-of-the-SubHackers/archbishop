import sys

import discord
from discord.ext import commands


class Util(commands.Cog):
    """
    Implements utility functions

    """

    def __init__(self, bot):
        """
        Cog initialization

        Args:
            bot (discord.ext.commands.Bot): Instance of the bot

        """
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        """on_ready executes once the bot has connected to Discord"""
        print(f"{self.bot.user.name} has connected to Discord!")

    # Commands
    @commands.command(
        brief="Tests bot's connection to server",
        description="Bot will respond with \"Pong!\" if connected"
    )
    async def ping(self, ctx):
        await ctx.send("Pong!")

    """
    Loads a cog extension

    Sends a message announcing loading of extension

    Args:
        ctx (discord.ext.commands.Context): The context of the Discord bot the
        command was executed under.
        extension (str): The cog extension to load

    Raises:
        ExtensionNotLoaded: If cog cannot be loaded
        ExtensionAlreadyLoaded: If Cog already Loaded 


    Returns:
        None

    """

    @commands.command(
        brief="Loads an extension",
        description="Loads an extension. Admins only"
    )
    @commands.has_role("Admin")
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(f"cogs.{extension}")
        except discord.ext.commands.errors.ExtensionNotFound as err_load:
            await ctx.send(
                f"{err_load} "
                f"Ensure cog exists."
            )
            pass
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await ctx.send(
                f"Cog Already Loaded."
            )
            pass
        else:
            await ctx.send(f"{extension} loaded")

    """
    Reloads a cog extension

    Sends a message announcing reloading of extension

    Args:
        ctx (discord.ext.commands.Context): The context of the Discord bot the
        command was executed under.
        extension (str): The cog extension to reload

    Raises:
        ExtensionNotLoaded: If cog cannot be reloaded

    Returns:
        None

    """

    @commands.command(
        brief="Reloads an extension",
        description="Reloads an extension. Admins only"
    )
    @commands.has_role("Admin")
    async def reload(self, ctx, extension):
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except discord.ext.commands.errors.ExtensionNotLoaded as err_reload:
            await ctx.send(
                f"Failed to reload `{extension}` "
                f"{err_reload}"
            )
            pass
        else:
            await ctx.send(f"{extension} reloaded")

    """
    Unloads a cog extension

    Sends a message announcing unloading of extension

    Args:
        ctx (discord.ext.commands.Context): The context of the Discord bot the
        command was executed under.
        extension (str): The cog extension to unload

    Raises:
        ExtensionNotLoaded: If cog cannot be unloaded

    Returns:
        None

    """

    @commands.command(
        brief="Unloads an extension",
        description="Unloads an extension. Admins only"
    )
    @commands.has_role("Admin")
    async def unload(self, ctx, extension):
        if extension != "util":
            try:
                self.bot.unload_extension(f"cogs.{extension}")
            except discord.ext.commands.errors.ExtensionNotLoaded as err_unload:
                await ctx.send(
                    f"Failed to unload `{extension}` "
                    f"{err_unload}"
                )
                pass
            except BaseException:
                e = sys.exc_info()[0]
                print(e)
                pass
            else:
                await ctx.send(f"{extension} unloaded")
        else:
            await ctx.send("Cannot unload `util`")


def setup(bot):
    bot.add_cog(Util(bot))
