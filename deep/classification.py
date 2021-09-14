import os

import requests


class ClassificationImage:
    def get_image(self, image_url):
        res = requests.get(image_url, headers={"Authorization": f'Bearer {os.environ["SLACK_TOKEN"]}'})
        return res.content

    def classify_image(self, image_url):
        """classify image by using CNN"""
        image = self.get_image(image_url)

        with open("image.png", "w+b") as f:
            f.write(bytearray(image))

        return 1
