import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql://test_user:test_user@119.67.85.26/PROJECT'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    model_name = 'ft:gpt-3.5-turbo-0125:personal::9SqEUNiZ'
    api_key = os.getenv('OPENAI_API_KEY')