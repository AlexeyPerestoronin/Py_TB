# Exchange Module
This is the module mainly providing `ExchangeI`-interfaces fot really business interactions with an Online Exchange Platform.
Example:
```py
class ExchangeI:
    # ...
```

There are many ways to realize this interface:

## 1. Simply implementation based on `ExchangeI` and `CommandI` interfaces
This implementation implies one method inside interface for to all api-commands
```py
class ExchangeI:
    """general interface for interaction with an Exchange Platform"""

    def interactWith(
        i_command : CommandI, # target api-command
    ) -> json:
    """executes one api-command on the Exchange and returns result of it"""
    return tryToExecute(
        10, # attempts quantity for to the command execution
        lambda: i_command.tryToInteract(), # target execution command
        i_command.BAD_ANSWERS) # list of errors which allows to try to execute command again

class CommandI:
    """general interface for an api-command to interactions with an Exchange Platform"""

    # list of errors which allows to try to execute command again
    BAD_ANSWERS = [ ... ]

    def tryToInteract() -> json:
        # ...

```
NOTES:
1. It is looks good to realize all constraints and other important things for each command as once uploaded setting file:
```txt
set_buy_order.yaml - all settings for buy-order
...
set_sell_order.yaml - all settings for sell-order
```