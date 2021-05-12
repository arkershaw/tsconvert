import unittest
from datetime import datetime, timezone
from tsconvert import UNIX, JAVASCRIPT, CASSANDRA, DOTNET, from_date, to_date, current

TS_DATE = datetime(2018, 3, 3, 12, 0, 0, tzinfo=timezone.utc)
TS_UNIX = 1520078400
TS_JAVASCRIPT = 1520078400000
TS_CASSANDRA = 1520078400000000
TS_DOTNET = 636556752000000000


class TestTimestamp(unittest.TestCase):
    def test_from_unix(self):
        format = UNIX
        expected = TS_DATE
        actual = format.to_date(TS_UNIX)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_unix(self):
        format = UNIX
        expected = TS_UNIX
        actual = format.from_date(TS_DATE)
        self.assertEqual(expected, actual)

    def test_from_javascript(self):
        format = JAVASCRIPT
        expected = TS_DATE
        actual = format.to_date(TS_JAVASCRIPT)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_javascript(self):
        format = JAVASCRIPT
        expected = TS_JAVASCRIPT
        actual = format.from_date(TS_DATE)
        self.assertEqual(expected, actual)

    def test_from_cassandra(self):
        format = CASSANDRA
        expected = TS_DATE
        actual = format.to_date(TS_CASSANDRA)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_cassandra(self):
        format = CASSANDRA
        expected = TS_CASSANDRA
        actual = format.from_date(TS_DATE)
        self.assertEqual(expected, actual)

    def test_from_dotnet(self):
        format = DOTNET
        expected = TS_DATE
        actual = format.to_date(TS_DOTNET)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_dotnet(self):
        format = DOTNET
        expected = TS_DOTNET
        actual = format.from_date(TS_DATE)
        self.assertEqual(expected, actual)

    def test_from_date(self):
        expected = TS_UNIX
        actual = from_date(TS_DATE)
        self.assertEqual(expected, actual)

    def test_to_date(self):
        expected = TS_DATE
        actual = to_date(TS_UNIX)
        self.assertEqual(expected, actual)

    def test_current(self):
        expected = int(datetime.now(timezone.utc).timestamp())
        actual = current()
        self.assertEqual(expected, actual)
