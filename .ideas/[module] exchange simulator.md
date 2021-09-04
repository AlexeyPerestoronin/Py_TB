# Exchange Simulator Module
This is the module mainly providing the `ExchangeSimulatorI`-interface for simulating an Exchange logic.  
For example:
```py
class ExchangeSimulatorI:
    # ...

    def getNextPrice() -> float:
        """returns the next trade-pair related price each time when called"""
        # ...
    
```
## General tips:
1. All trade-pair data related must be the real data obtained from an Exchange.  
    - This data must be collected inside local BD from which there will to be extracted by request  
2. Since the trading is a real time process there is must to be an feature to accelerate this process in simulating.  
3. Maybe it makes sense to implement a result data collection as a part of this interface