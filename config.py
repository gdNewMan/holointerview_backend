import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql://root:whehdgus0!@localhost/holo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SECURE = False,  # 개발 환경에서는 False로 설정, 배포 환경에서는 True로 설정
    SESSION_TYPE = 'filesystem'
     # 필요에 따라 filesystem 또는 다른 저장소 설정

