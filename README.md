# What is it?
Module with basic functionality to work with SQLite3.

# Installation
```cmd
pip install --upgrade sqlite3w
```

# Example
```python
import sqlite3worker

db = sqlite3worker.SQLite3Worker("main.sqlite3") # "FILEPATH" | ":memory:"

db.create_table(
    "users",
    {
        "id": (int, True), # "id": (int, True) -> "COLON_NAME": (PYTHON_TYPE, IS_PRIMARY_KEY)
        "nick": (str, False),
        "desc": (str, False),
        "birthday": (float, False)
    }
)

db.add_data(
    "users",
    [0, "Roman", "...", 1]
)
```
