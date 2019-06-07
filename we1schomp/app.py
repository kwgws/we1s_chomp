# -*- coding: utf-8 -*-
"""
we1schomp/app.py
Boilerplate application framework.

WE1SCHOMP ©2018-19, licensed under MIT.
A Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says.
http://we1s.ucsb.edu
http://github.com/seangilleran/we1schomp
"""
import argparse
import json
import logging
import os
from random import choice

import colorama
import requests
from dateparser import parse as getdate

from we1schomp import actions
from we1schomp.browser import Browser
from we1schomp.data import db, file_io

_LOGO = (
    "\u001b[2J\n\n  \u001b[37;41m        \u001b[0m"
    "\n  \u001b[37;41m What   \u001b[0m ┌─┐ ┬ ┬ ┌─┐ ┌┬┐ ┬─┐"
    "\n  \u001b[37;41m Every1 \u001b[0m │   ├─┤ │ │ │││ ├─┘"
    "\n \u001b[37;41m  Says   \u001b[0m └─┘ ┴ ┴ └─┘ ┴ ┴ ┴"
    "\n\u001b[37;41m          \u001b[0m"
    "\n\nA Digital Humanities Web Scraper by Sean Gilleran and WhatEvery1Says."
    "\n© 2018-19, licensed under MIT. See: \u001b[4;34mhttp://we1s.ucsb.edu\u001b[0m for details.\n"
)

_INFO = (
    "More options in config.py. "
    "Readme available at \u001b[4;34mhttp://github.com/seangilleran/we1schomp\u001b[0m."
)


def run() -> None:
    """Application entry point."""
    colorama.init()

    print(_LOGO)

    args = parse_args()
    start_logging(args.log_path, args.is_debug)
    task_list(args)

    start = getdate("now")

    if not os.path.exists(args.db_path):
        session, metadata = db.create_db(f"sqlite:///{args.db_path}")
    else:
        session, metadata = db.load_db(f"sqlite:///{args.db_path}")

    if args.source_in_file != "":
        file_io.import_sources(session, args.source_in_file)
    if args.query_in_file != "":
        file_io.import_queries(session, args.query_in_file)
    if args.response_in_path != "":
        file_io.import_responses(session, args.response_in_path)
    if args.article_in_path != "":
        file_io.import_articles(session, args.article_in_path)

    if args.do_responses:

        cx = os.getenv("CHOMP_GOOGLE_CX")
        key = os.getenv("CHOMP_GOOGLE_KEY")

        if (not args.lynx_path or args.lynx_path == "") and (
            not args.chrome_path or args.chrome_path == ""
        ):
            print("\u001b[31mError:\u001b[0m skipping responses, no browser specified.")

        elif (
            args.chrome_path is not None
            and args.chrome_path != ""
            and (not cx or cx == "" or not key or key == "")
        ):
            print(
                "\u001b[31mError:\u001b[0m skipping responses, cannot find Google CSE ID and key."
            )

        else:
            with Browser(
                lynx_path=args.lynx_path,
                chrome_path=args.chrome_path,
                chrome_log_path=args.chrome_log_path,
                wait_time=(args.min, args.max),
            ) as browser:

                actions.get_responses(session, cx, key, browser)

    if args.do_articles:

        if (not args.lynx_path or args.lynx_path == "") and (
            not args.chrome_path or args.chrome_path == ""
        ):
            print("\u001b[31mError:\u001b[0m skipping articles, no browser specified.")

        else:
            with Browser(
                lynx_path=args.lynx_path,
                chrome_path=args.chrome_path,
                chrome_log_path=args.chrome_log_path,
                wait_time=(args.min, args.max),
            ) as browser:

                actions.get_articles(session, browser)

    if args.do_clean:
        actions.clean_articles(session, args.tag)

    if args.source_out_file != "":
        file_io.export_sources(session, args.source_out_file)
    if args.query_out_file != "":
        file_io.export_queries(session, args.query_out_file)
    if args.response_out_path != "":
        file_io.export_responses(session, args.response_out_path)
    if args.article_out_path != "":
        file_io.export_articles(session, args.article_out_path)

    session.close()
    print(f'\nChomping completed in {getdate("now") - start}')
    print("Have a nice day!\n\n")


def start_logging(path: str, is_debug: bool = False) -> None:
    """
    """
    log_level = logging.DEBUG if is_debug else logging.INFO
    logging.basicConfig(filename=path, level=log_level)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(epilog=_INFO)

    parser.add_argument(
        "-r",
        "--search",
        help="collect search results",
        action="store_true",
        dest="do_responses",
    )
    parser.add_argument(
        "-a",
        "--articles",
        help="collect articles",
        action="store_true",
        dest="do_articles",
    )
    parser.add_argument(
        "-c",
        "--clean",
        help="clean article content",
        action="store_true",
        dest="do_clean",
    )

    options = parser.add_argument_group("configuration arguments")
    options.add_argument(
        "--no-disable",
        help="do not disable completed queries",
        action="store_true",
        dest="no_disable",
    )
    options.add_argument(
        "--tags",
        help="content tags to check (def: [p])",
        nargs="+",
        default=["p", "span", "div"],
        dest="tag",
        type=str,
    )
    options.add_argument(
        "--length",
        help="content tag length to check (def: 75)",
        default=75,
        dest="l",
        type=int,
    )
    options.add_argument(
        "--db",
        help="database path (def: ...\\chomp.sqlite)",
        default="chomp.sqlite",
        dest="db_path",
        type=str,
    )
    options.add_argument(
        "--log",
        help="logfile path (def: ...\\chomp.log)",
        default="chomp.log",
        dest="log_path",
        type=str,
    )
    options.add_argument(
        "--min-wait", help="min browser wait time", default=1.0, dest="min", type=float
    )
    options.add_argument(
        "--max-wait", help="max browser wait time", default=3.0, dest="max", type=float
    )
    options.add_argument("--lynx", help="lynx path", dest="lynx_path", type=str)
    options.add_argument(
        "--chrome", help="chome driver path", dest="chrome_path", type=str
    )
    options.add_argument(
        "--chrome-log",
        help="chrome logfile path (def: ...\\chrome.log)",
        default="chrome.log",
        dest="chrome_log_path",
        type=str,
    )
    options.add_argument(
        "--debug",
        help="debug mode, extra logging",
        action="store_true",
        dest="is_debug",
    )

    input_opts = parser.add_argument_group("file input arguments")
    input_opts.add_argument(
        "-iS",
        "--import-sources",
        help="import sources from csv",
        default="",
        dest="source_in_file",
        type=str,
    )
    input_opts.add_argument(
        "-iQ",
        "--import-queries",
        help="import queries from csv",
        default="",
        dest="query_in_file",
        type=str,
    )
    input_opts.add_argument(
        "-iR",
        "--import-responses",
        help="import json responses",
        default="",
        dest="response_in_path",
        type=str,
    )
    input_opts.add_argument(
        "-iA",
        "--import-articles",
        help="import json articles",
        default="",
        dest="article_in_path",
        type=str,
    )

    output_opts = parser.add_argument_group("file output arguments")
    output_opts.add_argument(
        "-dA",
        "--dump-articles",
        help="export json articles",
        default="",
        dest="article_out_path",
        type=str,
    )
    output_opts.add_argument(
        "-dR",
        "--dump-responses",
        help="export json responses",
        default="",
        dest="response_out_path",
        type=str,
    )
    output_opts.add_argument(
        "-dQ",
        "--dump-queries",
        help="export queries to csv",
        default="",
        dest="query_out_file",
        type=str,
    )
    output_opts.add_argument(
        "-dS",
        "--dump-sources",
        help="export sources to csv",
        default="",
        dest="source_out_file",
        type=str,
    )

    return parser.parse_args()


def task_list(args) -> None:
    """
    """

    print(f"Using database at sqlite:///{args.db_path}")
    print(f"Logging to {args.log_path}\n")
    print("Task list:")
    print(" Nothing here!", end="\r", flush=True)
    if args.source_in_file != "":
        print(f" ✓ Import sources from {args.source_in_file}")
    if args.query_in_file != "":
        print(f" ✓ Import queries from {args.query_in_file}")
    if args.response_in_path != "":
        print(f" ✓ Import responses from {args.response_in_path}")
    if args.article_in_path != "":
        print(f" ✓ Import articles from {args.article_in_path}")
    if args.do_responses:
        print(" ✓ Scrape sources for query search results")
        if args.lynx_path is not None and args.lynx_path != "":
            print(f"   Using Lynx at {args.lynx_path}")
        if args.chrome_path is not None and args.chrome_path != "":
            print(f"   Using Chrome Driver at {args.chrome_path}")
            print(f"   Logging to {args.chrome_log_path}")
    if args.do_articles:
        print(" ✓ Collect raw article XML/HTML from search results")
        if args.lynx_path is not None and args.lynx_path != "":
            print(f"   Using Lynx at {args.lynx_path}")
        if args.chrome_path is not None and args.chrome_path != "":
            print(f"   Using Chrome Driver at {args.chrome_path}")
            print(f"   Logging to {args.chrome_log_path}")
    if args.do_clean:
        print(" ✓ Collect article content from raw XML/HTML")
        print(f"   Using tag(s): {', '.join(args.tag)}")
        print(f"   With text longer than {args.l} chars")
    if args.source_out_file != "":
        print(f" ✓ Export sources to {args.source_out_file}")
    if args.query_out_file != "":
        print(f" ✓ Export queries to {args.query_out_file}")
    if args.response_out_path != "":
        print(f" ✓ Export responses to {args.response_out_path}")
    if args.article_out_path != "":
        print(f" ✓ Export articles to {args.article_out_path}")
    print("\nDouble-check this list. Some tasks may take a long time to complete.")
    while True:
        selection = input("(C)ontinue or e(X)it? ")
        if selection.strip().lower() == "c":
            print("\nHere we go...")
            print(motd())
            break
        elif selection.strip().lower() == "x":
            print('\nFor configuration options, try "python chomp.py --help"')
            print("Have a nice day!\n")
            exit()


def motd() -> str:
    """Get message of the day."""
    key = os.getenv("CHOMP_NEWSAPI_KEY")
    try:
        if key is not None and key != "":
            url = f"https://newsapi.org/v2/everything?q=humanities&apiKey={key}"
            headline = (
                "Humanities Headline: "
                + choice(json.loads(requests.get(url).content)["articles"])["title"]
                + "\n"
            )

        else:
            url = "http://randomuselessfact.appspot.com/random.json?language=en"
            headline = (
                "Headline: " + json.loads(requests.get(url).content)["text"] + "\n"
            )

    except:  # noqa: E722
        headline = ""
    return headline
