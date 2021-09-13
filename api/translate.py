import googletrans
from config.commands.translation_languages import LANGUAGES
from config.errors import InvalidLanguage


class TranslationApi:
    def __init__(self):
        self.translator = googletrans.Translator()

    def translate_text(self, text, lang="en"):
        if lang not in LANGUAGES:
            return "Please, write supported language. To see supported languages, type /translation --languages"
        else:
            return self.translator.translate(text, lang).text
