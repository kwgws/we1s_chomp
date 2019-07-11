#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Unit tests for browser.py.

N.b. the Browser class tests require your Selenium grid to be up and running.
Also, some websites will give different content for different browser types--
especially something like the Python Requests module--so comparing output
accross methods may give you unpredictable results.

Todo:
    - Mock version of Selenium interface?
"""

import itertools
import os
import unittest

import ssdeep
from unidecode import unidecode

from we1s_chomp import browser


_SOURCE_URL = "https://we1s.ucsb.edu/we1s-summer-camp-retrospective/"


class TestBrowser(unittest.TestCase):
    """Unit tests for browser.py.
    """

    def test_simple_get(self):
        """Test the simple programmatic get()."""

        test_output_path = os.path.join(os.getcwd(), "tests", "data")
        results = []
        hashes = []

        for i in range(3):
            # Get responses.
            result = unidecode(browser.get(_SOURCE_URL))
            results.append(result)
            # print(f'HTML response: "{result[:50]}..."')

            # Hash the results.
            hash = ssdeep.hash(result)
            hashes.append(hash)
            # print(f'Hash: "{hash}"')

            # Save result for manual inspection.
            filename = os.path.join(test_output_path, f"simple_test{i}.html")
            with open(filename, "w", encoding="utf-8") as htmlfile:
                htmlfile.write(result)
            # print(f"Saved to {filename}.")

        # Compare hashes.
        for i, hash in enumerate(hashes):
            comparison = ssdeep.compare(hashes[0], hash)
            # print(f"Score {i}: {comparison}")
            self.assertGreaterEqual(comparison, 63)

    def test_browser_get(self):
        """Test the Selenium Grid get()."""

        test_output_path = os.path.join(os.getcwd(), "tests", "data")

        br = browser.Browser("http://harbor.english.ucsb.edu:4444/")
        assert br.is_grid_ready()

        hashes = []

        # Get responses.
        for i, result in enumerate(
            [
                unidecode(r[1])
                for r in br.get_batch(itertools.repeat(_SOURCE_URL, 6), 3)
            ]
        ):
            # print(f'HTML response: "{result[:50]}..."')

            # Compute hash.
            hash = ssdeep.hash(result)
            hashes.append(hash)
            # print(f'Hash: "{hash}"')

            # Save result for manual inspection.
            filename = os.path.join(test_output_path, f"browser_test{i}.html")
            with open(filename, "w", encoding="utf-8") as htmlfile:
                htmlfile.write(result)
            # print(f"Saved to {filename}.")

        # Compare hashes.
        for i, hash in enumerate(hashes):
            comparison = ssdeep.compare(hashes[0], hash)
            # print(f"Score {i}: {comparison}")
            self.assertGreaterEqual(comparison, 63)


if __name__ == "__main__":
    unittest.main()
