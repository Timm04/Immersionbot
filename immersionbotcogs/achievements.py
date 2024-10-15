import discord
from discord.ext import commands
from discord import app_commands
from modals.sql import Store
from modals.constants import _MULTIPLIERS, tmw_id, _DB_NAME
import modals.helpers as helpers
import json

class Achievements(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.myguild = self.bot.get_guild(tmw_id)
                
    @app_commands.command(name='achievements', description=f'Shows your immersion milestones.')
    async def achievements(self, interaction: discord.Interaction):
        
        bool, msg = helpers.check_maintenance()
        if bool:
            return await interaction.response.send_message(content=f'In maintenance: {msg.maintenance_msg}', ephemeral=True)

        await interaction.response.defer()
        multipliers_path = _MULTIPLIERS
        try:
            with open(multipliers_path, "r") as file:
                MULTIPLIERS = json.load(file)
        except FileNotFoundError:
            MULTIPLIERS = {}
        with Store(_DB_NAME) as store:
            points = store.get_logs_by_user(interaction.user.id, None, ("2000-01-01", interaction.created_at), None)
        weighed_points_mediums = helpers.multiplied_points(points, MULTIPLIERS)
        abmt = helpers.calc_achievements(weighed_points_mediums)
        achievements = helpers.get_achievement_text(abmt)
        embed = discord.Embed(title='All Time Achievements')
        embed.add_field(name='Achievements', value='''
'''.join(achievements))
        await interaction.edit_original_response(embed=embed)
    
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Achievements(bot))
