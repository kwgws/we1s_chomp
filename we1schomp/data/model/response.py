# -*- coding: utf-8 -*-
"""
we1schomp/data/model/response.py
Response data model.

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


class Response(Base):
    """Model to hold response metadata."""

    __tablename__ = "response"
    response_id = sql.Column(sql.Integer, primary_key=True)

    name = sql.Column(sql.Unicode, index=True, nullable=False, unique=True)
    url = sql.Column(sql.Unicode, nullable=False)

    query_id = sql.Column(sql.Integer, sql.ForeignKey("query.query_id"))
    query = orm.relationship("Query", back_populates="responses")

    content_raw = sql.Column(sql.UnicodeText, default="")

    created_on = sql.Column(sql.DateTime, default=getdate("now"))
    last_updated = sql.Column(sql.DateTime, default=getdate("now"), onupdate=getdate("now"))
    comment = sql.Column(sql.UnicodeText, default="")

    ###
    def to_dict(self) -> Dict:
        """Get response data as dict for exporting to file."""

        return dict(
            name=self.name,
            url=self.url,
            date=self.last_updated.strftime("%Y-%m-%d"),
            response=self.content_raw,
            created_on=self.created_on.strftime("%Y-%m-%d"),
            last_updated=self.last_updated.strftime("%Y-%m-%d"),
            comment=self.comment,
        )
