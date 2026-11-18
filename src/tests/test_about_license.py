"""About box licence wording.

Linux builds run Pro-free by platform (see gui/settings.py), so the About box must not tell those
users that a paid licence is required. Pure string logic - no wx needed, runs headless.

Regression test for "on linux builds it still says 'pro licence required'".
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.messages import (  # noqa: E402
    ABOUT_LICENSE,
    ABOUT_LICENSE_PRO,
    about_license_texts,
)


class TestAboutLicenseTexts(unittest.TestCase):
    def test_community(self):
        edition, header, details = about_license_texts(
            unregistered=True, pro_free=False, registered_to=""
        )
        self.assertEqual(edition, "Community Edition")
        self.assertEqual(header, ABOUT_LICENSE)
        self.assertNotIn("paid license", details)

    def test_linux_is_free_not_paid(self):
        edition, header, details = about_license_texts(
            unregistered=False, pro_free=True, registered_to="Linux users"
        )
        self.assertIn("free on Linux", edition)
        self.assertEqual(header, "License: GPL 3 - free on Linux")
        self.assertIn("no license is required", details)
        self.assertNotIn("requires a valid paid license", details)
        self.assertNotIn("pynsource.com/buy", details)
        # the GPL text and the warranty disclaimer still belong in the About box
        self.assertIn("free software", details)
        self.assertIn("WITHOUT ANY WARRANTY", details)

    def test_paid_pro(self):
        edition, header, details = about_license_texts(
            unregistered=False, pro_free=False, registered_to="Andy"
        )
        self.assertIn('registered to "Andy"', edition)
        self.assertEqual(header, ABOUT_LICENSE_PRO)
        self.assertIn("requires a valid paid license", details)


if __name__ == "__main__":
    unittest.main()
