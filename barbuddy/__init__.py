import os

from flask import Flask

#from . import login

app = Flask(__name__)
config_path = os.environ.get("CONFIG_PATH", "barbuddy.config.DevelopmentConfig")
app.config.from_object(config_path)

from . import api

from .database import Base, engine
Base.metadata.create_all(engine)

