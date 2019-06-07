# -*- coding: utf-8 -*-
"""
we1schomp/data/model/query.py
Query data model.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
from typing import Dict

import sqlalchemy as sql
from dateparser import parse as getdate
from sqlalchemy import orm

from we1schomp.data.model import Base


class Query(Base):
    """Model to hold query metadata."""

    __tablename__ = "query"
    query_id = sql.Column(sql.Integer, primary_key=True)

    source_name = sql.Column(sql.Unicode, sql.ForeignKey("source.name"), index=True)
    source = orm.relationship("Source", back_populates="queries")
    term = sql.Column(sql.Unicode, index=True, nullable=False)
    start_date = sql.Column(sql.DateTime, index=True, nullable=False)
    end_date = sql.Column(sql.DateTime, index=True, nullable=False)

    responses = orm.relationship("Response", back_populates="query")
    articles = orm.relationship("Article", back_populates="query")
    article_count = sql.Column(sql.Integer, default=0)

    enabled = sql.Column(sql.Boolean, default=True, nullable=False)

    created_on = sql.Column(sql.DateTime, default=getdate("now"))
    last_updated = sql.Column(sql.DateTime, default=getdate("now"), onupdate=getdate("now"))
    comment = sql.Column(sql.UnicodeText, default="")

    ###
    def to_dict(self) -> Dict:
        """Get query data as dict for exporting to file."""

        return dict(
            source=self.source.name,
            term=self.term,
            startDate=self.start_date.strftime("%Y-%m-%d"),
            endDate=self.end_date.strftime("%Y-%m-%d"),
            count=self.article_count,
            enabled="" if self.enabled else "false",
            created_on=self.created_on.strftime("%Y-%m-%d"),
            last_updated=self.last_updated.strftime("%Y-%m-%d"),
            comment=self.comment,
        )

    ###
    def find(session: orm.Session, name: str) -> None:
        """Find a query by object name."""

        name = name.replace("chomp-response_", "")
        name = name.replace("chomp_", "")

        source, term, start_date, end_date = name.split("_")[:4]

        return (
            session.query(Query)
            .filter_by(
                source_name=source,
                term=term,
                start_date=getdate(start_date),
                end_date=getdate(end_date),
            )
            .first()
        )
