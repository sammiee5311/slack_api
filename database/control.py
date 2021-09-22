from typing import Dict


class ControlDatabase:
    def __init__(self, db):
        self.db = db
    
    def create_database(self):
        self.db.create_all()

    def insert_data(self, data: Dict, model) -> None:
        data_object = model(**data)
        self.db.session.add(data_object)
        self.db.session.commit()
