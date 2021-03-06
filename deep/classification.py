import os

import numpy as np
import requests

from deep.models import Model


class ClassificationImage:
    def get_image(self, image_url: str) -> str:
        res = requests.get(image_url, headers={"Authorization": f'Bearer {os.environ["SLACK_TOKEN"]}'})
        return res.content

    def classify_image(self, image_url: str) -> str:
        """classify image by using CNN"""
        model = Model()
        image = self.get_image(image_url)

        predicted_value = model.predict(image)

        return predicted_value
