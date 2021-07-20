from threading import *


class Sprite:
    def __init__(self, instrument, origin):
        self.instrument = instrument
        self.origin: Grid = origin
        self.exchange = self.instrument.exchange
        self.symbol = self.instrument.symbol
        self.instrument.create_sprite(self)
        self.new_quote_flag = Event()
        self.quote = 0
        self.thread = Thread(target=self.feed, daemon=True)

    def quote_update(self, quote):
        self.quote = quote
        self.new_quote_flag.set()

    def feed(self):
        while self.new_quote_flag.wait():
            self.new_quote_flag.clear()

    def kill(self):
        self.instrument.kill_sprite(self)

    @staticmethod
    def get_ltp(quote):
        return quote['last_price']

    @staticmethod
    def get_timestamp(quote):
        return quote['timestamp']

    @staticmethod
    def get_volume(quote):
        return quote['volume']

    @staticmethod
    def get_oi(quote):
        return quote['oi']

# class PriceAbove(Sprite):
#     def __init__(self, instrument, origin, id, price, event_handler):
#         super().__init__(instrument, origin)
#         self.price = price
#         self.event_handler = event_handler
#         self.id = id
#
#     def feed(self, quote):
#         quote = float(quote['ltp'])
#         if quote > self.price:
#             self.event_handler(self.id)
#             self.kill()
#
#
# class PriceAboveOrEqual(Sprite):
#     def __init__(self, instrument, origin, id, price, event_handler):
#         super().__init__(instrument, origin)
#         self.price = price
#         self.event_handler = event_handler
#         self.id = id
#
#     def feed(self, quote):
#         quote = float(quote['ltp'])
#         if quote >= self.price:
#             self.event_handler(self.id)
#             self.kill()
#
#
# class PriceBelow(Sprite):
#     def __init__(self, instrument, origin, id, price, event_handler):
#         super().__init__(instrument, origin)
#         self.price = price
#         self.event_handler = event_handler
#         self.id = id
#
#     def feed(self, quote):
#         quote = float(quote['ltp'])
#         if quote < self.price:
#             self.event_handler(self.id)
#             self.kill()
#
#
# class PriceBelowOrEqual(Sprite):
#     def __init__(self, instrument, origin, id, price, event_handler):
#         super().__init__(instrument, origin)
#         self.price = price
#         self.event_handler = event_handler
#         self.id = id
#
#     def feed(self, quote):
#         quote = float(quote['ltp'])
#         if quote <= self.price:
#             self.event_handler(self.id)
#             self.kill()