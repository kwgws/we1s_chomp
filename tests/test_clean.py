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

    def test_clean_passes(self):
        """Test each clean pass."""

        html_filename = os.path.join(os.getcwd(), "tests", "data", "article.html")
        assert os.path.exists(html_filename)
        with open(html_filename, encoding="utf-8") as htmlfile:
            html = htmlfile.read()

        result_filename = os.path.join(os.getcwd(), "tests", "data", "clean{i}.txt")
        
        # Throw out tags we don't need.
        soup = clean.BeautifulSoup(html, "html5lib")
        with clean.suppress(AttributeError):
            soup.caption.extract()
            soup.footer.extract()
            soup.header.extract()
            soup.img.extract()
            soup.nav.extract()
            soup.script.extract()
        
        # Take all the content tags, default <p>, and mush together the ones that
        # are over the specified length. This seems to work (mostly), but if we're
        # getting bad content for a site we should consider tweaking the formula or
        # using another extraction method.
        content = ""
        for tag in [t for t in soup.find_all("p") if len(t.text) > 75]:
            content += " " + str(tag.text)
        with open(result_filename.format(i=0), "w", encoding="utf-8") as txtfile:
            txtfile.write(content)

        # Expose HTML tags.
        content = clean.html.unescape(content)
        with open(result_filename.format(i=1), "w", encoding="utf-8") as txtfile:
            txtfile.write(content)
        
        # Convert to UTF-8.
        content = clean.unidecode(content)
        with open(result_filename.format(i=2), "w", encoding="utf-8") as txtfile:
            txtfile.write(content)
        
        # Remove HTML tags and leftover URLs.
        content = clean.re.sub(clean.REGEX_HTML_CLEAN, "", content)
        with open(result_filename.format(i=3), "w", encoding="utf-8") as txtfile:
            txtfile.write(content)

        # Hash results and compare.
        hashes = []
        for i in range(4):
            with open(result_filename.format(i=i), encoding="utf-8") as txtfile:
                hashes.append(ssdeep.hash(txtfile.read()))
        
        prev_hash = hashes[0]
        for hash in hashes[1:]:
            # print(ssdeep.compare(prev_hash, hash))
            prev_hash = hash


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
