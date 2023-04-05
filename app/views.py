import pprint
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy import asc, desc, or_
from app import app, db
from app.models import AllCoins, Profiles, Exchanges, TradingPairs
from flask import render_template, request, Response, jsonify, json
from datetime import datetime


@app.route("/")
def index():
    with app.app_context():
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 20
        all_coins_data = db.session.query(AllCoins, Profiles). \
            join(Profiles, AllCoins.id_coin == Profiles.coin_id). \
            order_by(asc(AllCoins.rating)). \
            paginate(page=page, per_page=per_page)

        pagination = Pagination(page=page, total=all_coins_data.total, per_page=per_page,
                                css_framework='bootstrap4', format_current=' ')

    return render_template("index.html", title="Bambetel", all_coins_data=all_coins_data, pagination=pagination)


@app.route("/exchanges")
def exchanges():
    with app.app_context():
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 20
        all_exchanges = db.session.query(Exchanges). \
            order_by(asc(Exchanges.id)). \
            paginate(page=page, per_page=per_page)

        pagination = Pagination(page=page, total=all_exchanges.total, per_page=per_page, css_framework='bootstrap4')

    return render_template("exchanges.html", title="Exchanges", all_exchanges=all_exchanges, pagination=pagination)


@app.route("/<alias>")
def coin(alias):
    with app.app_context():
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10

        coin = db.session.query(AllCoins).filter_by(id_coin=alias).one()
        profile = db.session.query(Profiles).filter_by(coin_id=alias).one()
        traid_pair = db.session.query(Exchanges.name, Exchanges.url, Exchanges.image, TradingPairs.base,
                                      TradingPairs.target, TradingPairs.volume,
                                      TradingPairs.trade_url). \
            join(TradingPairs, Exchanges.id_exch == TradingPairs.exch_id). \
            filter(TradingPairs.coin_id == alias). \
            order_by(Exchanges.id). \
            paginate(page=page, per_page=per_page, error_out=False)

        price_list = db.session.query(AllCoins.price_list).filter_by(id_coin=alias).one()
        date_list = db.session.query(AllCoins.date_list).filter_by(id_coin=alias).one()
        json_price = json.loads(price_list[0])
        json_date = json.loads(date_list[0])

        data = [{'x': json_date, 'y': json_price, 'type': 'line', 'name': coin.name}]
        pagination = Pagination(page=page, total=traid_pair.total, per_page=per_page, css_framework='bootstrap4')

        return render_template('coin.html', coin=coin, profile=profile, db_result=traid_pair, data=data,
                               pagination=pagination)


@app.route('/coins/<coin_id>/schedule')
def get_schedule(coin_id):
    coin = AllCoins.query.filter_by(id_coin=coin_id).first()
    return Response(coin.schedule, mimetype='image/png')


@app.route('/search_coins')
def search_coins():
    search_query = request.args.get('q')
    # знайти всі монети, які містять рядок search_query у назві або символі
    coins = AllCoins.query.filter(
        or_(AllCoins.name.ilike(f'%{search_query}%'), AllCoins.symbol.ilike(f'%{search_query}%'))).all()
    # створити список монет у форматі JSON
    coin_list = [{'id_coin': coin.id_coin, 'name': coin.name, 'symbol': coin.symbol} for coin in coins]
    # повернути список монет у форматі JSON
    return jsonify(coin_list)
