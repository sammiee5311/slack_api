from bot import db


class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    team = db.Column(db.String, nullable=False)
    is_leader = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
