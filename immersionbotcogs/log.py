import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import time
from typing import Dict, Tuple, List,  Optional
import json

from modals.sql import Store, Set_Goal
from modals.log_constructor import Log_constructor
from modals.api_requests import vndb_autocomplete, anilist_autocomplete, tmdb_autocomplete
from modals.constants import guild_id, _DB_NAME, _GOAL_DB, _IMMERSION_CODES, _MULTIPLIERS, TMDB_API_KEY
from modals.helpers import check_maintenance, amount_time_conversion, _to_amount, format_message, get_name_of_immersion, media_type_format_grammar, check_achievements, update_goals, get_goal_description, media_type_format, random_emoji, add_suffix_to_date

cache: Dict[str, Tuple[List[app_commands.Choice], float]] = {}
CACHE_EXPIRY_TIME = 10 * 60

class Log(commands.Cog):

    def __init__(self, bot: commands.Bot, db_conn=None, goal_conn=None) -> None:
        self.bot = bot
        self.conn = db_conn if db_conn else Store(_DB_NAME)
        self.goal = goal_conn if goal_conn else Set_Goal(_GOAL_DB)

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)

    @app_commands.command(name='log', description=f'Log your immersion')
    @app_commands.describe(amount='''Episodes watched, characters or pages read. Time read/listened in [hr:min:sec], [min:sec], [min] for example '1.30' or '25'.''')
    @app_commands.describe(comment='''Comment''')
    @app_commands.describe(name='''You can use vndb IDs and titles for VN and Anilist codes for Anime and Manga''')
    @app_commands.choices(media_type = [Choice(name="Visual Novel", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    async def log(self, interaction: discord.Interaction, media_type: str, amount: str, name: Optional[str], comment: Optional[str]):
        
        #media_type = media_type.upper()
        # only allowed to log in #bot-debug, #immersion-logs, DMs
        # DMs not working
        channel = interaction.channel
        if channel.id != 1010323632750350437 and channel.id != 814947177608118273 and channel.type != discord.ChannelType.private and channel.id != 947813835715256393:
            return await interaction.response.send_message(ephemeral=True, content='You can only log in #immersion-log or DMs.')
        
        bool, info = check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {info.maintenance_msg}', ephemeral=True)
        
        amount = amount_time_conversion(media_type, amount)
        if not amount.bool:
            return await interaction.response.send_message(ephemeral=True, content='Enter a valid number.')
        
        # introducing upperbound for amount to log for each media_type
        def is_valid_amount(media_type, amount):
            limits = {
                "VN": 2000000,
                "MANGA": 3000,
                "ANIME": 200,
                "BOOK": 500,
                "READTIME": 400,
                "LISTENING": 1000,
                "READING": 2000000,
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
        
        await interaction.response.defer()

        date = interaction.created_at
        goals = self.goal.get_goals(interaction.user.id)
        first_date = date.replace(day=1, hour=0, minute=0, second=0)

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

        weighed_amount = _to_amount(media_type, amount.value, MULTIPLIERS)
        point_conversion = format_message(media_type, weighed_amount, MULTIPLIERS)
        immersion_title = get_name_of_immersion(media_type, name, codes, codes_path)
        media_suffix = media_type_format_grammar(media_type, amount.value)
        
        monthy_points_before_log = self.conn.total_points_for_user(interaction.user.id, MULTIPLIERS, (first_date, date))
        old_rank_achievement, old_achievemnt_points, old_next_achievement, old_emoji, old_rank_name, old_next_rank_emoji, old_next_rank_name, id = check_achievements(interaction.user.id, media_type.upper(), self.conn, MULTIPLIERS)

        self.conn.new_log(guild_id, interaction.user.id, media_type.upper(), amount.value, name, comment, date)
        
        current_rank_achievement, current_achievemnt_points, new_rank_achievement, new_emoji, new_rank_name, new_next_rank_emoji, new_next_rank_name, id = check_achievements(interaction.user.id, media_type.upper(), self.conn, MULTIPLIERS)
        monthly_points_after_log = self.conn.total_points_for_user(interaction.user.id, MULTIPLIERS, (first_date, date))

        if goals:
            log = Log_constructor(interaction.user.id, media_type, amount.value, name, comment, interaction.created_at)
            goal_message = update_goals(interaction, goals, log, self.goal, media_type, MULTIPLIERS, codes, codes_path)
            goals = self.goal.get_goals(interaction.user.id)
    
            goals_description = get_goal_description(goals, codes_path, codes)
            
        else:
            goals_description = []
            goal_message = []

        streak = self.conn.get_log_streak(interaction.user.id)[0].current_streak
        
        def create_log_embed():
            embed = discord.Embed(
                title=f'''Logged {round(amount.value,2)} {media_suffix} of {immersion_title[1]} {random_emoji()}''',
                description=f'{immersion_title[0]}\n\n{point_conversion}\n{date.strftime("%B")}: ~~{monthy_points_before_log}~~ → {monthly_points_after_log}',
                color=discord.Colour.random())
            
            embed.add_field(name='Streak', value=f'current streak: **{streak} days**')
            
            if new_next_rank_name != "Master" and old_next_achievement == new_rank_achievement:
                embed.add_field(name='Next Achievement', value=media_type.upper() + " " + new_next_rank_name + " " + new_next_rank_emoji + " in " + str(round(new_rank_achievement-current_achievemnt_points, 2)) + " " + media_type_format(media_type.upper()))
            elif old_next_achievement != new_rank_achievement:
                embed.add_field(name='Next Achievement', value=media_type.upper() + " " + new_next_rank_name + " " + new_next_rank_emoji + " in " + str(int(new_rank_achievement)) + " " + media_type_format(media_type.upper()), inline=True)
            
            if goals_description:
                embed.add_field(name='Goals', value='\n'.join(goals_description), inline=False)
            
            embed.set_footer(text=f'From {interaction.user.display_name} on {add_suffix_to_date(interaction.created_at)}', icon_url=interaction.user.display_avatar.url)
            if immersion_title[3]:
                embed.set_thumbnail(url=immersion_title[3])
            
            return embed

        embed = create_log_embed()
        
        message = await interaction.edit_original_response(embed=embed)
        
        if comment:
            await message.reply(content=">>> " + comment, mention_author=False)
            
        if old_next_achievement != new_rank_achievement:
            await message.reply(content=f'{interaction.user.mention} congrats on unlocking the achievement {media_type.upper()} {new_rank_name} {new_emoji} {str(int(current_rank_achievement))} {media_type_format(media_type.upper())}!!! {random_emoji()}')

        if goal_message != [] and goals:
            await interaction.channel.send(content=f'{goal_message[0][0]} congrats on finishing your goal of {goal_message[0][1]} {goal_message[0][2]} {goal_message[0][3]} {goal_message[0][4]}, keep the spirit!!! {goal_message[0][5]} {random_emoji()}')
        
        if self.conn.check_if_in_memory():
            self.conn.close()
            self.goal.close()
        
    @log.autocomplete('name')
    async def log_autocomplete(self, interaction: discord.Interaction, current: str,) -> List[app_commands.Choice[str]]:

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
    await bot.add_cog(Log(bot))
