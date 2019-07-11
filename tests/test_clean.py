#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Unit tests for clean.py.
"""

import os
import unittest

import ssdeep

from we1s_chomp import clean


class TestClean(unittest.TestCase):
    """Unit tests for clean.py.
    """

    def test_clean(self):
        """Test clean_html().

        Make sure we're getting a reasonable facsimlie of what we know to be the
        article text from the clean_html() function.
        """

        article_filename = os.path.join(os.getcwd(), "tests", "data", "article.txt")
        assert os.path.exists(article_filename)
        with open(article_filename, encoding="utf-8") as txtfile:
            article = txtfile.read()

        html_filename = os.path.join(os.getcwd(), "tests", "data", "article.html")
        assert os.path.exists(html_filename)
        with open(html_filename, encoding="utf-8") as htmlfile:
            html = htmlfile.read()

        output = clean.clean_html(html)
        output_filename = os.path.join(
            os.getcwd(), "tests", "data", "article_output.txt"
        )
        with open(output_filename, "w", encoding="utf-8") as txtfile:
            txtfile.write(output)
        # print(f"Saved to {output_filename}.")

        hash1 = ssdeep.hash(article)
        hash2 = ssdeep.hash(output)
        comparison = ssdeep.compare(hash1, hash2)
        self.assertGreaterEqual(comparison, 63)


if __name__ == "__main__":
    unittest.main()
