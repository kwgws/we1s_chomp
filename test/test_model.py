import unittest
from datetime import datetime
from pathlib import Path

from we1s_chomp import db, model


class TestModel(unittest.TestCase):
    def setUp(self):
        self.dirpath = Path("test/data")

    def test_source(self):

        # Create source.
        source = model.Source(
            name="we1s",
            webpage="http://we1s.ucsb.edu",
            tags=["hello"],
            country="US",
            language="en-US",
            copyright="(C) 2017-2019 UCSB and the WE1S Project",
        )
        self.assertIsInstance(source, model.Source)
        self.assertEqual(source.name, "we1s")

        # Save to disk.
        db.save_manifest_file(source, self.dirpath)
        self.assertTrue((self.dirpath / f"{source.name}.json").exists())

        # Load from disk.
        source2 = db.load_manifest_file("we1s", self.dirpath)
        self.assertDictEqual(vars(source), vars(source2))

    def test_query(self):

        # Create source.
        query = model.Query(
            source_name="we1s",
            query_str="humanities",
            start_date=datetime(year=2000, month=1, day=1),
            end_date=datetime(year=2019, month=12, day=31),
        )
        self.assertIsInstance(query, model.Query)
        self.assertEqual(query.name, "we1s_humanities_2000-01-01_2019-12-31")

        # Save to disk.
        db.save_manifest_file(query, self.dirpath)
        self.assertTrue((self.dirpath / f"{query.name}.json").exists())

        # Load from disk.
        query2 = db.load_manifest_file(
            "we1s_humanities_2000-01-01_2019-12-31", self.dirpath
        )
        self.assertDictEqual(vars(query), vars(query2))

    def test_response(self):

        # Create response.
        response = model.Response(
            name="chomp-response_we1s_humanities_2000-01-01_2019-12-31_0",
            url="http://we1s.ucsb.edu",
            content="12345 Hello!",
            api_data_provider="wordpress",
            source_name="we1s",
            query_name="we1s_humanities_2000-01-01_2019-12-31",
        )
        self.assertIsInstance(response, model.Response)
        self.assertEqual(
            response.name, "chomp-response_we1s_humanities_2000-01-01_2019-12-31_0"
        )

        # Save to disk.
        db.save_manifest_file(response, self.dirpath)
        self.assertTrue((self.dirpath / f"{response.name}.json").exists())

        # Load from disk.
        response2 = db.load_manifest_file(
            "chomp-response_we1s_humanities_2000-01-01_2019-12-31_0", self.dirpath
        )
        self.assertDictEqual(vars(response), vars(response2))

    def test_article(self):

        # Create article.
        article = model.Article(
            name="chomp_we1s_humanities_2000-01-01_2019-12-31_0",
            url="http://we1s.ucsb.edu",
            title="WhatEvery1Says Article",
            pub="WhatEvery1Says",
            pub_date=datetime(year=2019, month=12, day=31),
            content_html="<h1>Hello!</h1>",
            copyright="(C) 2017-2019 UCSB and the WE1S Project",
            api_data_provider="wordpress",
        )
        self.assertIsInstance(article, model.Article)
        self.assertEqual(article.name, "chomp_we1s_humanities_2000-01-01_2019-12-31_0")

        # Save to disk.
        db.save_manifest_file(article, self.dirpath)
        self.assertTrue((self.dirpath / f"{article.name}.json").exists())

        # Load from disk.
        article2 = db.load_manifest_file(
            "chomp_we1s_humanities_2000-01-01_2019-12-31_0", self.dirpath
        )
        self.assertDictEqual(vars(article), vars(article2))
