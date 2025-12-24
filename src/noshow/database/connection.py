import logging
import os
from typing import Optional

from sqlalchemy import Engine, create_engine, func, text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

logger = logging.getLogger(__name__)


def get_connection_string(
    db_user: str | None = None,
    db_passwd: str | None = None,
    db_host: str | None = None,
    db_port: str | None = None,
    db_database: str | None = None,
) -> tuple[str, Optional[dict]]:
    """Construct the connection string for the database.

    This function retrieves database connection details from environment variables
    or uses the provided parameters to construct the connection string.

    Parameters
    ----------
    db_user : str, optional
        Username of the service account. Defaults to the value of the "DB_USER"
        environment variable.
    db_passwd : str, optional
        Password of the service account. Defaults to the value of the "DB_PASSWD"
        environment variable.
    db_host : str, optional
        Host of the database. Defaults to the value of the "DB_HOST"
        environment variable.
    db_port : str, optional
        Database port. Defaults to the value of the "DB_PORT" environment variable.
    db_database : str, optional
        Database name. Defaults to the value of the "DB_DATABASE" environment variable.

    Returns
    -------
    tuple[str, Optional[dict]]
        A tuple containing the connection string and an optional dictionary for
        additional connection options. If no user is provided and the environment
        variable is empty, a SQLite connection string is returned with a schema
        translation map.
    """
    db_user = db_user or os.getenv("DB_USER", "")
    db_passwd = db_passwd or os.getenv("DB_PASSWD")
    db_host = db_host or os.getenv("DB_HOST")
    db_port = db_port or os.getenv("DB_PORT")
    db_database = db_database or os.getenv("DB_DATABASE")

    if db_user == "":
        logger.warning("Using debug SQLite database...")
        return "sqlite:///./sql_app.db", {"schema_translate_map": {"noshow": None}}
    return (
        f"mssql+pymssql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_database}",
        None,
    )


def get_engine(connection_str: str | None = None) -> Engine:
    """Get the SQLAlchemy engine

    Optionally use the parameter to override the connection string

    Parameters
    ----------
    connection_str : str, optional
        The connection string to the database, by default None

    Returns
    -------
    create_engine
        The SQLAlchemy engine used for queries
    """
    if connection_str is None:
        connection_str, execution_options = get_connection_string()
    else:
        connection_str, execution_options = connection_str, None
    return create_engine(connection_str, execution_options=execution_options)


class CastDate(expression.FunctionElement):
    """This class is used to overwrite the casting behaviour of datetimes to
    dates in SQLAlchemy. This is needed because the default behaviour of SQLAlchemy
    doesn't work on both SQLite and MSSQL
    """

    type = DateTime()
    inherit_cache = True


@compiles(CastDate)
def cast_date_default(element, compiler, **kw):
    """Compile CastDate to a DATE cast for dialects like MSSQL."""
    date = compiler.process(element.clauses, **kw)
    return f"CAST({date} AS DATE)"


@compiles(CastDate, "sqlite")
def cast_date_sqlite(element, compiler, **kw):
    """Compile CastDate for the SQLite dialect using the DATE() function."""
    date = compiler.process(element.clauses, **kw)
    return compiler.process(func.DATE(text(date)))
