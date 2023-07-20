import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@st.cache_resource
def init_session(user: str, passwd: str, host: str, port: str, db: str) -> sessionmaker:
    """Initialize the connection to the database and cache the resource

    Parameters
    ----------
    user : str
        Username of the service account
    passwd : str
        Password of the service account
    host : str
        Host of the database
    port : int
        Database port
    db : str
        Database name

    Returns
    -------
    Engine
        The returned SQLAlchemy engine used for queries
    """

    CONNECTSTRING = rf"mssql+pymssql://{user}:{passwd}@{host}:{port}/{db}"
    engine = create_engine(CONNECTSTRING)
    session_object = sessionmaker(bind=engine)
    return session_object
