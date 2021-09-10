from abc import ABC, abstractmethod


class SlashCommand(ABC):
    @abstractmethod
    def __init__(self, bot):
        """init method"""

    @abstractmethod
    def handler(self):
        """slash command handler"""
