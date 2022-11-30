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
            return interaction.client.is_owner(interaction.user)
        return app_commands.check(predicate)
