from datetime import datetime

START = datetime.now().time().replace(hour=0, minute=0, second=0)
MARKET_OPEN_TIME = datetime.now().time().replace(hour=9, minute=14, second=59)
MARKET_CLOSE_TIME = datetime.now().time().replace(hour=23, minute=59, second=59)

date_format = '%Y-%m-%d'
time_format = '%H:%M:%S'
datetime_format = '%Y-%m-%d %H:%M:%S'
yb = "%y%b"
ym = "%y%m"

CURRENT = "current"
NEAR = "NEAR"
FAR = "FAR"

LONG = 'LONG'
SHORT = 'SHORT'
BUY = 'BUY'
SELL = 'SELL'

CE = "CE"
PE = "PE"

EQUITY = "equity"
COMMODITY = "commodity"


class CustomEnum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __setattr__(self, name, value):
        raise RuntimeError('Cannot override values')

    def __delattr__(self, name):
        raise RuntimeError('Cannot delete values')


class OrderStatus(CustomEnum):
    OPEN = "OPEN"
    UPDATE = "UPDATE"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ProductType(CustomEnum):
    DELIVERY = 'DELIVERY'
    INTRADAY = 'INTRADAY'
    MIS = "MIS"
    CNC = "CNC"
    NRML = "NRML"
    CO = "CO"
    BO = "BO"


class OrderType(CustomEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SLM = "SL-M"
    SL = "SL"


class Variety(CustomEnum):
    REGULAR = "regular"
    BO = "bo"
    CO = "co"
    AMO = "amo"


class TransactionType(CustomEnum):
    BUY = "BUY"
    SELL = "SELL"


class Validity(CustomEnum):
    DAY = "DAY"
    IOC = "IOC"


class Exchange(CustomEnum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"
    CDS = "CDS"
    BFO = "BFO"
    MCX = "MCX"


class Segment(CustomEnum):
    NFO_OPT = "NFO-OPT"
    NFO_FUT = "NFO-FUT"
    NSE = "NSE"


class InstrumentType:
    EQ = "EQ"
    CE = "CE"
    PE = "PE"
    FUT = "FUT"
