from importlib import import_module
from types import ModuleType

from vnpy.trader.database import (
    DB_TZ,
    convert_tz,
    BarOverview,
    TickOverview,
    BaseDatabase
)

from .setting import SETTINGS


database: BaseDatabase = None


def get_database() -> BaseDatabase:
    """"""
    # Return database object if already inited
    global database
    if database:
        return database

    # Read database related global setting
    database_name: str = SETTINGS["database.name"]
    module_name: str = f"vnpy_{database_name}"

    # Try to import database module
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError:
        print(("Database adapter not found{}, use default DuckDB adpater").format(module_name))
        module: ModuleType = import_module("vnpy_duckdb")

    # Create database object from module
    database = module.Database()
    return database
