import pytest
import discord
from discord.ext import commands
from unittest import mock
from unittest.mock import AsyncMock
from immersionbotcogs.log import Log
from immersionbotcogs.set_goal_media import Set_Goal_Media
from immersionbotcogs.set_goal_points import Set_Goal_Points
from modals.sql import Store, Set_Goal
from modals.constants import _MULTIPLIERS, ACHIEVEMENT_EMOJIS, ACHIEVEMENT_RANKS
from modals.helpers import format_message
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

class TestLogCommand:
    @pytest.fixture
    async def setup(self):
        self.store = log_setup_db()
        self.goal = goal_setup_db()
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
        self.cog = Log(self.bot, self.store, self.goal)
        self.goal_points = Set_Goal_Points(self.bot, self.goal, self.store)
        self.goal_media = Set_Goal_Media(self.bot, self.goal, self.store)
        await self.bot.add_cog(self.cog)
        self.interaction = create_mock_interaction()
        
        try:
            with open(_MULTIPLIERS, "r") as file:
                self.MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            self.MULTIPLIERS = {}
        
        return self.cog, self.store

    @pytest.mark.asyncio
    async def test_log_anime_and_get_achievement(self, setup):
        cog, store = await setup
        media_type = "ANIME"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

        self.interaction.response.send_message.assert_not_called()

        assert self.interaction.edit_original_response.call_count == 1
        assert self.interaction.channel.send.call_count == 1
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 ep of {media_type}')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type],4 )}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 12 eps'
        
        message = self.interaction.channel.send.call_args[1]['content']
        assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 eps!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_vn_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "VN"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 char of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type],4 )}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 50000 chars'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 chars!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_book_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "BOOK"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 page of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type], 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 100 pgs'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 pgs!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_manga_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "MANGA"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 page of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type], 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 250 pgs'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 pgs!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_readtime_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "READTIME"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 min of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type], 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 250 mins'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 mins!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_listening_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "LISTENING"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 min of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type], 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 250 mins'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 mins!!!')
        
    # @pytest.mark.asyncio
    # async def test_log_reading_and_get_achievement(self, setup):
    #     cog, store = await setup
    #     media_type = "READING"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()

    #     assert self.interaction.edit_original_response.call_count == 1
    #     assert self.interaction.channel.send.call_count == 1
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 char of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~0~~ → {round(self.MULTIPLIERS[media_type], 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 50000 chars'
        
    #     message = self.interaction.channel.send.call_args[1]['content']
    #     assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 chars!!!')

    @pytest.mark.asyncio
    async def test_log_anime(self, setup):
        cog, store = await setup
        media_type = "ANIME"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        
        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 ep of {media_type}')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 10 eps'
        
    # @pytest.mark.asyncio
    # async def test_log_vn(self, setup):
    #     cog, store = await setup
    #     media_type = "VN"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        
    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 char of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 49998 chars'

    # @pytest.mark.asyncio
    # async def test_log_book(self, setup):
    #     cog, store = await setup
    #     media_type = "BOOK"

    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        
    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 page of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 98 pgs'
        
    # @pytest.mark.asyncio
    # async def test_log_manga(self, setup):
    #     cog, store = await setup
    #     media_type = "MANGA"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        
    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 page of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 248 pgs'
        
    # @pytest.mark.asyncio
    # async def test_log_readtime(self, setup):
    #     cog, store = await setup
    #     media_type = "READTIME"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 min of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 248 mins'

    # @pytest.mark.asyncio
    # async def test_log_listening(self, setup):
    #     cog, store = await setup
    #     media_type = "LISTENING"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 min of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 248 mins'

    # @pytest.mark.asyncio
    # async def test_log_reading(self, setup):
    #     cog, store = await setup
    #     media_type = "READING"
        
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
    #     await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)

    #     self.interaction.response.send_message.assert_not_called()
    #     assert self.interaction.edit_original_response.call_count == 2
    #     embed = self.interaction.edit_original_response.call_args[1]['embed']
    #     assert embed.title.startswith(f'Logged 1 char of {media_type}')
    #     assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
    #     streak_field = next(field for field in embed.fields if field.name == 'Streak')
    #     assert streak_field.value == 'current streak: **1 days**'
    #     achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
    #     assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 49998 chars'
        
    @pytest.mark.asyncio
    async def test_log_anime_with_anilist_api(self, setup):
        cog, store = await setup
        media_type = "ANIME"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='5114', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 ep of Fullmetal Alchemist: Brotherhood')
        assert embed.description == f'''Anilist: [Fullmetal Alchemist: Brotherhood](https://anilist.co/anime/5114/Fullmetal-Alchemist:-Brotherhood/)\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 10 eps'
        
        message = self.interaction.channel.send.call_args[1]['content']
        assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 eps!!!')
        assert embed.thumbnail.url == 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx5114-Dilr312jctdJ.jpg'
        
    @pytest.mark.asyncio
    async def test_log_vn_with_vndb_api(self, setup):
        cog, store = await setup
        media_type = "VN"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='v1483', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 char of Kitto, Sumiwataru Asairo Yori mo,')
        assert embed.description == f'''VNDB: [Kitto, Sumiwataru Asairo Yori mo,](<https://vndb.org/v1483>)\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 49998 chars'
        
        message = self.interaction.channel.send.call_args[1]['content']
        assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 chars!!!')
        assert embed.thumbnail.url == 'https://t.vndb.org/cv.t/98/79698.jpg'
        
    @pytest.mark.asyncio
    async def test_log_listening_with_tmdb_api(self, setup):
        cog, store = await setup
        media_type = "LISTENING"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='''[5178, 'tv', '/o5hxzWnfIvBioeuLd8Io1Sg3EwG.jpg']''', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 min of Stairway to Heaven')
        assert embed.description == f'''TMDB: [Stairway to Heaven](https://www.themoviedb.org/tv/5178)\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 248 mins'
        
        message = self.interaction.channel.send.call_args[1]['content']
        assert message.startswith(f'{self.interaction.user.mention} congrats on unlocking the achievement {media_type} {ACHIEVEMENT_RANKS[0]} {ACHIEVEMENT_EMOJIS[0]} 1 mins!!!')
        assert embed.thumbnail.url == 'https://image.tmdb.org/t/p/original/o5hxzWnfIvBioeuLd8Io1Sg3EwG.jpg'
        
    @pytest.mark.asyncio
    async def test_log_anime_with_name(self, setup):
        cog, store = await setup
        media_type = "ANIME"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='Fullmetal Alchemist: Brotherhood', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 ep of Fullmetal Alchemist: Brotherhood')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 10 eps'
        
    @pytest.mark.asyncio
    async def test_log_vn_with_name(self, setup):
        cog, store = await setup
        media_type = "VN"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='Kitto, Sumiwataru Asairo Yori mo,', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 char of Kitto, Sumiwataru Asairo Yori mo,')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 49998 chars'

    @pytest.mark.asyncio
    async def test_log_listening_with_name(self, setup):
        cog, store = await setup
        media_type = "LISTENING"
        
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type=media_type, amount='1', name='Stairway to Heaven', comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 2
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 min of Stairway to Heaven')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type], 4)}~~ → {round(self.MULTIPLIERS[media_type] * 2, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 248 mins'

    @pytest.mark.asyncio
    async def test_log_something_multiple_times(self, setup):
        cog, store = await setup
        media_type = "ANIME"
        
        # Execute the log command multiple times
        await cog.log.callback(cog, self.interaction, media_type='ANIME', amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type='ANIME', amount='1', name=None, comment=None)
        await cog.log.callback(cog, self.interaction, media_type='ANIME', amount='1', name=None, comment=None)

        self.interaction.response.send_message.assert_not_called()
        assert self.interaction.edit_original_response.call_count == 3
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        assert embed.title.startswith(f'Logged 1 ep of {media_type}')
        assert embed.description == f'''Source: N/A\n\n{format_message(media_type, self.MULTIPLIERS[media_type], self.MULTIPLIERS)}\n{self.interaction.created_at.strftime("%B")}: ~~{round(self.MULTIPLIERS[media_type] * 2, 4)}~~ → {round(self.MULTIPLIERS[media_type] * 3, 4)}'''
        streak_field = next(field for field in embed.fields if field.name == 'Streak')
        assert streak_field.value == 'current streak: **1 days**'
        achievement_field = next(field for field in embed.fields if field.name == 'Next Achievement')
        assert achievement_field.value == f'{media_type} {ACHIEVEMENT_RANKS[1]} {ACHIEVEMENT_EMOJIS[1]} in 9 eps'

    @pytest.mark.asyncio
    async def test_log_with_goal_display(self, setup):
        #Tests if the goal is displayed correctly on the log for an unrelated goal
        cog, store = await setup
        media_type = "ANIME"
        
        # Execute the log command multiple times
        await self.goal_media.set_goal_media.callback(self.goal_media, self.interaction, media_type='LISTENING', amount='10', name=None, span='DAY')
        await cog.log.callback(cog, self.interaction, media_type='ANIME', amount='1', name=None, comment=None)
        
        assert self.interaction.edit_original_response.call_count == 1
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        goal_field = next(field for field in embed.fields if field.name == 'Goals')
        assert goal_field.value.startswith(f'- 0/10 mins of [LISTENING](https://anilist.co/home)')
        
    @pytest.mark.asyncio
    async def test_log_with_updating_goal_display(self, setup):
        #Tests if the goal is displayed correctly on the log for an related goal
        cog, store = await setup
        media_type = "ANIME"
        
        # Execute the log command multiple times
        await self.goal_media.set_goal_media.callback(self.goal_media, self.interaction, media_type='ANIME', amount='10', name=None, span='DAY')
        await cog.log.callback(cog, self.interaction, media_type='ANIME', amount='1', name=None, comment=None)
        
        assert self.interaction.edit_original_response.call_count == 1
        embed = self.interaction.edit_original_response.call_args[1]['embed']
        goal_field = next(field for field in embed.fields if field.name == 'Goals')
        assert goal_field.value.startswith(f'- 1/10 eps of [ANIME](https://anilist.co/home)')
