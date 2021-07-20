from kiteconnect.connect import *
from kiteconnect.exceptions import *
from Broker.kite_headless import *
import pandas as pd
import json
from os.path import join, dirname
from Broker.Constants import *


setup_file_path = join(dirname(__file__), 'kite.json')


class Kite:
    default_setup_file = setup_file_path
    exchanges = []

    def __init__(self, init_file=default_setup_file):
        self.init_file = init_file
        self.equity_margin = 0
        self.commodity_margin = 0
        self.kite = None
        self.logged_in = False
        self.api_key = self.read_key_from_settings('api_key')
        self.access_token = self.read_key_from_settings('access_token')
        self.session = self.read_key_from_settings('session')
        if self.access_token is not None and self.api_key is not None:
            try:
                self.kite = KiteConnect(api_key=self.api_key, access_token=self.access_token)
                self.get_balance()
                self.logged_in = True
            except TokenException as te:
                print('Token Exception: [%s]. \nRegenerating Session\n\n' % te)

        if self.logged_in is False:
            self.api_key = self.read_key_from_settings('api_key')
            if self.api_key is None:
                self.api_key = input('What is your app''s API key:  ')
                self.write_key_to_settings('api_key', self.api_key)

            self.api_secret = self.read_key_from_settings('api_secret')
            if self.api_secret is None:
                self.api_secret = input('What is your app''s API secret:  ')
                self.write_key_to_settings('api_secret', self.api_secret)

            self.redirect_uri = self.read_key_from_settings('redirect_uri')
            if self.redirect_uri is None:
                self.redirect_uri = input('What is your app''s redirect_uri:  ')
                self.write_key_to_settings('redirect_uri', self.redirect_uri)

            self.username = self.read_key_from_settings('username')
            if self.username is None:
                self.username = input('What is your account''s username:  ')
                self.write_key_to_settings('username', self.username)

            self.password = self.read_key_from_settings('password')
            if self.password is None:
                self.password = input('What is your account''s password:  ')
                self.write_key_to_settings('password', self.password)

            self.pin = self.read_key_from_settings('pin')
            if self.pin is None:
                self.pin = input('What is your account''s pin:  ')
                self.write_key_to_settings('pin', self.pin)

            self.kite = KiteConnect(self.api_key)
            self.url = self.kite.login_url()

            request_token = get_request_token(self.url, self.username, self.password, self.pin, headless=False)
            self.session = self.kite.generate_session(request_token=request_token, api_secret=self.api_secret)

            try:
                self.access_token = self.session['access_token']
            except SystemError as se:
                print('Uh oh, there seems to be something wrong. Error: [%s]' % se)
                return

            self.session['login_time'] = str(self.session['login_time'])
            self.write_key_to_settings('session', self.session)
            self.write_key_to_settings('access_token', self.access_token)
            self.kite.set_access_token(self.access_token)
        self.instruments = {}
        self.instruments_by_token = {}
        self.get_exchanges()
        self.get_instruments()

    def get_exchanges(self):
        if not len(self.exchanges):
            self.exchanges = list(dict.fromkeys(self.session['exchanges']))
        return self.exchanges

    def get_instruments(self):
        for exchange in ["NSE", "NFO", "BSE"]:
            instruments = self.kite.instruments(exchange)
            exchange_dictionary = {}
            for instr in instruments:
                tradingsymbol = instr['tradingsymbol']
                exchange_dictionary.update({tradingsymbol: instr})
                token = instr['instrument_token']
                self.instruments_by_token.update({token: instr})
            self.instruments.update({exchange: exchange_dictionary})

    def limit_buy(self, exchange, tradingsymbol, price, quantity, product_type=ProductType.DELIVERY):

        if product_type == ProductType.DELIVERY:
            if exchange == Exchange.NFO:
                product_type = ProductType.NRML
            elif exchange == Exchange.NSE:
                product_type = ProductType.CNC
        elif product_type == ProductType.INTRADAY:
            product_type = ProductType.MIS

        return self.kite.place_order(variety=Variety.REGULAR,
                                     exchange=exchange,
                                     tradingsymbol=tradingsymbol,
                                     transaction_type=TransactionType.BUY,
                                     quantity=quantity,
                                     product=product_type,
                                     order_type=OrderType.LIMIT,
                                     price=price)

    def limit_sell(self, exchange, tradingsymbol, price, quantity, product_type=ProductType.DELIVERY):

        if product_type == ProductType.DELIVERY:
            if exchange == Exchange.NFO:
                product_type = ProductType.NRML
            elif exchange == Exchange.NSE:
                product_type = ProductType.CNC
        elif product_type == ProductType.INTRADAY:
            product_type = ProductType.MIS

        return self.kite.place_order(variety=Variety.REGULAR,
                                     exchange=exchange,
                                     tradingsymbol=tradingsymbol,
                                     transaction_type=TransactionType.SELL,
                                     quantity=quantity,
                                     product=product_type,
                                     order_type=OrderType.LIMIT,
                                     price=price)

    def market_buy(self, exchange, tradingsymbol, quantity, product_type=ProductType.DELIVERY):

        if product_type == ProductType.DELIVERY:
            if exchange == Exchange.NFO:
                product_type = ProductType.NRML
            elif exchange == Exchange.NSE:
                product_type = ProductType.CNC
        elif product_type == ProductType.INTRADAY:
            product_type = ProductType.MIS

        return self.kite.place_order(variety=Variety.REGULAR,
                                     exchange=exchange,
                                     tradingsymbol=tradingsymbol,
                                     transaction_type=TransactionType.BUY,
                                     quantity=quantity,
                                     product=product_type,
                                     order_type=OrderType.MARKET)

    def market_sell(self, exchange, tradingsymbol, quantity, product_type=ProductType.DELIVERY):

        if product_type == ProductType.DELIVERY:
            if exchange == Exchange.NFO:
                product_type = ProductType.NRML
            elif exchange == Exchange.NSE:
                product_type = ProductType.CNC
        elif product_type == ProductType.INTRADAY:
            product_type = ProductType.MIS

        return self.kite.place_order(variety=Variety.REGULAR,
                                     exchange=exchange,
                                     tradingsymbol=tradingsymbol,
                                     transaction_type=TransactionType.SELL,
                                     quantity=quantity,
                                     product=product_type,
                                     order_type=OrderType.MARKET)

    def cancel_order(self, order_id):
        return self.kite.cancel_order(variety=Variety.REGULAR, order_id=order_id)

    def modify_order(self, order_id, **kwargs):
        """
        :param order_id:
        :param kwargs:
                     quantity=None,
                     price=None,
                     order_type=None,
                     trigger_price=None,
                     validity=None,
                     disclosed_quantity=None):
        """
        return self.kite.modify_order(variety=Variety.REGULAR, order_id=order_id, **kwargs)

    def write_key_to_settings(self, key, value):
        try:
            file = open(self.init_file, 'r')
        except IOError:
            data = {"api_key": "", "api_secret": "", "redirect_uri": "", "access_token": "", "username": "",
                    "password": "", "pin": ""}
            with open(self.init_file, 'w') as output_file:
                json.dump(data, output_file)
        file = open(self.init_file, 'r')
        try:
            data = json.load(file)
        except Exception:
            data = {}
        data[key] = value
        with open(self.init_file, 'w') as output_file:
            json.dump(data, output_file)

    def read_key_from_settings(self, key):
        try:
            file = open(self.init_file, 'r')
        except IOError:
            file = open(self.init_file, 'w')
        file = open(self.init_file, 'r')
        try:
            data = json.load(file)
            return data[key]
        except Exception:
            pass
        return None

    def get_instrument(self, exchange, tradingsymbol):
        return self.instruments[exchange][tradingsymbol]

    def get_balance(self):
        margins = self.kite.margins()
        self.equity_margin = margins[EQUITY]['net']
        self.commodity_margin = margins[COMMODITY]['net']
        return margins

    def get_positions(self):
        return self.kite.positions()

    def get_holdings(self):
        return self.kite.holdings()

    def get_profile(self):
        return self.kite.profile()

    def get_trade_book(self):
        return self.kite.trades()

    def get_order_details(self, order_id):
        return self.kite.order_history(order_id)

    def get_order_trades(self, order_id):
        return self.kite.order_history(order_id)

    @staticmethod
    def get_symbol(contract_name):
        year = datetime.now().strftime("%y")
        yearplus = str(int(year) + 1)
        if year in contract_name:
            return contract_name[:contract_name.find(year)]
        elif yearplus in contract_name:
            return contract_name[:contract_name.find(yearplus)]

    @staticmethod
    def get_year_month(contract_name):
        return contract_name[-8:-3]

    @staticmethod
    def symbol_parse(tradingsymbol):
        if tradingsymbol.upper() in ['NIFTY 50', 'NIFTY_50', 'NIFTY50']:
            return 'NIFTY'
        elif tradingsymbol.upper() in ['NIFTY_BANK', 'NIFTY BANK', 'BANK_NIFTY', 'BANK NIFTY', 'NIFTYBANK']:
            return "BANKNIFTY"
        else:
            return tradingsymbol

    def search(self, exchange, regx):
        df = pd.DataFrame(self.instruments[exchange].values())
        df = df[df.tradingsymbol.str.contains(regx)]
        return df

    def ordered_months(self, as_dict=False):
        contracts = self.search(Exchange.NFO, "FUT").tradingsymbol
        year_month_list = []
        dates = []

        for sym in contracts:
            year_month = self.get_year_month(sym)
            if year_month not in year_month_list:
                year_month_list.append(year_month)
        for each in year_month_list:
            dates.append(datetime.strptime(each, yb).strftime(ym) + " " + each)

        current = dates.pop(dates.index(min(dates)))[-5:].upper()
        far = dates.pop(dates.index(max(dates)))[-5:].upper()
        near = dates.pop(0)[-5:].upper()
        if as_dict:
            return {CURRENT: current, NEAR: near, FAR: far}
        else:
            return current, near, far

    def get_option_chain(self, tradingsymbol, year_month=CURRENT):
        year_month = self.ordered_months(as_dict=True)[year_month]
        if tradingsymbol.find(year_month) != -1:
            tradingsymbol = tradingsymbol[:tradingsymbol.index(year_month)]
        tradingsymbol = self.symbol_parse(tradingsymbol)
        df: pd.DataFrame = self.search(Exchange.NFO, tradingsymbol)
        df = df[(df.tradingsymbol.str.contains(year_month)) & (df.instrument_type == PE) & (df.name == tradingsymbol)]
        return df.strike.astype(float).sort_values()

    def get_nearest_call_option(self, tradingsymbol, price, year_month=CURRENT):
        year_month = self.ordered_months(as_dict=True)[year_month]
        if tradingsymbol.find(year_month) != -1:
            tradingsymbol = tradingsymbol[:tradingsymbol.index(year_month)]
        tradingsymbol = self.symbol_parse(tradingsymbol)
        df: pd.DataFrame = self.search(Exchange.NFO, tradingsymbol)
        df = df[(df.tradingsymbol.str.contains(year_month)) & (df.instrument_type == CE) & (df.name == tradingsymbol)]
        chain = df.strike.astype(float).sort_values()
        try:
            call_option_strike_price = float(chain[chain > price].values[0])
        except IndexError:
            return False
        call_option_instrument = df[df.strike == call_option_strike_price].tradingsymbol.item()
        return call_option_instrument

    def get_nearest_put_option(self, tradingsymbol, price, year_month=CURRENT):
        year_month = self.ordered_months(as_dict=True)[year_month]
        if tradingsymbol.find(year_month) != -1:
            tradingsymbol = tradingsymbol[:tradingsymbol.index(year_month)]
        tradingsymbol = self.symbol_parse(tradingsymbol)
        df: pd.DataFrame = self.search(Exchange.NFO, tradingsymbol)
        df = df[(df.tradingsymbol.str.contains(year_month)) & (df.instrument_type == PE) & (df.name == tradingsymbol)]
        chain = df.strike.astype(float).sort_values()
        try:
            put_option_strike_price = float(chain[chain < price].values[-1])
        except IndexError:
            return False
        put_option_instrument = df[df.strike == put_option_strike_price].tradingsymbol.item()
        return put_option_instrument

    def get_current_future(self, tradingsymbol):
        tradingsymbol = self.symbol_parse(tradingsymbol)
        current, _, _ = self.ordered_months()
        future_instrument = tradingsymbol + current + "FUT"
        return future_instrument

    # def get_historical_data(self, exchange, tradingsymbol, from_date, to_date, interval, parse_time=False):
    #     instrument = self.get_instrument(exchange, tradingsymbol)
    #     if parse_time:
    #         from_date = datetime.strptime(from_date, date_format)
    #         to_date = datetime.strptime(to_date, date_format)
    #     return self.upstox_object.get_ohlc(instrument, interval, from_date, to_date)


if __name__ == '__main__':
    k = Kite()
