import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost:5432/db_easy_hasanah'
    SQLALCHEMY_TRACK_MODIFICATIONS = False