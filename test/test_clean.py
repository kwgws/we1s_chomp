#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Unit tests for clean.py.
"""

import os
import unittest

from we1s_chomp import clean


class TestClean(unittest.TestCase):
    """Unit tests for clean.py.
    """

    def test_get_content(self):
        """Test get_content().

        Make sure we're getting a reasonable facsimlie of what we know to be the
        article text from the clean_html() function.
        """
        import ssdeep

        # Load control article.
        article_filename = os.path.join(os.getcwd(), "tests", "data", "article.txt")
        self.assertTrue(os.path.exists(article_filename))
        with open(article_filename, encoding="utf-8") as txtfile:
            article = txtfile.read()

        # Load test HTML.
        html_filename = os.path.join(os.getcwd(), "tests", "data", "article.html")
        self.assertTrue(os.path.exists(html_filename))
        with open(html_filename, encoding="utf-8") as htmlfile:
            html = htmlfile.read()

        # Clean the HTML.
        output = clean.get_content(html)
        output_filename = os.path.join(
            os.getcwd(), "tests", "data", "article_output.txt"
        )
        with open(output_filename, "w", encoding="utf-8") as txtfile:
            txtfile.write(output)

        hash1 = ssdeep.hash(article)
        hash2 = ssdeep.hash(output)
        comparison = ssdeep.compare(hash1, hash2)
        self.assertGreaterEqual(comparison, 63)

    def test_parse_date(self):
        """Test parse_date()."""
        from datetime import datetime

        today = datetime.now().date()
        today_parsed = clean.parse_date("Today").date()
        self.assertEqual(today, today_parsed)

        a_date = datetime.fromtimestamp(240934800.0).date()
        a_parsed_date = clean.parse_date("August 20th, 1977").date()
        self.assertEqual(a_date, a_parsed_date)


if __name__ == "__main__":
    unittest.main()
