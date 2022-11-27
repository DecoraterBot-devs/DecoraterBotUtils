# coding=utf-8
"""
Checks for DecoraterBot.
"""
import discord
from discord import app_commands


class Checks:
    @staticmethod
    def is_bot_owner():
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == int(interaction.client.BotConfig.discord_user_id)
        return app_commands.check(predicate)
