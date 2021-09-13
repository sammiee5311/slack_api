from api.translate import TranslationApi
from config.commands.translation_languages import LANGUAGES
from flask import request

from commands.slash_command import SlashCommand


class TranslationCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.icon = bot.ICON
        self.send_meesage = bot.send_message
        self.translate_api = TranslationApi()

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        text = data.get("text", "").lstrip().rstrip()
        channel = f"@{user}"

        if not text:
            text = "Please, Write text that you want to translate."
            self.send_meesage(text, channel)
            return

        if "--lang" not in text:
            translated_text = self.translate_api.translate_text(text)
        elif "--language" in text:
            translated_text = ""
            for abbre, country in LANGUAGES.items():
                translated_text += f"{abbre}: {country} \n\n"
        else:
            text, lang = text.split("--lang")
            translated_text = self.translate_api.translate_text(text, lang.lstrip().rstrip())

        self.send_meesage(translated_text, channel)
