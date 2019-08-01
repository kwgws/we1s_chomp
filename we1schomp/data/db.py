# -*- coding: utf-8 -*-
"""
we1schomp/data/db.py
Database handlers.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
from typing import Tuple

import sqlalchemy as sql
from sqlalchemy import orm

from we1schomp.data import Base


def create_db(db_path: str) -> Tuple[orm.Session, sql.MetaData]:
    """Create new database instance and instantiate metadata."""

    engine = sql.create_engine(db_path)
    metadata = Base.metadata.create_all(engine)
    session = orm.sessionmaker(bind=engine)()
    session.commit()

    return session, metadata


def load_db(db_path: str) -> Tuple[orm.Session, sql.MetaData]:
    """Load existing database instance."""

    engine = sql.create_engine(db_path)
    metadata = Base.metadata
    session = orm.sessionmaker(bind=engine)()
    session.commit()

    return session, metadata
