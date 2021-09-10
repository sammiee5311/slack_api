import googletrans


class TranslationApi:
    def __init__(self):
        self.translator = googletrans.Translator()

    def translate_text(self, text, lang="en"):
        return self.translator.translate(text, lang).text
