# -*- coding: utf-8 -*-
"""
we1schomp/data/model/source.py
Source data model.

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


class Source(Base):
    """Model to hold source metadata."""

    __tablename__ = "source"
    source_id = sql.Column(sql.Integer, primary_key=True)

    name = sql.Column(sql.Unicode, index=True, nullable=False, unique=True)
    short_title = sql.Column(sql.Unicode, default="")
    source_title = sql.Column(sql.Unicode, default="")
    title = sql.Column(sql.Unicode, default="")
    description = sql.Column(sql.UnicodeText, default="")
    audience = sql.Column(sql.Unicode, default="")
    country = sql.Column(sql.Unicode, default="")
    language = sql.Column(sql.Unicode, default="")
    media = sql.Column(sql.Unicode, default="")
    url = sql.Column(sql.Unicode, default="")
    wordpress_uri = sql.Column(sql.Unicode, default="")
    other_urls = sql.Column(sql.Unicode, default="")

    queries = orm.relationship("Query", back_populates="source")
    query_count = sql.Column(sql.Integer, default=0)

    created_on = sql.Column(sql.DateTime, default=getdate("now"))
    last_updated = sql.Column(sql.DateTime, default=getdate("now"), onupdate=getdate("now"))
    comment = sql.Column(sql.UnicodeText, default="")

    ###
    def to_dict(self) -> Dict:
        """Get source data as dict for exporting to file."""

        return dict(
            name=self.name,
            shortTitle=self.short_title,
            source_title=self.source_title,
            title=self.title,
            description=self.description,
            audience=self.audience,
            country=self.country,
            language=self.language,
            media=self.media,
            url=self.url,
            wordpressUri=self.wordpress_uri,
            otherUrls=self.other_urls,
            queries=self.query_count,
            created_on=self.created_on.strftime("%Y-%m-%d"),
            last_updated=self.last_updated.strftime("%Y-%m-%d"),
            comment=self.comment,
        )

    ###
    def update(self, **kwargs: Dict) -> None:
        """Update values from dict."""

        self.source_title = kwargs.get("source_title", self.source_title)
        self.title = kwargs.get("title", self.title)
        self.short_title = kwargs.get("shortTitle", self.short_title)
        self.description = kwargs.get("description", self.description)
        self.country = kwargs.get("country", self.country)
        self.language = kwargs.get("language", self.language)
        self.audience = kwargs.get("audience", self.audience)
        self.media = kwargs.get("media", self.media)
        self.url = kwargs.get("url", self.url)
        self.wordpress_uri = kwargs.get("wordpressUri", self.wordpress_uri)
        self.other_urls = kwargs.get("otherUrls", self.other_urls)
        self.comment = kwargs.get("comment", self.comment)
