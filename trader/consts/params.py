from common import CONSTANT as C
from common import CREATE_CONSTANT as CC

# brief: class collects all key-values for access to fields in launch-parameters
class SETTINGS(metaclass=C("PARAMS")):
    PUBLIC_KEY = CC("PUBLIC_KEY")
    SECRET_KEY = CC("SECRET_KEY")
    TAKER_COMMISSION_PROMOTION = CC("TAKER_COMMISSION_PROMOTION")
    MAKER_COMMISSION_PROMOTION = CC("MAKER_COMMISSION_PROMOTION")
    class TRADING(metaclass=C("TRADING")):
        PAIR = CC("PAIR")
        INIT_COST = CC("INIT_COST")
        DB_FILENAME = CC("DB_FILENAME")
        SAVE_CATALOG = CC("SAVE_CATALOG")
        class COMPLETED_POLICY(metaclass=C("COMPLETED_POLICY")):
            ID = CC("ID")
            PARAMS = CC("PARAMS")
        class STRATEGY(metaclass=C("STRATEGY")):
            ID = CC("ID")
            PARAMS = CC("PARAMS")
