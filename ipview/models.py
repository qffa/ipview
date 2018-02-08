from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Site(Base):
    __tablename__ = 'site'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(32), unique=True, index=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<site: {}>'.format(self.name)



