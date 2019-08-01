"""File handling and data management tools.

Todo:
    Write handlers for Mongo DB.
"""
import json
from copy import copy
from logging import getLogger
from pathlib import Path
from typing import Dict

from we1s_chomp.clean import date_to_str, str_to_date
from we1s_chomp.model import Source, Query, Response, Document


###############################################################################
# Load/import functions.                                                      #
###############################################################################


def _load_json_file(name: str, dirpath: Path) -> Dict:
    """Load a JSON file by name field."""
    log = getLogger(__name__)

    for filename in dirpath.glob("*.json"):
        with open(filename, encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
            if data.get("name", "") == name:
                log.info('Loaded manifest "%s" from "%s".' % (name, filename))
                return data

    log.error('JSON manifest "%s" not found in path "%s".' % (name, dirpath))
    return None


def load_source(name: str, dirpath: str) -> Source:
    """Load source manifest from JSON file."""
    log = getLogger(__name__)

    source_dict = _load_json_file(name, Path(dirpath))
    if not source_dict:
        return None

    source = Source(**source_dict)
    log.info('Loaded source "%s".' % source.name)
    return source


def load_query(name: str, dirpath: str) -> Query:
    """Load query manifest from JSON file."""
    log = getLogger(__name__)

    query_dict = _load_json_file(name, Path(dirpath))
    if not query_dict:
        return None
    query = Query(**query_dict)

    # Parse start & end dates.
    query.start_date = str_to_date(query.start_date)
    query.end_date = str_to_date(query.end_date)

    log.info('Loaded query "%s".' % query.name)
    return query


def load_response(name: str, dirpath: str) -> Response:
    """Load response manifest from JSON file."""
    log = getLogger(__name__)

    response_dict = _load_json_file(name, Path(dirpath))
    if not response_dict:
        return None

    response = Response(**response_dict)
    log.info('Loaded response "%s".' % response.name)
    return response


def load_document(name: str, dirpath: str) -> Document:
    """Load document from JSON & HTML files."""
    log = getLogger(__name__)

    document_dict = _load_json_file(name, Path(dirpath))
    if not document_dict:
        return None

    document = Document(**document_dict)

    # Load raw HTML content.
    if document.content_html != "":
        filename = Path(dirpath) / document.content_html
        if filename.exists():
            with open(filename, encoding="utf-8") as htmlfile:
                document.content_html = htmlfile.read()
        else:
            log.warning("Raw HTML content not found at %s, skipping." % filename)

    # Parse pub_date.
    if document.pub_date != "":
        document.pub_date = str_to_date(document.pub_date)

    log.info('Loaded document "%s".' % document.name)
    return document


###############################################################################
# Save/export functions.                                                      #
###############################################################################


def _save_json_file(manifest: Dict, dirpath: Path) -> None:
    """Save a JSON file.

    Args:
        manifest: Dictionary manifest.
        dirpath: Directory in which to save. The final filename will be based
            on the manifest's "name" property.
    """
    log = getLogger(__name__)

    filename = manifest["name"] + ".json"
    with open(dirpath / filename, "w", encoding="utf-8") as jsonfile:
        json.dump(manifest, jsonfile, indent=4, ensure_ascii=False)
    log.info('Saved manifest "%s" to "%s".' % (manifest["name"], filename))


def _save_txt_file(content: str, filename: Path) -> None:
    """Save a raw text file."""
    log = getLogger(__name__)

    with open(filename, "w", encoding="utf-8") as txtfile:
        txtfile.write(content)
    log.info('Saved content to "%s".' % filename)


def save_source(source: Source, dirpath: str) -> None:
    """Save source manifest to JSON file."""
    source_dict = copy(source.__dict__)

    source_dict["queries"] = list(source_dict["queries"])
    source_dict["responses"] = list(source_dict["responses"])
    source_dict["documents"] = list(source_dict["documents"])

    _save_json_file(source_dict, Path(dirpath))


def save_query(query: Query, dirpath: str) -> None:
    """Save query manifest to JSON file."""
    query_dict = copy(query.__dict__)

    query_dict["responses"] = list(query_dict["responses"])
    query_dict["documents"] = list(query_dict["documents"])

    # Parse start & end dates.
    query_dict["start_date"] = date_to_str(query_dict["start_date"])
    query_dict["end_date"] = date_to_str(query_dict["end_date"])

    _save_json_file(query_dict, Path(dirpath))


def save_response(response: Response, dirpath: str) -> None:
    """Save response manifest to JSON file."""
    response_dict = copy(response.__dict__)

    response_dict["documents"] = list(response_dict["documents"])

    _save_json_file(response_dict, Path(dirpath))


def save_document(document: Document, dirpath: str) -> None:
    """Save document manifest to JSON and HTML files."""
    document_dict = copy(document.__dict__)

    # Save raw HTML content and store filename in manifest.
    if document_dict.get("content_html", "") != "":
        content_html = document_dict["content_html"]
        filename = document_dict["name"] + ".html"
        _save_txt_file(content_html, Path(dirpath) / filename)
        document_dict["content_html"] = filename

    # Parse pub_date.
    if document_dict.get("pub_date", "") != "":
        document_dict["pub_date"] = date_to_str(document_dict["pub_date"])

    _save_json_file(document_dict, Path(dirpath))
