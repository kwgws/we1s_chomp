"""File handling and data management tools.

Todo:
    Write handlers for Mongo DB.
"""
import json
from copy import copy
from logging import getLogger
from pathlib import Path
from typing import Dict, Iterator

from we1s_chomp.model import Manifest


###############################################################################
# Load/import functions.                                                      #
###############################################################################


def load_html_file(filename: Path) -> str:
    """Load an HTML file."""
    log = getLogger(__name__)

    try:
        log.info("Loading HTML: %s" % filename)
        with open(filename, encoding="utf-8") as htmlfile:
            return htmlfile.read()

    except FileNotFoundError:
        log.error("HTML file not found: %s" % filename)
        return None


def load_list_file(filename: Path) -> Iterator[str]:
    """Load a list of values from a file, separated by newlines."""
    log = getLogger(__name__)

    try:
        log.info("Loading list: %s" % filename)
        with open(filename, encoding="utf-8") as listfile:
            for value in listfile.readlines():
                value = value.strip(",").strip('"').strip("'")
                if value != "":
                    log.debug('Loaded "%s" from: %s' % (value, filename))
                    yield value

    except FileNotFoundError:
        log.error("List file not found: %s" % filename)
        return None


def load_manifest_file(name: str, dirpath: Path) -> Dict:
    """Load a JSON manifest from a file by name field."""
    log = getLogger(__name__)

    # In theory we could assume that the filename is the name field, since it
    # usually is--but this is probably a safer way to do it. It may need some
    # performance testing, especially with larger data sets, to make sure it's
    # not bogging us down.
    manifest = None
    for filename in dirpath.glob("**/*.json"):
        with open(filename, encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
        if data.get("name", "") == name:
            manifest = copy(data)
            break
    if not manifest:
        log.error('JSON manifest "%s" not found in path: %s' % (name, dirpath))

    # Load raw HTML content if necessary.
    filename_html = manifest.get("content_html", None)
    if filename_html is not None and filename_html != "":
        filename = Path(dirpath) / manifest["content_html"]
        if filename.exists():
            with open(filename, encoding="utf-8") as htmlfile:
                manifest["content_html"] = htmlfile.read()
        else:
            log.warning(
                'Raw HTML specified in "%s" but not found: %s' % (name, filename)
            )

    log.info("Loaded manifest: %s" % filename)
    return manifest


###############################################################################
# Save/export functions.                                                      #
###############################################################################


def check_path(dirpath: Path, create: bool = False) -> bool:
    """Check if a path exists."""
    log = getLogger(__name__)
    path_exists = dirpath.exists()

    if not path_exists and create:
        dirpath.mkdirs(parents=True)
        log.info("Created directory: %s" % dirpath)
        path_exists = True

    return path_exists


def save_html_file(content: str, filename: Path) -> None:
    """Save an HTML file."""
    log = getLogger(__name__)

    check_path(filename.parent, create=True)
    with open(filename, "w", encoding="utf-8") as htmlfile:
        htmlfile.write(content)
        log.info("Saved HTML to: %s" % filename)


def save_manifest_file(manifest: Manifest, dirpath: Path) -> None:
    """Save a manifest to JSON file."""
    log = getLogger(__name__)

    manifest_dict = manifest.to_json()

    # Save raw HTML content if necessary.
    content_html = manifest_dict.get("content_html", None)
    if content_html is not None and content_html != "":
        filename_html = dirpath / f"{manifest.name}.html"
        save_html_file(content_html, filename_html)
        manifest_dict["content_html"] = filename_html

    check_path(dirpath, create=True)
    filename = dirpath / f"{manifest.name}.json"
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(manifest_dict, jsonfile, indent=4, ensure_ascii=False)
    log.info('Saved manifest "%s" to: %s' % (manifest.name, filename))
