"""Schema for data handling and import/export.

See https://github.com/whatevery1says/manifest for more information.
"""
from uuid import uuid4


class Manifest:
    """Basic manifest schema."""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.title = kwargs.get("title", name)
        self.database = kwargs.get("database", "chomp")


class Source(Manifest):
    """Source manifest schema."""

    def __init__(self, name: str, webpage: str, **kwargs):
        Manifest.__init__(self, name, **kwargs)
        self.webpage = webpage
        self.source_id = kwargs.get("source_id", str(uuid4().hex))
        self.content_type = kwargs.get("content_type", "website")
        self.country = kwargs.get("country", "")
        self.language = kwargs.get("language", "en-US")
        self.copyright = kwargs.get("copyright", "")
        self.queries = set(kwargs.get("queries", []))
        self.responses = set(kwargs.get("responses", []))
        self.documents = set(kwargs.get("documents", []))


class Query(Manifest):
    """Search manifest schema."""

    def __init__(
        self,
        name: str,
        source: str,
        query_str: str,
        start_date: str,
        end_date: str,
        **kwargs,
    ):
        Manifest.__init__(self, name, **kwargs)
        self.query_id = kwargs.get("query_id", str(uuid4().hex))
        self.query_str = query_str
        self.start_date = start_date
        self.end_date = end_date
        self.source = source
        self.responses = set(kwargs.get("responses", []))
        self.documents = set(kwargs.get("documents", []))


class Response(Manifest):
    """Search response manifest schema."""

    def __init__(self, name: str, url: str, **kwargs):
        Manifest.__init__(self, name, **kwargs)
        self.response_id = kwargs.get("response_id", str(uuid4().hex))
        self.chompApi = kwargs.get("chompApi", "google")
        self.url = url
        self.content = kwargs.get("content", "")
        self.source = kwargs.get("source", "")
        self.query = kwargs.get("query", "")
        self.documents = set(kwargs.get("documents", []))


class Document(Manifest):
    """Raw document data manifest schema."""

    def __init__(self, name: str, url: str, **kwargs):
        Manifest.__init__(self, name, **kwargs)
        self.document_id = kwargs.get("document_id", str(uuid4().hex))
        self.chompApi = kwargs.get("chompApi", "google")
        self.url = url
        self.pub_date = kwargs.get("pub_date", "01-01-1900")
        self.content_html = kwargs.get("content_html", "")
        self.content = kwargs.get("content", "")
        self.length = kwargs.get("length", len(self.content.split(" ")))
        self.pub = kwargs.get("pub", "")
        self.copyright = kwargs.get("copyright", "")
        self.source = kwargs.get("source", "")
        self.query = kwargs.get("query", "")
        self.response = kwargs.get("response", "")
