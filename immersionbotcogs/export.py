import discord
from discord.ext import commands
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice
from modals.sql import Store
import csv
import os
import asyncio
import json
import modals.helpers as helpers
from datetime import date as timedelta
from modals.constants import TIMEFRAMES, _DB_NAME, guild_id, _IMMERSION_CODES

class Export(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
                
    @app_commands.command(name='export', description=f'Export your immersion logs.')
    @app_commands.describe(timeframe='''DEFAULT=MONTH; Week, Month, Year, All, [year-month-day] or [year-month-day-year-month-day]''')
    @app_commands.choices(media_type = [Choice(name="Visual Novels", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    async def export(self, interaction: discord.Interaction, timeframe: Optional[str], media_type: Optional[str]):

        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private:
            return await interaction.response.send_message(ephemeral=True, content='You can only export your logs in #immersion-log or DMs.')
        
        bool, msg = helpers.check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {msg.maintenance_msg}', ephemeral=True)

        if not media_type:
            media_type = None

        if not timeframe or timeframe.upper() == "MONTH":
            #Month
            timeframe = "Monthly"
            beginn = interaction.created_at.replace(day=1, hour=0, minute=0)
            if beginn.month == 12:
                end = beginn.replace(year=beginn.year + 1, month=1)
            else:
                end = beginn.replace(month=beginn.month + 1, day=1)

        elif timeframe.upper() == "WEEK":
            beginn = (interaction.created_at - timedelta(days=interaction.created_at.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (beginn + timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
        
        elif timeframe.upper() == "YEAR":
            beginn = interaction.created_at.date().replace(month=1, day=1)
            end = interaction.created_at.date().replace(month=12, day=31)
            timeframe = f"""{beginn.strftime("%Y")}"""
        
        elif timeframe.upper() == "ALL":
            beginn = interaction.created_at.replace(year=2020)
            end = interaction.created_at
            timeframe = f"""All Time"""

        elif timeframe.upper() not in TIMEFRAMES:
            try:
                dates = timeframe.split('-')
                if len(timeframe.split('-')) == 6:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]))
                    end = interaction.created_at.replace(year=int(dates[3]), month=int(dates[4]), day=int(dates[5]))
                    timeframe = f"""{beginn.strftime("{0}").format(helpers.ordinal(beginn.day))}-{end.strftime("{0} %b").format(helpers.ordinal(end.day))}"""
                    if beginn > end:
                        return await interaction.response.send_message(content='You switched up the dates.', ephemeral=True)
                elif len(timeframe.split('-')) == 3:
                    beginn = interaction.created_at.replace(year=int(dates[0]), month=int(dates[1]), day=int(dates[2]), hour=0, minute=0, second=0)
                    end = beginn + timedelta(days=1)
                    if beginn > interaction.created_at:
                        return await interaction.response.send_message(content='''You can't look into the future.''', ephemeral=True)
                else:
                    return Exception
            except Exception:
                return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)

        with Store(_DB_NAME) as store:
            logs = store.get_logs_by_user(interaction.user.id, media_type, (beginn, end), None)
        if logs == []:
            return await interaction.edit_original_response(content='No logs were found.')

        await interaction.response.defer()

        filename = interaction.user.name + f" logs{' (' + media_type + ')' if media_type else ''}"

        codes_path = _IMMERSION_CODES
        try:
            with open(codes_path, "r") as file:
                codes = json.load(file)
        except FileNotFoundError:
            codes = {}

        with open(f'{filename}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            field = ["discord_user_id", "media_type", "amount", "title", "note", "created_at"]
            
            writer.writerow(field)
            for log in logs:
                writer.writerow([f"{log.discord_user_id}", f"{log.media_type}", f"{log.amount}", f"{helpers.get_name_of_immersion(log.media_type, log.title, codes, codes_path)[1]}",f"{log.note}", f"{log.created_at}"])

        await interaction.delete_original_response()
        await interaction.channel.send(file=discord.File(fr'{filename}.csv'))
        
        await asyncio.sleep(1)

        for file in os.listdir():
            if file == f'{filename}.csv':
                os.remove(f'{filename}.csv')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Export(bot))
