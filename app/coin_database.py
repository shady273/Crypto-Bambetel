import io
import pprint
import sqlite3
import time
from datetime import datetime
import plotly.graph_objs as go
import numpy as np
from flask import json
from sqlalchemy import asc, desc, or_
from app import db, cg, app
from app.models import AllCoins, Profiles, Exchanges, TradingPairs
import matplotlib.pyplot as plt


def coin_data():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        profiles = db.session.query(Profiles).all()
        id_coin_list = [coin.coin_id for coin in profiles]
        for coin in all_coins_data:
            if coin.id_coin in id_coin_list:
                print("already in the table")
            else:
                try:
                    info_coin = cg.get_coin_by_id(coin.id_coin)
                    print(f"{coin.id_coin} proces")
                    pr = Profiles(coin_id=coin.id_coin, market_cap=info_coin['market_data']['market_cap']['usd'],
                                  img_large=info_coin['image']['large'],
                                  img_small=info_coin['image']['small'],
                                  img_thumb=info_coin['image']['thumb'],
                                  homepage=info_coin['links']['homepage'][0])
                    db.session.add(pr)
                    db.session.commit()
                    print(f"{coin.id_coin} add")
                except Exception as e:
                    print(e)


# removes unrated cryptocurrencies
def delete_wtht_rtng():
    with app.app_context():
        coins_to_delete = AllCoins.query.filter(or_(AllCoins.high_24h == None)).all()
        for coin in coins_to_delete:
            db.session.delete(coin)

        db.session.commit()


# rating CG update
def update_rtng():
    id_list = []
    with app.app_context():
        id_list = AllCoins.query.all()
        for coin in id_list:
            try:
                info_coin = cg.get_coin_by_id(coin.id_coin)
                print(f"{coin.id_coin} new cg_rank {info_coin['market_data']['market_cap']['usd']}")
                db.session.query(Profiles).filter_by \
                    (coin_id=coin.id_coin).update({Profiles.cg_rank: info_coin['market_data']['market_cap']['usd']})

                db.session.commit()
            except Exception as e:
                print(e)


# оновлення рейтингу монет за капіталізацією
def updata_rating():
    with app.app_context():
        profiles_sorted = AllCoins.query.order_by(AllCoins.market_cap.desc()).all()
        i = 0
        for profile in profiles_sorted:
            print(f'old_id={profile.rating}-{profile.id_coin}')
            i += 1
            print(f'new_id={i}')
            db.session.query(AllCoins).filter_by(id_coin=profile.id_coin).update({'rating': i})
            db.session.flush()
        db.session.commit()


# udate price and market cap
def updata_price():
    with app.app_context():
        all_data = []
        page = 1
        while len(all_data) < 930:
            data = cg.get_coins_markets(order='market_cap_desc', page=page, per_page=250, vs_currency='usd',
                                        price_change_percentage='1h,24h,7d,30d,1y', locale='en')
            all_data.extend(data)
            page += 1

        for coin in all_data:
            db.session.query(AllCoins).filter_by(id_coin=coin['id']).update({
                'price': coin['current_price'],
                'high_24h': coin['high_24h'],
                'low_24h': coin['low_24h'],
                'ath': coin['ath'],
                'ath_change_percentage': coin['ath_change_percentage'],
                'max_supply': coin['max_supply'] if coin['max_supply'] is not None else 0,
                'circulating_supply': coin['circulating_supply'],
                'market_cap': coin['market_cap'],
                'usd_1h_change': coin['price_change_percentage_1h_in_currency']
                if coin['price_change_percentage_1h_in_currency'] is not None else 0,
                'usd_24h_change': coin['price_change_percentage_24h_in_currency']
                if coin['price_change_percentage_24h_in_currency'] is not None else 0,
                'usd_7d_change': coin['price_change_percentage_7d_in_currency']
                if coin['price_change_percentage_7d_in_currency'] is not None else 0,
                'usd_30d_change': coin['price_change_percentage_30d_in_currency']
                if coin['price_change_percentage_30d_in_currency'] is not None else 0,
                'usd_1y_change': coin['price_change_percentage_1y_in_currency']
                if coin['price_change_percentage_1y_in_currency'] is not None else 0})
            db.session.commit()
        print(f"Coins data update")


# Delete coin withaout coin price
def delete_coin_wpr():
    with app.app_context():
        subq = db.session.query(AllCoins.id_coin).order_by(AllCoins.rating).offset(1000).subquery()
        db.session.query(AllCoins).filter(~AllCoins.id_coin.in_(subq)).delete()
        db.session.commit()


def exchanges_data():
    with app.app_context():
        try:
            markets_list = cg.get_exchanges_list()
            for item in markets_list:
                ex = Exchanges(id_exch=item['id'],
                               name=item['name'],
                               year_established=item['year_established'],
                               country=item['country'],
                               url=item['url'],
                               image=item['image'],
                               trust_score_rank=item['trust_score_rank'],
                               trade_volume_24h_btc=item['trade_volume_24h_btc'])
                db.session.add(ex)
                db.session.commit()
            print("exchanges add")
        except Exception as e:
            print(e)


def coin_exchange():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        for coin in all_coins_data:
            pair_data = cg.get_coin_by_id(coin.id_coin)
            for data in pair_data['tickers']:
                coin_ex = TradingPairs(
                    coin_id=data['coin_id'],
                    exch_id=data['market']['identifier'],
                    base=data['base'],
                    target=data['target'],
                    volume=data['volume'],
                    trade_url=data['trade_url'],
                )
                db.session.add(coin_ex)
                db.session.commit()
                print("exchang pair add")
        print("all add")


def schedule():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        for coin in all_coins_data:
            try:
                bitcoin_data = cg.get_coin_market_chart_by_id(id=coin.id_coin, vs_currency='usd', days=30)

                # Розбити дані на окремі списки з датами і цінами
                dates = [datetime.fromtimestamp(data[0] / 1000) for data in bitcoin_data['prices']]
                prices = [data[1] for data in bitcoin_data['prices']]

                # Побудувати графік
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(dates, prices)
                ax.set_xlabel('Date')
                ax.set_ylabel('Price (USD)')
                ax.set_title(f'{coin.name} price for the last 30 days')
                # Зберегти зображення в байтовий рядок
                img_data = io.BytesIO()
                fig.savefig(img_data, format='png')
                img_data.seek(0)
                plt.close()
                # Зберегти зображення у базу даних
                binary = sqlite3.Binary(img_data.read())
                db.session.query(AllCoins).filter_by(id_coin=coin.id_coin).update(
                    {'schedule': binary})
                db.session.commit()
                print(f'{coin.name} schedule add')
                time.sleep(30)
            except Exception as e:
                print(e)


def interactive_schedule():
    with app.app_context():
        price_list = db.session.query(AllCoins.price_list).filter_by(id_coin='bitcoin').one()
        date_list = db.session.query(AllCoins.date_list).filter_by(id_coin='bitcoin').one()
        json_price = json.loads(price_list[0])
        json_date = json.loads(date_list[0])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=json_date, y=json_price, mode='lines', name='BTC'))
        fig.update_layout(title='Bitcoin price chart', xaxis_title='Date', yaxis_title='USD')

        fig.show()


# збір данних для побудови графіку
def add_plist():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        now = datetime.now()
        for coin in all_coins_data:
            price_list = db.session.query(AllCoins.price_list).filter_by(id_coin=coin.id_coin).one()
            date_list = db.session.query(AllCoins.date_list).filter_by(id_coin=coin.id_coin).one()
            json_price = json.loads(price_list[0])
            json_date = json.loads(date_list[0])
            json_price.append(coin.price)
            json_date.append(now)
            db.session.query(AllCoins).filter_by(id_coin=coin.id_coin).update(
                {"price_list": json.dumps(json_price[-504:]), "date_list": json.dumps(json_date[-504:])})
            db.session.commit()

        print('add_plist Done')


def add_price_list():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        for coin in all_coins_data:
            now = datetime.now()
            print(coin.price, now)
            db.session.query(AllCoins).filter_by(id_coin=coin.id_coin).update(
                {"price_list": json.dumps([coin.price]), "date_list": json.dumps([now])})
        db.session.commit()
        print('Done')


def del_plist():
    with app.app_context():
        all_coins_data = db.session.query(AllCoins).order_by(asc(AllCoins.rating)).all()
        now = datetime.now()
        for coin in all_coins_data:
            price_list = db.session.query(AllCoins.price_list).filter_by(id_coin=coin.id_coin).all()
            date_list = db.session.query(AllCoins.date_list).filter_by(id_coin=coin.id_coin).all()
            json_price = json.loads(price_list[0][0])
            json_date = json.loads(date_list[0][0])

            db.session.query(AllCoins).filter_by(id_coin=coin.id_coin).update(
                {"price_list": json.dumps(json_price[-504:]), "date_list": json.dumps(json_date[-504:])})
            db.session.commit()

        print('del_plist Done')


def del_data():
    with app.app_context():
        db.session.query(AllCoins).filter(AllCoins.rating > 1010).delete()

        db.session.commit()


def synchronize_prof_allcoin():
    with app.app_context():
        id_coin_list = [row.id_coin for row in AllCoins.query.all()]

        Profiles.query.filter(~Profiles.coin_id.in_(id_coin_list)).delete(synchronize_session=False)
        db.session.commit()
