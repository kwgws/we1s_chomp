# -*- coding: utf-8 -*-
"""
we1schomp/data/model/article.py
Article data model.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
from typing import Dict
from uuid import uuid4

import sqlalchemy as sql
from dateparser import parse as getdate
from sqlalchemy import orm

from we1schomp.data.model import Base


class Article(Base):
    """Model to hold article data."""

    __tablename__ = "article"
    article_id = sql.Column(sql.Integer, primary_key=True)

    article_uuid = sql.Column(sql.Unicode, index=True, unique=True, default=uuid4())
    name = sql.Column(sql.Unicode, index=True, nullable=False, unique=True)
    url = sql.Column(sql.Unicode, index=True, nullable=False)
    date = sql.Column(sql.DateTime, default=None)
    title = sql.Column(sql.Unicode, nullable=False)
    content_raw = sql.Column(sql.UnicodeText, default="")
    content = sql.Column(sql.UnicodeText, default="")
    no_match = sql.Column(sql.Boolean, default=False)

    query_id = sql.Column(sql.Integer, sql.ForeignKey("query.query_id"))
    query = orm.relationship("Query", back_populates="articles")

    attachment_id = sql.Column(sql.Integer, default=0)
    metapath = sql.Column(sql.Unicode, default="corpus,{name},metadata")
    namespace = sql.Column(sql.Unicode, default="we1sv2.0")
    database = sql.Column(sql.Unicode, default="chomp")

    created_on = sql.Column(sql.DateTime, default=getdate("now"))
    last_updated = sql.Column(sql.DateTime, default=getdate("now"), onupdate=getdate("now"))
    comment = sql.Column(sql.UnicodeText, default="")

    ###
    def to_dict(self) -> Dict:
        """Get article data as dict for exporting to file."""

        return dict(
            doc_id=self.article_uuid,
            name=self.name,
            url=self.url,
            pub_date=self.date.strftime("%Y-%m-%d"),
            title=self.title,
            pub=self.query.source.title,
            content_raw=self.content_raw,
            content=self.content,
            length=len(self.content.split(" ")),
            pub_short=self.query.source.name,
            attachment_id=self.attachment_id,
            metapath=self.metapath,
            namespace=self.namespace,
            database=self.database,
            created_on=self.created_on.strftime("%Y-%m-%d"),
            last_updated=self.last_updated.strftime("%Y-%m-%d"),
            comment=self.comment,
        )

    ###
    def update(self, **kwargs: Dict) -> None:
        """Update values from dict."""
        self.attachment_id = kwargs.get("attachment_id", self.attachment_id)
        self.title = kwargs.get("title", self.title)
        self.url = kwargs.get("url", self.url)
        self.content_raw = kwargs.get("content_raw", self.content_raw)
        self.content = kwargs.get("content", self.content)
        self.metapath = kwargs.get("metapath", self.metapath)
        self.namespace = kwargs.get("namespace", self.namespace)
        self.database = kwargs.get("database", self.database)
        self.comment = kwargs.get("comment", self.comment)
