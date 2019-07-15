#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""Unit tests for Wordpress scraping module.
"""

import unittest

from we1s_chomp import wordpress


class TestWordpress(unittest.TestCase):
    """Unit tests for Wordpress scraping."""

    def test_is_api_available(self):
        """Test the Wordpress API availability test."""

        url = "http://we1s.ucsb.edu"
        self.assertTrue(wordpress.is_api_available(url))

        url = "http://ucsb.edu"
        self.assertFalse(wordpress.is_api_available(url))
