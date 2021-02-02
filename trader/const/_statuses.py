# brief: class for presents all statuses for trading
class Status:
    # brief: class for presents all traders' statuses
    class Trader:
        VOID = "void"
        DURING = "during"
        FINISHED = "finished"

    # brief: class for present all a strategies' statuses
    class Strategy:
        VOID = "void"
        INIT = "init"
        TRADE = "trade"
        WAIT = "wait"
        COMPLETE = "complete"

    # brief: class for present all a orders' statuses
    class Order:
        WAIT = "wait"
        DEAL = "deal"
        CANCEL = "cancel"
