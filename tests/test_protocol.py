import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).parents[1] / "custom_components" / "icelsius")
)

from protocol import PacketBuffer, normalize_value


class PacketBufferTests(unittest.TestCase):
    def test_reassembles_fields_split_across_datagrams(self):
        buffer = PacketBuffer()

        first_updates = buffer.feed(b"SensorID=10002652&temp1=272")
        second_updates = buffer.feed(b"69&battery=3932&")

        self.assertEqual(first_updates, {"SensorID": "10002652"})
        self.assertEqual(
            second_updates, {"temp1": "27269", "battery": "3932"}
        )
        self.assertEqual(buffer.values["SensorID"], "10002652")
        self.assertEqual(normalize_value("temp1", buffer.values["temp1"]), 22.69)
        self.assertEqual(normalize_value("battery", buffer.values["battery"]), 3.932)

    def test_retains_incomplete_field_until_delimiter_arrives(self):
        buffer = PacketBuffer()

        self.assertEqual(buffer.feed(b"SensorID=123"), {})
        self.assertEqual(buffer.feed(b"&RSSI=-85&"), {"SensorID": "123", "RSSI": "-85"})
        self.assertEqual(buffer.values["SensorID"], "123")


if __name__ == "__main__":
    unittest.main()