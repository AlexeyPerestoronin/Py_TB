# Data Base Module
This is the module intended to save any information inside an data base and based on three interfaces: CommandI, TableI and DataBaseI
***

## Implementation Idea in general case
General notes (step by step):
1. Some file with settings must exist, for example `bd_settings.json`
```json
{
    "Tables" : [
        {
            "descriptions": "this is the table for collecting history of performed operations via any Exchange API",
            "name": "Operations",
            "commands":
            [
                {
                    "descriptions": "creates target table",
                    "name": "create",
                    "SQL": "CREATE TABLE Operations (TEXT time, TEXT name, TEXT result)"
                },
                {
                    "descriptions": "insert in table new data",
                    "name": "insert",
                    "SQL": "INSERT INTO Operations (time, name, result) VALUES (?1, ?2, ?3)"
                }
            ]
        }
    ]
}
```

2. This is the class collected enum-values about statuses of operations from BD
```py
class Statuses:
    C = "CREATED"
    I = "INSERTED"
    U = "UPDATED"
    D = "DELETED"
```

3. This is the interface performed some command in BD
```py
class CommandI:
    def __call__(self, data: list) -> Statuses:
        pass
```

3. This is the interface managed the commands for target table in BD
```py
class TableI:
    def __getitem__(self, command_name: str) -> Command:
            pass
```

4. This is the interface managed the tables for target BD
```py
class DataBaseI:
    def __getitem__(self, table_name: str) -> Table:
            pass
```

5. This is the function returns existent of creates new instance of BD by its name and path
```py
def getDB(name: str, path: str = None) -> DataBaseI:
    pass
```

How it should be used:
```py
statistics = getDB("Statistics")
statistics["commands"]["create"]()
statistics["commands"]["insert"]([["XX.XX.XXXX", "open-order", "success"], ["YY.YY.YYYY", "close-order", "success"]])
```

### NoSQL Specialization for the dictionary
This is the especial realization of CommandI interface for to save any dict-object directly.
***
There are set of examples are describing for what this specialization intends (step by step):
1. Example of the target table structure in the **settings.json**
```json
{
    "Tables" : [
        // others tables
        {
            "descriptions": "this is the table imitated NoSQL DB for saving any dict-objects",
            "features": ["NoSQL"],
            "name": "TradeHistory",
            "commands":
            [
                {
                    "descriptions": "creates target table",
                    "name": "create",
                    "SQL": "CREATE TABLE Operations (
                    INTEGER ID UNIQUE PRIMARY KEY,
                    INTEGER Parent-ID FOREIGN KEY (ID),
                    TEXT    K-Type,
                    TEXT    K-Value,
                    TEXT    V-Type,
                    TEXT    V-Value);"
                },
                {
                    "descriptions": "insert in table new data",
                    "name": "insert",
                    "SQL": "INSERT INTO Operations (ID, Parent-ID, K-Type, K-Value, V-Type, V-Value)
                    VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
                }
            ]
        }
    ]
}
```
2. Let this is a dict-object in python-code
```py
result = {
    'status': 'success',
    'details': {
        'order type': 'sale',
        'trade pair': 'BTC-USD',
        'quantity': 0.11,
        'price': 21000,
        'commission': {
            'BTC': 0.0005,
            'USD': 0.0
        },
        'times' : [
            '13:00',
            '13:01',
            '13:02',
            '13:03'
        ]
    }
}
```
3. Then in any place will try to save above dict-object in our table
```py
statistics = getDB("TradeHistory")
statistics["commands"]["insert"](result)
```
4. After this operation will be completed, we will see next content in the TradeHistory-table  

| ID | Parent-ID | K-Type | K-Value       | V-Type  | V-Value
| -- | --------- | ------ | ------------- | ------- | -------
| 1  | NULL      | NULL   | NULL          | 'dict'  | '2,3'
| 2  | 1         | str    | 'status'      | 'str'   | 'success'
| 3  | 1         | str    | 'details'     | 'dict'  | '4,5,6,7'
| 4  | 3         | str    | 'order type'  | 'str'   | 'sale'
| 5  | 3         | str    | 'trade pair'  | 'str'   | 'BTC-USD'
| 6  | 3         | str    | 'quantity'    | 'float' | '0.11'
| 7  | 3         | str    | 'price'       | 'float' | '21000'
| 8  | 3         | str    | 'commission'  | 'dict'  | '9,10'
| 9  | 8         | str    | 'BTC'         | 'float' | '0.0005'
| 10 | 8         | str    | 'USD'         | 'float' | '0.0'
| 11 | 3         | str    | 'times'       | 'list'  | '12,13,14,15'
| 12 | 11        | NULL   | NULL          | 'str'   | '13:00'
| 13 | 11        | NULL   | NULL          | 'str'   | '13:01'
| 14 | 11        | NULL   | NULL          | 'str'   | '13:02'
| 15 | 11        | NULL   | NULL          | 'str'   | '13:03'

Technical notes:
* recursion technic will help realizing serializations/deserializations process to/from dict-object/data-base
* maybe it will be better to preserve V-Value for dict|list-types in another table (but this approach more difficult in realization)