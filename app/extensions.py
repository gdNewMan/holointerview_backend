from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

class SessionData(db.Model):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    data = Column(Text, nullable=False)
    expiry = Column(DateTime, nullable=False)

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
