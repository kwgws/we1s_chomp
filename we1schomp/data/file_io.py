# -*- coding: utf-8 -*-
"""
we1schomp/data/file_io.py
File handlers.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
import csv
import json
import os
from logging import getLogger
from zipfile import ZipFile

from dateparser import parse as getdate
from sqlalchemy import orm

from we1schomp.data import Article, Query, Response, Source


def import_sources(session: orm.Session, filename: str) -> None:
    """Load sources from a csv file."""

    log = getLogger(__name__)
    print(f"Importing sources from {filename}")

    print("Loading...", end="\r", flush=True)
    with open(filename, newline="") as csvfile:

        i = 0
        for i, data in enumerate(csv.DictReader(csvfile)):

            source = session.query(Source).filter_by(name=data["name"]).first()
            add = False
            if not source:
                source = Source(name=data["name"])  # Don't change name.
                add = True
            source.update(**data)

            if add:
                session.add(source)

            log.info("Loaded source: %s" % source.name)
            print(f"Loading...{i + 1}", end="\r", flush=True)

    session.commit()
    print(f"Loading...{i + 1} [\u001b[32mOK\u001b[0m]")


def import_queries(session: orm.Session, filename: str) -> None:
    """Load queries from a csv file."""

    log = getLogger(__name__)
    print(f"Importing queries from {filename}")

    print(f"Loading...", end="\r", flush=True)
    with open(filename, newline="") as csvfile:

        i = 0
        for i, data in enumerate(csv.DictReader(csvfile)):

            query = Query.find(
                session,
                "_".join(
                    [data["source"], data["term"], data["startDate"], data["endDate"]]
                ),
            )
            add = False
            if not query:
                source = session.query(Source).filter_by(name=data["source"]).first()
                source.query_count += 1
                query = Query(
                    source=source,
                    term=data["term"],
                    start_date=getdate(data["startDate"]),
                    end_date=getdate(data["endDate"]),
                )
                add = True
            query.enabled = (
                False if data.get("enabled", "").lower() == "false" else True
            )
            query.comment = data.get("comment", "")

            if add:
                session.add(query)
            log.info(
                'Loaded query: "%s" at %s (Enabled: %r)'
                % (query.term, query.source_name, query.enabled)
            )
            print(f"Loading...{i + 1}", end="\r", flush=True)

    session.commit()
    print(f"Loading...{i + 1} [\u001b[32mOK\u001b[0m]")


def import_responses(session: orm.Session, path: str) -> None:
    """Load responses from JSON files."""

    log = getLogger(__name__)
    print(f"Importing responses from {path}")

    print("Loading...", end="\r", flush=True)
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for i, filename in enumerate(f for f in filenames if f.endswith(".json")):

            if i > 1259:
                break

            filename = os.path.join(dirpath, filename)
            with open(filename, encoding="utf-8") as jsonfile:
                data = json.load(jsonfile)

            response = session.query(Response).filter_by(name=data["name"]).first()
            add = False
            if not response:
                response = Response(name=data["name"])
                add = True
            response.url = data["url"]
            response.content_raw = json.dumps(json.loads(data.get("response", "")))
            response.query = Query.find(session, data["name"])

            if count > 0 and count % 100 == 0:
                log.info("Flushing db session...")
                session.flush()

            if add:
                session.add(response)
            count += 1
            log.info("Loaded response: %s" % filename)
            print(f"Loading...{count}", end="\r", flush=True)

    session.commit()
    print(f"Loading...{count} [\u001b[32mOK\u001b[0m]")


def import_articles(session: orm.Session, path: str) -> None:
    """Load articles from JSON files."""

    log = getLogger(__name__)
    print(f"Importing articles from {path}")

    print("Extracting...", end="\r", flush=True)
    count = 0
    for filename in [f for f in os.listdir(path) if f.endswith(".zip")]:

        filename = os.path.join(path, filename)
        with ZipFile(filename) as zipfile:

            count += len(zipfile.namelist()) + 1

            filepath = filename.replace(".zip", "")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            zipfile.extractall(filepath)

        os.remove(filename)
        log.info("Extracted archive: %s" % filename)
        print(f"Extracting...{count}", end="\r", flush=True)

    print(f"Extracting...{count} [\u001b[32mOK\u001b[0m]")

    print("Loading...", end="\r", flush=True)
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for i, filename in enumerate(f for f in filenames if f.endswith(".json")):

            filename = os.path.join(dirpath, filename)
            with open(filename, encoding="utf-8") as jsonfile:
                data = json.load(jsonfile)

            article = session.query(Article).filter_by(name=data["name"]).first()
            add = False
            if not article:
                query = Query.find(session, data["name"])
                query.article_count += 1
                article = Article(
                    article_uuid=data["doc_id"],
                    name=data["name"],
                    date=getdate(data["pub_date"]),
                    no_match=True if "_no-exact-match" in filename else False,
                    query=query,
                )
                add = True
            article.update(**data)

            if count > 0 and count % 100 == 0:
                log.info("Flushing db session...")
                session.flush()

            filename = filename.replace(".json", ".html")
            try:
                with open(filename, encoding="utf-8") as htmlfile:
                    article.content_raw = htmlfile.read()
            except FileNotFoundError:
                article.content_raw = ""

            if add:
                session.add(article)
            count += 1
            log.info("Loaded article: %s" % filename)
            print(f"Loading...{count}", end="\r", flush=True)

    session.commit()
    print(f"Loading...{count} [\u001b[32mOK\u001b[0m]")


def export_sources(session: orm.Session, filename: str) -> None:
    """Save sources to a csv file."""

    log = getLogger(__name__)
    print(f"Exporting sources to {filename}")

    path = os.path.dirname(filename)
    if not os.path.exists(path):
        os.makedirs(path)
        log.info("Created directory: %s" % path)

    sources = [s.to_dict() for s in session.query(Source)]

    print("Saving...", end="\r", flush=True)
    i = 0
    with open(filename, "w", newline="") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=sources[0].keys())
        writer.writeheader()

        for i, source in enumerate(sources):
            writer.writerow(source)
            log.info("Saved source: %s" % filename)
            print(f"Saving...{i + 1}", end="\r", flush=True)

    print(f"Saving...{i + 1} [\u001b[32mOK\u001b[0m]")


def export_queries(session: orm.Session, filename: str) -> None:
    """Save queries to a csv file."""

    log = getLogger(__name__)
    print(f"Exporting queries to {filename}")

    path = os.path.dirname(filename)
    if not os.path.exists(path):
        os.makedirs(path)
        log.info("Created directory: %s" % path)

    queries = [q.to_dict() for q in session.query(Query)]

    print("Saving...", end="\r", flush=True)
    i = 0
    with open(filename, "w", newline="") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=queries[0].keys())
        writer.writeheader()

        for i, query in enumerate(queries):
            writer.writerow(query)
            log.info('Saved query: "%s" at %s' % (query["term"], query["source"]))
            print(f"Saving...{i + 1}", end="\r", flush=True)

    print(f"Saving...{i + 1} [\u001b[32mOK\u001b[0m]")


def export_responses(session: orm.Session, path: str) -> None:
    """Save table contents to JSON."""

    log = getLogger(__name__)
    print(f"Exporting responses to: {path}")

    print("Saving...", end="\r", flush=True)
    i = 0
    for i, data in enumerate(d.to_dict() for d in session.query(Response).all()):

        # Create base filename and directory.
        if not os.path.exists(path):
            os.makedirs(path)
            log.info("Created directory: %s" % path)

        # Save response metadata and processed content.
        filename = os.path.join(path, f'{data["name"]}.json')
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)

        log.info("Saved response: %s" % filename)
        print(f"Saving...{i + 1}", end="\r", flush=True)

    print(f"Saving...{i + 1} [\u001b[32mOK\u001b[0m]")


def export_articles(session: orm.Session, path: str) -> None:
    """Save table contents to JSON."""

    log = getLogger(__name__)

    print(f"Exporting articles to {path}")

    print("Saving...", end="\r", flush=True)
    i = 0
    for i, data in enumerate(d.to_dict() for d in session.query(Article).all()):

        # Create base filename and directory.
        filepath = os.path.join(path, "_".join(data["name"].split("_")[:-1]))
        if not os.path.exists(filepath):
            os.makedirs(filepath)
            log.info("Created directory: %s" % path)

        # Save raw content to a separate HTML file.
        if data.get("content_raw", None) is not None and data["content_raw"] != "":
            content_raw = data.pop("content_raw")
            filename = os.path.join(filepath, f'{data["name"]}.html')
            with open(filename, "w", encoding="utf-8") as htmlfile:
                htmlfile.write(content_raw)
                log.info("Saved raw html: %s" % filename)

        # Save article metadata and processed content.
        filename = os.path.join(filepath, f'{data["name"]}.json')
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)

        log.info("Saved article: %s" % filename)
        print(f"Saving...{i + 1}", end="\r", flush=True)

    print(f"Saving...{i + 1} [\u001b[32mOK\u001b[0m]")

    print("Archiving...", end="\r", flush=True)
    i = 0
    for dirpath, dirnames, filenames in os.walk(path):

        for dirname in dirnames:
            filepath = os.path.join(dirpath, dirname)
            with ZipFile(f"{filepath}.zip", "w") as zipfile:

                for filename in os.listdir(filepath):
                    zipfile.write(os.path.join(filepath, filename), filename)
                    os.remove(os.path.join(filepath, filename))
                    if filename.endswith(".json"):
                        i += 1

                    log.info("Archiving file: %s" % filename)
                    print(f"Archiving...{i}", end="\r", flush=True)

            os.rmdir(os.path.join(os.path.join(dirpath, dirname)))

            log.info("Created archive: %s" % f"{filepath}.zip")

    print(f"Archiving...{i} [\u001b[32mOK\u001b[0m]")
