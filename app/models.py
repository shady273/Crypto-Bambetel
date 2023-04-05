from app import db


class AllCoins(db.Model):
    __tablename__ = 'all_coins'
    __table_args__ = {'extend_existing': True}
    rating = db.Column(db.Integer, primary_key=True)
    id_coin = db.Column(db.String, unique=True)
    symbol = db.Column(db.String)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    high_24h = db.Column(db.Float)
    low_24h = db.Column(db.Float)
    ath = db.Column(db.Float)
    ath_change_percentage = db.Column(db.Float)
    max_supply = db.Column(db.Float)
    circulating_supply = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    usd_1h_change = db.Column(db.Float)
    usd_24h_change = db.Column(db.Float)
    usd_7d_change = db.Column(db.Float)
    usd_30d_change = db.Column(db.Float)
    usd_1y_change = db.Column(db.Float)
    price_list = db.Column(db.Text)
    date_list = db.Column(db.Text)
    pr = db.relationship("Profiles", backref="all_coins", uselist=False)


class Profiles(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String, db.ForeignKey('all_coins.id_coin'), unique=True)
    market_cap = db.Column(db.Integer)
    img_large = db.Column(db.String)
    img_small = db.Column(db.String)
    img_thumb = db.Column(db.String)
    homepage = db.Column(db.String)


class Exchanges(db.Model):
    __tablename__ = 'exchanges'
    id = db.Column(db.Integer, primary_key=True)
    id_exch = db.Column(db.String, unique=True)
    name = db.Column(db.String, unique=True)
    year_established = db.Column(db.Integer)
    country = db.Column(db.String)
    url = db.Column(db.String)
    image = db.Column(db.String)
    trust_score_rank = db.Column(db.Integer)
    trade_volume_24h_btc = db.Column(db.Integer)


class TradingPairs(db.Model):
    __tablename__ = 'trading_pairs'
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String, db.ForeignKey('all_coins.id_coin', name='trading_pairs_coin_id_fkey'))
    exch_id = db.Column(db.String, db.ForeignKey('exchanges.id_exch', name='trading_pairs_exch_id_fkey'))
    base = db.Column(db.String)
    target = db.Column(db.String)
    volume = db.Column(db.Integer)
    trade_url = db.Column(db.String)
    ex = db.relationship("Exchanges", backref="trading_pairs", uselist=False)
