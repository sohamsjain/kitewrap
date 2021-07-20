from threading import *


class Instrument:
    def __init__(self, exchange, symbol, lot_size, tick_size):
        self.exchange: str = exchange.upper()
        self.symbol: str = symbol.upper()
        self.lot_size: int = int(lot_size) if type(lot_size) in [int, float, str] else 0
        self.tick_size: float = float(tick_size) if type(lot_size) in [int, float, str] else 50
        self.quote = 0
        self.new_quote_flag = Event()
        self.__sprites = []
        self.inx_thread = Thread(name=self.symbol, target=self.feed, daemon=True).start()

    def create_sprite(self, new_sprite):
        self.__sprites.append(new_sprite)

    def kill_sprite(self, to_kill):
        if to_kill in self.__sprites:
            self.__sprites.remove(to_kill)

    def quote_update(self, quote):
        # print(quote)  # comment out
        self.quote = quote
        self.new_quote_flag.set()

    def feed(self):
        while self.new_quote_flag.wait():
            self.new_quote_flag.clear()
            for sprite in self.__sprites:
                sprite.quote_update(self.quote)
