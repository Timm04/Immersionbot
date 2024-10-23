import discord
from discord.ext import commands
from modals.sql import Set_jp
import modals.helpers as helpers
import re
from discord import app_commands
from modals.constants import ALLOWED_CHANNELS, guild_id, _JP_DB
from collections import deque

jp_REGEX = re.compile(r"[一-鿿ぁ-ゔァ-ヴーａ-ｚＡ-Ｚ０-９々〆〤ヶ]+|[ぁ-ゔ]+|[ァ-ヴー]+|[々〆〤ヶ]+[]+] +/u")
latin_REGEX = re.compile(r"""[a-zA-Z0-9()*_\-!#$%^&*,."\'\][]""")

class LimitedQueue:
    def __init__(self):
        self.max_length = 20
        self.data = deque(maxlen=self.max_length)

    def add(self, item):
        self.data.append(item)

    def __repr__(self):
        return repr(self.data)

class Japanese_tracker(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.limitedQueue = LimitedQueue()

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(guild_id)
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.channel.id not in ALLOWED_CHANNELS:
            return
        with Set_jp("japanese.db") as store:
            try:
                store.delete_output(message.id)
            except Exception:
                return

    @app_commands.command(name='output_channels', description=f'Shows the output channels.')
    async def output_channels(self, interaction: discord.Interaction):
        channels = []
        for id in ALLOWED_CHANNELS:
            channels.append(f'<#{id}>')
            
        await interaction.response.send_message(content=f'''In the following channels, outputting in Japanese will give you points. 
{', '.join(channels)}''', ephemeral=True)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.channel.id == 814947177608118273:
            if message.content.startswith("."):
                await message.channel.send("If you are trying to run a command from the immersion bot, then please use a / instead of a dot. For more info refer to <#1241081712193175665>.")
        
        channel = message.channel
        if channel.id not in ALLOWED_CHANNELS:
            return
        
        if message.author.bot:
            return
        
        if not message.content:
            return
        
        print(message.channel.name)

        japanese = helpers.regex_jp_contents(message.content, jp_REGEX)

        latin = helpers.regex_latin_contents(message.content, latin_REGEX)
        if japanese > 0 and (japanese + latin) / 2 > latin and (japanese + latin) / 2 < japanese:
            if message.content in self.limitedQueue.data and japanese > 12:
                print("in queue already")
                return
            
            if len(message.content) < japanese * 0.7:
                print("too few jp chars")
                return
            
        
            with Set_jp(_JP_DB) as store:
                if store.find_similar(message.author.id, message.content) and japanese > 12:
                    print("dupe")
                    return
                
                print(message.content)
                store.log_jp(message.author.id, message.channel.id, message.id, "OUTPUT", message.content, japanese, message.created_at)
                await self.limitedQueue.add(message.content)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Japanese_tracker(bot))
