"""Tests for the QuickStatements client class."""

import unittest

from quickstatements_client import QuickStatementsClient


class TestClient(unittest.TestCase):
    """Tests for the QuickStatements client class."""

    def setUp(self):
        """Set up the test case with a quickstatements client."""
        self.client = QuickStatementsClient()

    def test_batch_info(self):
        """Test getting batch info."""
        batch_info = self.client.get_batch_info(235283)
        self.assertEqual(23, batch_info.error)
        self.assertEqual(122, batch_info.done)
        self.assertEqual("done", batch_info.status)
