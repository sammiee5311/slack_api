from abc import ABC, abstractmethod

from bot import SlackBot


class SlashCommand(ABC):
    @abstractmethod
    def __init__(self, bot: SlackBot):
        """init method"""

    @abstractmethod
    def handler(self):
        """slash command handler"""
