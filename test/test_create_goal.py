import pytest
import discord
from discord.ext import commands
from unittest import mock
from unittest.mock import AsyncMock
from immersionbotcogs.set_goal_media import Set_Goal_Media
from immersionbotcogs.log import Log
from modals.sql import Store, Set_Goal
from modals.constants import _MULTIPLIERS
from datetime import timedelta
import json


def create_mock_interaction():
    interaction = mock.Mock()
    interaction.user = mock.Mock()
    interaction.user.id = 250351201923629058
    interaction.user.display_name = "Timm"
    interaction.response = AsyncMock()
    interaction.created_at = discord.utils.utcnow()
    interaction.edit_original_response = AsyncMock()
    interaction.channel = mock.Mock()
    interaction.channel.id = 1010323632750350437
    interaction.channel.type = discord.ChannelType.text
    interaction.channel.send = AsyncMock()
    
    return interaction

def log_setup_db():
    store = Store(":memory:")
    store.fetch('''CREATE TABLE logs (
        discord_guild_id INTEGER,
        discord_user_id INTEGER,
        media_type TEXT,
        amount INTEGER,
        title TEXT,
        note TEXT,
        created_at TIMESTAMP
    )''')
    return store

def goal_setup_db():
    store = Set_Goal(":memory:")
    store.fetch('''CREATE TABLE "completed" (
    "discord_user_id"	INTEGER,
    "goal_type"	TEXT,
    "amount"	INTEGER,
    "media_type"	TEXT,
    "text"	TEXT
)''')
    store.fetch('''CREATE TABLE "goals" (
    "discord_user_id"	INTEGER,
    "goal_type"	TEXT,
    "media_type"	TEXT,
    "current_amount"	INTEGER,
    "amount"	INTEGER,
    "text"	TEXT,
    "span"	TEXT,
    "created_at"	TEXT,
    "end"	TEXT
)''')
    return store

class TestSetMediaGoalCommand:
    @pytest.fixture
    async def setup(self):
        self.store = log_setup_db()
        self.goal = goal_setup_db()
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
        self.cog = Set_Goal_Media(self.bot, self.goal, self.store)
        self.log_cog = Log(self.bot, self.store, self.goal)
        await self.bot.add_cog(self.cog)
        self.interaction = create_mock_interaction()
        
        try:
            with open(_MULTIPLIERS, "r") as file:
                self.MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            self.MULTIPLIERS = {}
        
        return self.cog, self.goal

    @pytest.mark.asyncio
    async def test_create_media_goal(self, setup):
        cog, store = await setup
        
        # Mocking helper functions if necessary
        with mock.patch("modals.helpers.media_type_format", return_value="eps"), \
            mock.patch("modals.helpers.get_name_of_immersion", return_value=("", "Anime", "https://anilist.co/home")):
            
            # Call the slash command
            await cog.set_goal_media.callback(cog, self.interaction, media_type="ANIME", amount="10", span="DAY", name='')

        
            #self.interaction.response.send_message.assert_called_once_with(ephemeral=True, content=f'## Set MEDIA goal as DAY goal\n- 10 eps of [Anime](https://anilist.co/home) (<t:{int(self.interaction.created_at.timestamp())}:R>)\n\nUse ``/goals`` to view your goals for <t:{int(time.mktime((self.interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D>')

    @pytest.mark.asyncio
    async def test_create_media_goal_with_anilist_api(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await cog.set_goal_media.callback(cog, self.interaction, media_type="ANIME", amount="10", span="DAY", name='30')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "ANIME"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == "30"
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 0
        
        
    @pytest.mark.asyncio
    async def test_create_media_goal_with_vndb_api(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await cog.set_goal_media.callback(cog, self.interaction, media_type="VN", amount="10", span="DAY", name='v1483')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "VN"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == "v1483"
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 0
        
    @pytest.mark.asyncio
    async def test_create_media_goal_with_tmdb_api(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await cog.set_goal_media.callback(cog, self.interaction, media_type="LISTENING", amount="10", span="DAY", name="[5178, 'tv', '/o5hxzWnfIvBioeuLd8Io1Sg3EwG.jpg']")
    
        #self.interaction.response.send_message.assert_called_once_with(ephemeral=True, content=f'## Set SPECIFIC goal as DAY goal\n- 10 mins of [Stairway to Heaven](https://www.themoviedb.org/tv/5178) (<t:{int(self.interaction.created_at.timestamp())}:R>)\n\nUse ``/goals`` to view your goals for <t:{int(time.mktime((self.interaction.created_at.replace(hour=0, minute=0, second=0, microsecond=0)).timetuple()))}:D>')

        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "LISTENING"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == "[5178, ''tv'', ''/o5hxzWnfIvBioeuLd8Io1Sg3EwG.jpg'']"
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 0
        

    @pytest.mark.asyncio
    async def test_create_media_goal_ends_in_past(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await cog.set_goal_media.callback(cog, self.interaction, media_type="LISTENING", amount="10", span="1000-01-01", name='')
    
        self.interaction.response.send_message.assert_called_once_with(ephemeral=True, content=f"You can't set a goal in the past.")
        
    @pytest.mark.asyncio
    async def test_create_media_goal_span_longer_than_year(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await cog.set_goal_media.callback(cog, self.interaction, media_type="LISTENING", amount="10", span="9999-01-01", name='')
    
        self.interaction.response.send_message.assert_called_once_with(ephemeral=True, content=f"A goal span can't be longer than a year.")
        
    @pytest.mark.asyncio
    async def test_create_media_goal_after_logging_for_goal(self, setup):
        cog, store = await setup
        
        # Call the slash command
        await self.log_cog.log.callback(self.log_cog, self.interaction, media_type="LISTENING", amount="1", name='', comment='')
        await cog.set_goal_media.callback(cog, self.interaction, media_type="LISTENING", amount="10", span="DAY", name='')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "LISTENING"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == ""
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 1
        
    @pytest.mark.asyncio
    async def test_create_specific_goal_after_logging_for_goal(self, setup):
        # When entering something in the name parameter when setting a goal, then that goal is considered a specific goal.
        # Let's say you create a goal to watch 10 eps of Neon Genesis Evangelion (30) and then log 1 ep of Neon Genesis Evangelion (30) (before or after it doesn't matter).
        # The current amount i.e your progress with that goal should go up by one since the name parameter matches the name of the media you logged and the name parameter in the goal you set.
        #
        # This test makes sure this is true
        
        cog, store = await setup
        
        await self.log_cog.log.callback(self.log_cog, self.interaction, media_type="ANIME", amount="1", name='30', comment='')
        await cog.set_goal_media.callback(cog, self.interaction, media_type="ANIME", amount="10", span="DAY", name='30')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "ANIME"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == "30"
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 1
        
    @pytest.mark.asyncio
    async def test_create_specific_goal_after_logging_not_counting_for_goal(self, setup):
        # When entering something in the name parameter when setting a goal, then that goal is considered a specific goal.
        # Let's say you create a goal to watch 10 eps of Neon Genesis Evangelion (30) and then log 1 ep of Neon Genesis Evangelion (30) (before or after it doesn't matter).
        # The current amount i.e your progress with that goal should go up by one since the name parameter matches the name of the media you logged and the name parameter in the goal you set.
        
        # This test makes sure this is false
        
        cog, store = await setup

        await self.log_cog.log.callback(self.log_cog, self.interaction, media_type="ANIME", amount="1", name='', comment='')
        await cog.set_goal_media.callback(cog, self.interaction, media_type="ANIME", amount="10", span="DAY", name='30')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "ANIME"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == "30"
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 0
        
    @pytest.mark.asyncio
    async def test_create_media_goal_after_logging_counting_for_goal(self, setup):
        # When entering something in the name parameter when setting a goal, then that goal is considered a specific goal.
        # Let's say you create a goal to watch 10 eps of Neon Genesis Evangelion (30) and then log 1 ep of Neon Genesis Evangelion (30) (before or after it doesn't matter).
        # The current amount i.e your progress with that goal should go up by one since the name parameter matches the name of the media you logged and the name parameter in the goal you set.
        # It should also go up when you are logging something specific of the same media type.
        
        cog, store = await setup

        await self.log_cog.log.callback(self.log_cog, self.interaction, media_type="ANIME", amount="1", name='30', comment='')
        await cog.set_goal_media.callback(cog, self.interaction, media_type="ANIME", amount="10", span="DAY", name='')
    
        goals = self.goal.get_goals(self.interaction.user.id)
        assert goals[0].media_type.value == "ANIME"
        assert goals[0].amount == 10
        assert goals[0].span == "DAY"
        assert goals[0].text == ""
        assert goals[0].created_at == str(self.interaction.created_at.replace(hour=0, minute=0, second=0))
        assert goals[0].end == str(self.interaction.created_at.replace(hour=0, minute=0, second=0) + timedelta(days=1))
        assert goals[0].current_amount == 1
        
