from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pycoingecko import CoinGeckoAPI
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bambetel.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cg = CoinGeckoAPI()
scheduler = BackgroundScheduler()


def format_number(value):
    return "{:,}".format(value)


app.jinja_env.filters['format_number'] = format_number
app.jinja_env.globals.update(zip=zip)

from app import views
from app import admin_views
from app import coin_database
