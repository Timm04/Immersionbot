import discord
from discord.ext import commands
from datetime import timedelta
from typing import Optional
from discord import app_commands
from discord.app_commands import Choice
from typing import List, Dict, Tuple
import json
import time

from modals.helpers import _to_amount, format_message, get_name_of_immersion, media_type_format_grammar, media_type_format, random_emoji, add_suffix_to_date, amount_time_conversion, check_achievements, check_maintenance
from modals.sql import Store
from modals.api_requests import vndb_autocomplete, anilist_autocomplete, tmdb_autocomplete
from modals.constants import guild_id, _DB_NAME, _IMMERSION_CODES, _MULTIPLIERS, TMDB_API_KEY

class Backfill(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @app_commands.command(name='backfill', description=f'Backfill your immersion')
    @app_commands.describe(amount='''Episodes watched, characters or pages read. Time read/listened in [hr:min] or [min] for example '1.30' or '25'.''')
    @app_commands.describe(comment='''Comment''')
    @app_commands.describe(date='''[year-month-day] Example: '2023-12-24' ''')
    @app_commands.describe(name='''You can use vndb IDs and titles for VN and Anilist codes for Anime and Manga''')
    @app_commands.choices(media_type = [Choice(name="Visual Novel", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    async def backfill(self, interaction: discord.Interaction, date: str, media_type: str, amount: str, name: Optional[str], comment: Optional[str]):

        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private and channel.id != 947813835715256393:
            return await interaction.response.send_message(content='You can only backfill in #immersion-log or DMs.',ephemeral=True)
        
        bool, msg = check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {msg.maintenance_msg}', ephemeral=True)
            
        amount = amount_time_conversion(media_type, amount)
        if not amount.bool:
            return await interaction.response.send_message(ephemeral=True, content='Enter a valid number.')
        
        #introducing upperbound for amount to log for each media_type
        def is_valid_amount(media_type, amount):
            limits = {
                "VN": 2000000,
                "Manga": 3000,
                "Anime": 200,
                "Book": 500,
                "Readtime": 400,
                "Listening": 1000,
                "Reading": 2000000,
            }
            if not (0 < amount <= limits.get(media_type, float('inf'))):
                return False, f"Only numbers under {limits[media_type]} allowed."
            if amount in [float('inf'), float('-inf')]:
                return False, "No infinities allowed."
            return True, None
        
        is_valid_amount, erorr_message = is_valid_amount(media_type, amount.value)
        if not is_valid_amount:
            return await interaction.response.send_message(ephemeral=True, content=erorr_message)
        
        if name:
            if len(name) > 150:
                return await interaction.response.send_message(ephemeral=True, content='Only names under 150 characters allowed.')
        if comment:
            if len(comment) > 150:
                return await interaction.response.send_message(ephemeral=True, content='Only comments under 150 characters allowed.')

        try:
            date = interaction.created_at.replace(year=int(date.split('-')[0]), month=int(date.split('-')[1]), day=int(date.split('-')[2]))
            if date > interaction.created_at:
                return await interaction.response.send_message(content='''You can't backfill in the future.''', ephemeral=True)
            if date < interaction.created_at - timedelta(days=90):
                return await interaction.response.send_message(content='''You can't backfill more than 90 days in the past.''', ephemeral=True)
        except Exception:
            return await interaction.response.send_message(content='Enter a valid date. [Year-Month-day] e.g 2023-12-24', ephemeral=True)
        
        await interaction.response.defer()

        multipliers_path = _MULTIPLIERS
        try:
            with open(multipliers_path, "r") as file:
                MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            MULTIPLIERS = {}
            
        codes_path = _IMMERSION_CODES
        try:
            with open(codes_path, "r") as file:
                codes = json.load(file)
        except FileNotFoundError:
            codes = {}
            
        with Store(_DB_NAME) as store:
            first_date = date.replace(day=1, hour=0, minute=0, second=0)
            
            weighed_amount = _to_amount(media_type, amount.value, MULTIPLIERS)
            point_conversion_text = format_message(media_type, weighed_amount, MULTIPLIERS)
            immersion_title = get_name_of_immersion(media_type, name, codes, codes_path)
            media_suffix = media_type_format_grammar(media_type, amount.value)
            
            monthy_points_before_log = self.conn.total_points_for_user(interaction.user.id, MULTIPLIERS, (first_date, date))
            old_rank_achievement, old_achievemnt_points, old_next_achievement, old_emoji, old_rank_name, old_next_rank_emoji, old_next_rank_name, id = check_achievements(interaction.user.id, media_type.upper(), store, MULTIPLIERS)
            
            store.new_log(guild_id, interaction.user.id, media_type.upper(), amount.value, name, comment, date)
            
            current_rank_achievement, current_achievemnt_points, new_rank_achievement, new_emoji, new_rank_name, new_next_rank_emoji, new_next_rank_name, id = check_achievements(interaction.user.id, media_type.upper(), store, MULTIPLIERS)
        
            monthly_points_after_log = self.conn.total_points_for_user(interaction.user.id, MULTIPLIERS, (first_date, date))
        
        streak = self.conn.get_log_streak(interaction.user.id)[0].current_streak

        def create_log_embed():
            embed = discord.Embed(
                title=f'''Logged {round(amount.value,2)} {media_suffix} of {immersion_title[1]} {random_emoji()}''',
                description=f'{immersion_title[0]}\n\n{point_conversion_text}\n{date.strftime("%B")}: ~~{monthy_points_before_log}~~ → {monthly_points_after_log}',
                color=discord.Colour.random())
            
            embed.add_field(name='Streak', value=f'current streak: **{streak} days**')
            
            if new_next_rank_name != "Master" and old_next_achievement == new_rank_achievement:
                embed.add_field(name='Next Achievement', value=media_type.upper() + " " + new_next_rank_name + " " + new_next_rank_emoji + " in " + str(round(new_rank_achievement-current_achievemnt_points, 2)) + " " + media_type_format(media_type.upper()))
            elif old_next_achievement != new_rank_achievement:
                embed.add_field(name='Next Achievement', value=media_type.upper() + " " + new_next_rank_name + " " + new_next_rank_emoji + " in " + str(int(new_rank_achievement)) + " " + media_type_format(media_type.upper()), inline=True)
            
            embed.set_footer(text=f'From {interaction.user.display_name} on {add_suffix_to_date(interaction.created_at)}', icon_url=interaction.user.display_avatar.url)
            if immersion_title[3]:
                embed.set_thumbnail(url=immersion_title[3])
            
            return embed

        embed = create_log_embed()
        
        message = await interaction.edit_original_response(embed=embed)
        store.close()
        
    @backfill.autocomplete('name')
    async def log_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:

        cache: Dict[str, Tuple[List[app_commands.Choice], float]] = {}
        CACHE_EXPIRY_TIME = 10 * 60

        def get_cached_results(query: str):
            if query in cache:
                cached_data, timestamp = cache[query]
                if time.time() - timestamp < CACHE_EXPIRY_TIME:
                    return cached_data
                else:
                    del cache[query]
            return None

        def update_cache(query: str, data: List[app_commands.Choice]):
            cache[query] = (data, time.time())

        cached_result = get_cached_results(current)
        if cached_result:
            return cached_result

        media_type = interaction.namespace['media_type']
        suggestions = []

        if media_type == 'VN' or media_type == "READTIME":
            suggestions = await vndb_autocomplete(current)
        
        elif media_type == 'ANIME' or media_type == 'MANGA':
            suggestions = await anilist_autocomplete(current, media_type)

        elif media_type == 'LISTENING':
            suggestions = await tmdb_autocomplete(current, TMDB_API_KEY)

        update_cache(current, suggestions)
        return suggestions

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Backfill(bot))
