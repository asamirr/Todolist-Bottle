import sqlite3

import db


def connect(database=":memory:", script="todo.sql"):
    """ Open a connection to an SQLite database.
    :param database: full path plus database file name,
                     use :memory: for in-memory database
    :param script: SQL commands to create the database 
                    if it does not exist (like with :memory:)
    :return: None
    :raises: PermissionError - no read and/or write access
             DatabaseError - not a valid SQLite database
    """
    is_new_database = False

    if database == ":memory:":
        is_new_database = True
    else:
        try:
            with open(database, mode="r+"):
                pass
        except FileNotFoundError:
            is_new_database = True
            connection = sqlite3.connect(database)
            connection.close()

    db.connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    db.connection.row_factory = sqlite3.Row
    db.connection.execute("pragma foreign_keys = ON")
    db.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")

    if is_new_database:
        with open(script, "r") as file:
            db.connection.executescript(file.read())
            