from Constants import *
from Instrument import Instrument as Instrumento
from Candle import *
from Broker.Kite import *
from kiteconnect.ticker import *
import time


class Cerebelle:

    def __init__(self, kite):
        self.kite = kite
        self.api_key = kite.api_key
        self.access_token = kite.access_token
        self.feed_source = KiteTicker(self.api_key, self.access_token)
        self.feed_source.on_ticks = self.quote_update
        self.feed_source.on_close = self.on_disconnect
        self.feed_source.on_error = self.on_error
        self.pass_feed = False
        self.__exchanges = {}
        self.__chandlers = {}
        self.start_live_feed()
        while self.feed_source.ws is None:
            pass

    def set_on_order_update(self, on_order_update):
        self.feed_source.on_order_update = on_order_update

    def __add_instrument(self, exchange, symbol):
        inx = self.__validate_instrument(exchange, symbol)
        if inx is not False:
            if exchange not in self.__exchanges.keys():
                self.__exchanges.update({exchange: {}})
            if symbol not in self.__exchanges[exchange].keys():
                tick_size, lot_size = inx['tick_size'], inx['lot_size']
                token = inx['instrument_token']
                new_instrument = Instrumento(exchange, symbol, lot_size, tick_size)
                self.feed_source.subscribe([token])
                self.feed_source.set_mode(self.feed_source.MODE_FULL, [token])
                self.__exchanges[exchange].update({symbol: new_instrument})
                return True
        else:
            return False

    def __validate_instrument(self, exchange, symbol):
        try:
            inx = self.kite.get_instrument(exchange, symbol)
            return inx
        except KeyError:
            return False

    def quote_update(self, ws, quotes):
        if not self.pass_feed:
            return None
        try:
            for quote in quotes:
                token = quote['instrument_token']
                instr = self.kite.instruments_by_token[token]
                exchange = instr['exchange']
                instrument = instr['tradingsymbol']
                inx: Instrumento = self.__exchanges[exchange][instrument]
                inx.quote_update(quote)
        except KeyError:
            pass

    def get_instrument(self, exchange, symbol):
        exchange = exchange.upper()
        symbol = symbol.upper()
        try:
            return self.__exchanges[exchange][symbol]
        except KeyError:
            response = self.__add_instrument(exchange, symbol)
            if response:
                return self.__exchanges[exchange][symbol]
            else:
                return False

    def get_chandler(self, exchange, symbol):
        try:
            return self.__chandlers[exchange][symbol]
        except KeyError:
            if exchange not in self.__chandlers.keys():
                self.__chandlers[exchange] = {}
            instrument = self.get_instrument(exchange, symbol)
            if instrument:
                chandler = Chandler(instrument, self)
                self.__chandlers[exchange].update({symbol: chandler})
                return chandler
            else:
                return False

    def on_disconnect(self, ws, code, reason):
        print("Closed: " + str(datetime.now()))
        print(code)
        print(reason)
        self.start_live_feed()

    def on_error(self, ws, code, reason):
        print("ERROR: " + str(datetime.now()))
        print(code)
        print(reason)

    def start_live_feed(self):
        self.feed_source.connect(threaded=True)

    def pass_live_feed(self):
        self.pass_feed = True


if __name__ == '__main__':
    cb = Cerebelle
    cb.get_instrument("NSE", "TATASTEEL")
