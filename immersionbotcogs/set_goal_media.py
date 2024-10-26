import discord
from discord.ext import commands
from datetime import timedelta
from datetime import timedelta
from discord import app_commands
from discord.app_commands import Choice
from typing import List, Dict, Tuple, Optional
import time
import json

from modals.goal import Goal
import modals.helpers as helpers
from modals.log_constructor import Log_constructor
from modals.sql import MediaType, Set_Goal, Store
from modals.constants import guild_id, _GOAL_DB, _IMMERSION_CODES, _MULTIPLIERS, _DB_NAME, TMDB_API_KEY
from modals.api_requests import vndb_autocomplete, anilist_autocomplete, tmdb_autocomplete

class Set_Goal_Media(commands.Cog):

    def __init__(self, bot: commands.Bot, db_conn=None, store_conn=None) -> None:
        self.bot = bot
        self.conn = db_conn if db_conn else Set_Goal(_GOAL_DB)
        self.store = store_conn if store_conn else Store(_DB_NAME)

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
    
    @app_commands.command(name='set_goal_media', description=f'Set daily immersion log goals')
    @app_commands.describe(amount='''Episode to watch, characters or pages to read. Time to read/listen in [hr:min] or [min] for example '1.30' or '25'.''')
    @app_commands.choices(media_type = [Choice(name="Visual Novel", value="VN"), Choice(name="Manga", value="MANGA"), Choice(name="Anime", value="ANIME"), Choice(name="Book", value="BOOK"), Choice(name="Readtime", value="READTIME"), Choice(name="Listening", value="LISTENING"), Choice(name="Reading", value="READING")])
    @app_commands.describe(name='''You can use vndb IDs for VN and Anilist codes for Anime, Manga and Light Novels''')
    @app_commands.describe(span='''[Day = Till the end of today], [Daily = Everyday], [Date = Till a certain date ([year-month-day] Example: '2022-12-29')]''')
    async def set_goal_media(self, interaction: discord.Interaction, media_type: str, amount: str, name: Optional[str], span: str):
        
        bool, msg = helpers.check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {msg}', ephemeral=True)
        
        amount = helpers.amount_time_conversion(media_type, amount)
        if not amount.bool:
            return await interaction.response.send_message(ephemeral=True, content='Enter a valid number.')
        
        #introducing upperbound for amount to log for each media_type
        def is_valid_amount(media_type, amount):
            limits = {
                "VN": 4000000,
                "Manga": 10000,
                "Anime": 20000,
                "Book": 10000,
                "Readtime": 40000,
                "Listening": 40000,
                "Reading": 4000000,
            }
            if not (0 < amount <= limits.get(media_type, float('inf'))):
                return False, f"Only numbers under {limits[media_type]} allowed."
            if amount in [float('inf'), float('-inf')]:
                return False, "No infinities allowed."
            return True, None
        
        is_valid_amount, erorr_message = is_valid_amount(media_type, amount.value)
        if not is_valid_amount:
            return await interaction.response.send_message(ephemeral=True, content=erorr_message)
        
        if span.upper() == "DAY":
            span = "DAY"
            created_at = interaction.created_at.replace(hour=0, minute=0, second=0)
            end = interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        elif span.upper() == "DAILY":
            span = "DAILY"
            created_at = interaction.created_at.replace(hour=0, minute=0, second=0)
            end = interaction.created_at + timedelta(days=1)
        elif span.upper() == "WEEKLY":
            span = "WEEKLY"
            created_at = interaction.created_at - timedelta(days=interaction.created_at.weekday())
            end = created_at + timedelta(days=6)
        elif span.upper() == "MONTHLY":
            span = "MONTHLY"
            created_at = interaction.created_at.replace(day=1)
            next_month = interaction.created_at.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
        else:
            created_at = interaction.created_at
            try:
                end = interaction.created_at.replace(year=int((span.split("-"))[0]), month=int((span.split("-"))[1]), day=int((span.split("-"))[2]), hour=0, minute=0, second=0)
                if end > interaction.created_at + timedelta(days=366):
                    return await interaction.response.send_message(content='''A goal span can't be longer than a year.''', ephemeral=True)
                if end < interaction.created_at:
                    return await interaction.response.send_message(content='''You can't set a goal in the past.''', ephemeral=True)
            except Exception:
                return await interaction.response.send_message(ephemeral=True, content='Please enter the date in the correct format.')
            else:
                span = "DATE"
                if end < created_at:
                    return await interaction.response.send_message(ephemeral=True, content='''You can't set goals for the past.''')

        if name:
            if len(name) > 150:
                return await interaction.response.send_message(ephemeral=True, content='Only names under 150 characters allowed.')

        goal_type = "MEDIA" if not name else "SPECIFIC"
        bool = self.conn.check_goal_exists(interaction.user.id, goal_type, span, media_type.upper(), name)
        if bool:
            return await interaction.response.send_message(ephemeral=True, content='You already set this goal.')

        if len(self.conn.get_goals(interaction.user.id)) > 10:
            return await interaction.response.send_message(ephemeral=True, content='''You can't set more than 10 goals. To delete a goal do ```/delete_goal``''')
        if not name:
            name = ""
            
        if goal_type == "SPECIFIC" and media_type == "LISTENING":
            self.conn.new_goal(interaction.user.id, goal_type, media_type.upper(), 0, amount.value, str(eval(name)).replace("'", "''"), span, created_at, end)
        else:
            self.conn.new_goal(interaction.user.id, goal_type, media_type.upper(), 0, amount.value, name, span, created_at, end)
        
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
            
        logs = self.store.get_logs_by_user(interaction.user.id, media_type, (created_at, end), None)
        goal_msgs = []
        for log in logs:
            goal_msg = helpers.update_goals(interaction, [Goal(interaction.user.id, goal_type, MediaType[media_type.upper()], 0, amount.value, name, span, created_at, end)], Log_constructor(interaction.user.id, log.media_type.value, log.amount, log.title, log.note, log.created_at), self.conn, media_type, MULTIPLIERS, codes, codes_path)
            goal_msgs.append(goal_msg)
            
        name = helpers.get_name_of_immersion(media_type, name, codes, _IMMERSION_CODES)
        try:
            updated_date = f'<t:{int(end.timestamp())}:R>'
        except Exception:
            updated_date = end
        await interaction.response.send_message(ephemeral=True, content=f'''## Set {goal_type} goal as {span} goal\n- {amount.value} {helpers.media_type_format(media_type.upper())} of [{name[1]}]({name[2]}) ({updated_date})\n\nUse ``/goals`` to view your goals for <t:{int(time.mktime((interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D>''', suppress_embeds=True)

        if goal_msgs:
            for goal_message in goal_msgs:
                if goal_message == []:
                    continue
                else:
                    await interaction.channel.send(content=f'{goal_message[0][0]} congrats on finishing your goal of {goal_message[0][1]} {goal_message[0][2]} {goal_message[0][3]} {goal_message[0][4]}, keep the spirit!!! {goal_message[0][5]} {helpers.random_emoji()}')
    
        if self.store.check_if_in_memory():
            self.conn.close()
            self.store.close()
    
    @set_goal_media.autocomplete('name')
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
    await bot.add_cog(Set_Goal_Media(bot))
