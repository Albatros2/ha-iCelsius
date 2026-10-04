import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from release import next_version


class ReleaseVersionTests(unittest.TestCase):
    def test_first_release_of_day_has_no_suffix(self):
        self.assertEqual(next_version(date(2026, 10, 4), []), "2026.10.4")

    def test_follow_up_release_increments_suffix(self):
        tags = ["v2026.10.4", "v2026.10.4.1", "v2026.10.4.3"]
        self.assertEqual(next_version(date(2026, 10, 4), tags), "2026.10.4.4")

    def test_tags_from_other_days_do_not_change_version(self):
        self.assertEqual(
            next_version(date(2026, 10, 4), ["v2026.10.3", "v2026.9.30.1"]),
            "2026.10.4",
        )


if __name__ == "__main__":
    unittest.main()