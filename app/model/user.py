from app import db
from datetime import datetime

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nim = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(100), nullable=True)
    # photo_path = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return '<User {}>'.format(self.name)