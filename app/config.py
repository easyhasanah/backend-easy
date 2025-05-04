import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:kelompok2&@192.168.23.50:5432/db_easy_hasanah'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost:5432/db_easy_hasanah'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db_easy_hasanah.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "ewuqpdjsakcnoiwrqojaj"