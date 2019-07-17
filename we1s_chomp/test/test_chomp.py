#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Integration tests for the Chomp environment.
"""

import os
import unittest

import ssdeep

from we1s_chomp import browser, clean


class TestChomp(unittest.TestCase):
    """Integration tests for the Chomp environment."""

    def test_chomp_simple(self):
        """Test Chomp."""

        # hashes = []

        # Load control file.
        article_filename = os.path.join(os.getcwd(), "tests", "data", "article.txt")
        assert os.path.exists(article_filename)
        with open(article_filename, encoding="utf-8") as txtfile:
            article = txtfile.read()
        content_hash = ssdeep.hash(article)

        # Load control HTML.
        # html_filename = os.path.join(os.getcwd(), "tests", "data", "article.html")
        # assert os.path.exists(html_filename)
        # with open(html_filename, encoding="utf-8") as txtfile:
        #     html = txtfile.read()
        # html_hash = ssdeep.hash(html)

        result = browser.get(
            "https://we1s.ucsb.edu/research_post/reading-in-santa-barbara-future-building-the-utopian-university/"
        )
        # result_hash = ssdeep.hash(result)

        clean_content = clean.get_content(result)
        clean_content_hash = ssdeep.hash(clean_content)

        self.assertGreaterEqual(ssdeep.compare(content_hash, clean_content_hash), 63)

    def test_chomp(self):
        """Test Selenium Chomp."""

        # hashes = []

        # Load control file.
        article_filename = os.path.join(os.getcwd(), "tests", "data", "article.txt")
        assert os.path.exists(article_filename)
        with open(article_filename, encoding="utf-8") as txtfile:
            article = txtfile.read()
        content_hash = ssdeep.hash(article)

        # Load control HTML.
        # html_filename = os.path.join(os.getcwd(), "tests", "data", "article.html")
        # assert os.path.exists(html_filename)
        # with open(html_filename, encoding="utf-8") as txtfile:
        #     html = txtfile.read()
        # html_hash = ssdeep.hash(html)

        # Get HTML from the Browser.
        br = browser.Browser("http://harbor.english.ucsb.edu:4444")
        assert br.is_grid_ready()

        result = br.get(
            "https://we1s.ucsb.edu/research_post/reading-in-santa-barbara-future-building-the-utopian-university/"
        )
        # result_hash = ssdeep.hash(result)

        clean_content = clean.get_content(result)
        # print(clean_content)
        clean_content_hash = ssdeep.hash(clean_content)

        self.assertGreaterEqual(ssdeep.compare(content_hash, clean_content_hash), 63)


if __name__ == "__main__":
    unittest.main()
