"""Test Wikidata utilities."""

import unittest

from quickstatements_client.sources.utils import get_image, get_qid


class TestWikidata(unittest.TestCase):
    """Test Wikidata utilities."""

    def test_get_qid(self):
        """Test looking up a person based on their ORCID identifier."""
        with self.assertRaises(ValueError):
            get_qid("496", "0000-0003-4423-4370")

        self.assertEqual("Q47475003", get_qid("P496", "0000-0003-4423-4370"))

    def test_image(self):
        """Test looking up an image."""
        with self.assertRaises(ValueError):
            get_image("47475003")

        img = get_image("Q47475003")
        self.assertIsNotNone(img)
        self.assertTrue(img.startswith("http://commons.wikimedia.org"))

        self.assertIsNone(get_image("Q109302693"))
