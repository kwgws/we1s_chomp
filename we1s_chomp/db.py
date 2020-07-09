"""File handling and data management tools.

Todo:
    Write handlers for Mongo DB.
"""
import json
from copy import copy
from logging import getLogger
from pathlib import Path
from typing import Iterator, Union

from we1s_chomp import model
from we1s_chomp.model import Article, Query, Response, Source

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


def load_manifest_file(
    name: str, dirpath: Path
) -> Union[Source, Query, Response, Article]:
    """Load a JSON manifest from a file by its name field."""
    log = getLogger(__name__)

    # In theory we could assume that the filename is the name field, since it
    # usually is--but this is probably a safer way to do it. It may need some
    # performance testing, especially with larger data sets, to make sure it's
    # not bogging us down.
    manifest = None
    for filename in dirpath.glob("**/*.json"):
        with open(filename, encoding="utf-8") as jsonfile:
            manifest = json.load(jsonfile, object_hook=model.from_json)
        if isinstance(manifest, model.Manifest) and manifest.name == name:
            break
    if not manifest:
        log.error('JSON manifest "%s" not found in path: %s' % (name, dirpath))

    # Load raw HTML content if necessary.
    if hasattr(manifest, "content_html") and manifest.content_html != "":
        filename_html = Path(dirpath) / manifest.content_html
        if filename_html.exists():
            with open(filename_html, encoding="utf-8") as htmlfile:
                manifest.content_html = htmlfile.read()
        else:
            log.warning(
                'Raw HTML specified in "%s" but not found: %s' % (name, filename_html)
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
        dirpath.mkdir(parents=True)
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


def save_manifest_file(
    data: Union[Source, Query, Response, Article], dirpath: Path
) -> None:
    """Save a manifest to JSON file."""
    log = getLogger(__name__)

    # Use a copy so we don't mess with the original object's contents.
    manifest = copy(data)

    # Save raw HTML content if necessary.
    if hasattr(manifest, "content_html") and manifest.content_html != "":
        filename_html = dirpath / f"{manifest.name}.html"
        save_html_file(manifest.content_html, filename_html)
        manifest.content_html = f"{manifest.name}.html"

    check_path(dirpath, create=True)
    filename = dirpath / f"{manifest.name}.json"
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(
            manifest, jsonfile, default=model.to_json, indent=4, ensure_ascii=False
        )
    log.info('Saved manifest "%s" to: %s' % (manifest.name, filename))
