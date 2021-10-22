from typing import Callable, Dict

from flask_sqlalchemy.model import Model


class ControlDatabase:
    def __init__(self, db):
        self.db = db
    
    def create_database(self) -> None:
        self.db.create_all()

    def insert_data(self, data: Dict, model: Model) -> None:
        data_object = model(**data)
        self.db.session.add(data_object)
        self.db.session.commit()
