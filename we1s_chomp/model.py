"""Schema for data handling and import/export.
See https://github.com/whatevery1says/manifest for more information.
"""
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterable, Union
from uuid import uuid4

from we1s_chomp.clean import date_to_str, str_to_date


class Manifest:
    """Basic manifest schema."""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.chomp_id = kwargs.get("chomp_id", str(uuid4().hex))
        self.api_software = kwargs.get("api_software", "chomp2")
        self.created_date = kwargs.get("created_date", str_to_date("now"))
        self.updated_date = kwargs.get("updated_date", str_to_date("now"))
        self.notes = kwargs.get("notes", [])


class Source(Manifest):
    """Source manifest schema."""

    def __init__(self, name: str, webpage: str, tags: Iterable[str], **kwargs):
        self.webpage = webpage
        self.content_type = kwargs.get("content_type", "website")
        self.country = kwargs.get("country", "")
        self.language = kwargs.get("language", "en-US")
        self.copyright = kwargs.get("copyright", "")
        self.tags = set(tags)
        self.collection_identifiers = kwargs.get("collection_identifiers", [name])
        self.query_names = kwargs.get("query_names", [])
        self.response_names = kwargs.get("response_names", [])
        self.article_names = kwargs.get("article_names", [])
        Manifest.__init__(self, name, **kwargs)


class Query(Manifest):
    """Search manifest schema.
    TODO: This actually contains all the info we need to run a successful
    # query. Can we simplify it?
    """

    def __init__(
        self,
        source_name: str,
        query_str: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs,
    ):
        kwargs["name"] = "_".join(
            [
                source_name,
                query_str,
                date_to_str(start_date).split("T")[0],
                date_to_str(end_date).split("T")[0],
            ]
        )
        self.query_str = query_str
        self.start_date = start_date
        self.end_date = end_date
        self.source_name = source_name
        self.response_names = set(kwargs.get("response_names", []))
        self.article_names = set(kwargs.get("article_names", []))
        Manifest.__init__(self, **kwargs)


class Response(Manifest):
    """Search response manifest schema."""

    def __init__(self, name: str, url: str, **kwargs):
        Manifest.__init__(self, name, **kwargs)
        self.url = url
        self.content = kwargs.get("content", "")
        self.api_data_provider = kwargs.get("api_data_provider", "google")
        self.source_name = kwargs.get("source_name", "")
        self.query_name = kwargs.get("query_name", "")
        self.article_names = kwargs.get("article_names", [])


class Article(Manifest):
    """Raw article data manifest schema."""

    def __init__(self, name: str, url: str, **kwargs):
        Manifest.__init__(self, name, **kwargs)
        self.url = url
        self.title = kwargs.get("title", name)
        self.pub = kwargs.get("pub", "")
        self.pub_date = kwargs.get("pub_date", "01-01-1900")
        self.content_html = kwargs.get("content_html", "")
        self.content = kwargs.get("content", "")
        self.length = kwargs.get("length", len(self.content.split(" ")))
        self.copyright = kwargs.get("copyright", "")
        self.api_data_provider = kwargs.get("api_data_provider", "google")
        self.keywords = kwargs.get("keywords", [])
        self.source_name = kwargs.get("source_name", "")
        self.query_name = kwargs.get("query_name", "")
        self.response_name = kwargs.get("response_name", "")


def to_json(manifest: Union[Source, Query, Response, Article]) -> Dict:
    """JSON serialization hook."""
    manifest_dict = vars(manifest)

    # Parse date metadata.
    for date_field in [
        f for f in manifest_dict if isinstance(manifest_dict[f], datetime)
    ]:
        manifest_dict[date_field] = date_to_str(manifest_dict[date_field])

    # Parse sets.
    for set_field in [f for f in manifest_dict if isinstance(manifest_dict[f], set)]:
        manifest_dict[set_field] = list(manifest_dict[set_field])

    return manifest_dict


def from_json(manifest_dict: Dict):
    """JSON deserialization hook."""
    log = getLogger(__name__)

    # Parse date metadata.
    for date_field in [f for f in manifest_dict if f.endswith("_date")]:
        try:
            date_str = str_to_date(manifest_dict.get(date_field, "now"))
            manifest_dict[date_field] = date_str
        except (AttributeError, ValueError) as e:
            log.error(
                'Could not parse date string "%s" from field "%s": %s'
                % (date_str, date_field, e)
            )
            return None

    if "url" in manifest_dict.keys() and "pub_date" in manifest_dict.keys():
        return Article(**manifest_dict)
    if "url" in manifest_dict.keys():
        return Response(**manifest_dict)
    if "start_date" in manifest_dict.keys() and "end_date" in manifest_dict.keys():
        return Query(**manifest_dict)
    if "webpage" in manifest_dict.keys() and "tags" in manifest_dict.keys():
        return Source(**manifest_dict)
    else:
        return Manifest(**manifest_dict)
