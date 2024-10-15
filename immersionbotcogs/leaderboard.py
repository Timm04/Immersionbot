import discord
from discord.ext import commands
from datetime import timedelta
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice
from modals.sql import Store, Set_jp
import modals.helpers as helpers
from modals.constants import _DB_NAME, TIMEFRAMES, tmw_id, _MULTIPLIERS, _JP_DB
import json

class Leaderboard(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(tmw_id)
        
    @app_commands.command(name='leaderboard', description=f'Leaderboard of immersion.')
    @app_commands.choices(media_type = [Choice(name="Visual Novels", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING"), Choice(name="Output", value="OUTPUT")])
    @app_commands.describe(timeframe='''DEFAULT=MONTH; Week, Month, Year, All, [year-month-day] or [year-month-day-year-month-day]''')
    async def leaderboard(self, interaction: discord.Interaction, timeframe: Optional[str], media_type: Optional[str]):

        # channel = interaction.channel
        # if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
        #     return await interaction.response.send_message(content='You can only log in #immersion-log or DMs.', ephemeral=True)
        
        bool, msg = helpers.check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {msg}', ephemeral=True)
        
        if not media_type:
            media_type = None

        if not timeframe or timeframe.upper() == "MONTH":
            #Month
            title = "Monthly"
            beginn = interaction.created_at.replace(day=1, hour=0, minute=0)
            end = (beginn.replace(day=28) + timedelta(days=4)) - timedelta(days=(beginn.replace(day=28) + timedelta(days=4)).day)

        elif timeframe.upper() == "WEEK":
            beginn = (interaction.created_at - timedelta(days=interaction.created_at.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (beginn + timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            title = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
        
        elif timeframe.upper() == "YEAR":
            beginn = interaction.created_at.date().replace(month=1, day=1)
            end = interaction.created_at.date().replace(month=12, day=31)
            title = f"""{beginn.strftime("%Y")}"""
        
        elif timeframe.upper() == "ALL":
            beginn = interaction.created_at.replace(year=2020)
            end = interaction.created_at
            title = f"""All Time"""

        elif timeframe.upper() not in TIMEFRAMES:
            try:
                dates = timeframe.split('-')
                if len(timeframe.split('-')) == 6:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]))
                    end = interaction.created_at.replace(year=int(dates[3]), month=int(dates[4]), day=int(dates[5]))
                    title = f"""{beginn.strftime("{0} %b").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
                    if beginn > end:
                        return await interaction.response.send_message(content='You switched up the dates.', ephemeral=True)
                elif len(timeframe.split('-')) == 3:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]), hour=0, minute=0, second=0)
                    end = beginn + timedelta(days=1)
                    title = f"""{beginn.strftime("{0} %b").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
                    if beginn > interaction.created_at:
                        return await interaction.response.send_message(content='''You can't look into the future.''', ephemeral=True)
                else:
                    return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)
            except Exception:
                return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)

        await interaction.response.defer()
        
        multipliers_path = _MULTIPLIERS
        try:
            with open(multipliers_path, "r") as file:
                MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            MULTIPLIERS = {}
        if media_type != "OUTPUT":
            with Store(_DB_NAME) as store:
                leaderboard = store.get_leaderboard(interaction.user.id, (beginn, end), media_type, MULTIPLIERS)
        else:
            with Set_jp(_JP_DB) as store:
                leaderboard = store.get_jp_leaderboard(interaction.user.id, (beginn, end))

        multipliers_path = _MULTIPLIERS
        try:
            with open(multipliers_path, "r") as file:
                MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            MULTIPLIERS = {}
        title, leaderboard_desc = await helpers.get_leaderboard(self.bot, leaderboard, interaction.user, media_type, title, MULTIPLIERS)
        embed = discord.Embed(title=title, description=leaderboard_desc)
        
        await interaction.edit_original_response(embed=embed)
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leaderboard(bot))