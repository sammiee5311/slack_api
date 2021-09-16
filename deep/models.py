import numpy as np
import tensorflow as tf
from config.commands.names import IMAGE_SIZE, NAMES


class Model:
    def __init__(self):
        self.model = tf.keras.models.load_model('./config/model.h5')
        self.names = NAMES

    def predict(self, image):
        image = tf.image.decode_image(image)
        image = tf.expand_dims(image, axis=0)
        image = image / 255

        resized_image = tf.image.resize(image, size=IMAGE_SIZE)
        
        result = self.model.predict(resized_image)

        idx = np.argmax(result[0])
        return self.names[idx]
