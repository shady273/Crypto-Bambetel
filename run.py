from app import app, scheduler
from app.coin_database import updata_price, add_plist, updata_rating

scheduler.add_job(updata_price, 'cron', minute='10,30,50')
scheduler.add_job(add_plist, 'cron', minute='15,35,55')
scheduler.add_job(updata_rating, 'cron', hour='1')


scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
