from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    team = db.Column(db.String, nullable=False)
    message_cnt = db.Column(db.Integer, default=0)
    is_leader = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    ai_activation = db.Column(db.Boolean, default=False)
