import unittest
import unittest.mock
from datetime import datetime, timezone

from tsconvert import Precision, TSConverter, DOT_NET_TICKS, UNIX_SECONDS, \
    from_date_time, to_date_time, current, EPOCH_UNIX, \
    _parse_args, _DATE_FORMAT_STR

TS_DATE_TIME = datetime(2018, 3, 3, 12, 1, 2, 345678, tzinfo=timezone.utc)
TS_UNIX = 1520078462
TS_UNIX_MS = 1520078462345
TS_UNIX_US = 1520078462345678
TS_UNIX_NS = 1520078462345678000
TS_DOT_NET = 636556752623456780


class TestTSConverter(unittest.TestCase):
    def test_from_seconds(self):
        converter = UNIX_SECONDS
        expected = TS_DATE_TIME.replace(microsecond=0)
        actual = converter.to_dt(TS_UNIX)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_seconds(self):
        converter = UNIX_SECONDS
        expected = TS_UNIX
        actual = converter.from_dt(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_from_milliseconds(self):
        converter = TSConverter(precision=Precision.MILLISECONDS)
        expected = TS_DATE_TIME.replace(microsecond=345000)
        actual = converter.to_dt(TS_UNIX_MS)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_milliseconds(self):
        converter = TSConverter(precision=Precision.MILLISECONDS)
        expected = TS_UNIX_MS
        actual = converter.from_dt(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_from_microseconds(self):
        converter = TSConverter(precision=Precision.MICROSECONDS)
        expected = TS_DATE_TIME
        actual = converter.to_dt(TS_UNIX_US)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_microseconds(self):
        converter = TSConverter(precision=Precision.MICROSECONDS)
        expected = TS_UNIX_US
        actual = converter.from_dt(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_from_nanoseconds(self):
        converter = TSConverter(precision=Precision.NANOSECONDS)
        expected = TS_DATE_TIME
        actual = converter.to_dt(TS_UNIX_NS)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_nanoseconds(self):
        converter = TSConverter(precision=Precision.NANOSECONDS)
        expected = TS_UNIX_NS
        actual = converter.from_dt(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_from_dotnet(self):
        precision = DOT_NET_TICKS
        expected = TS_DATE_TIME
        actual = precision.to_dt(TS_DOT_NET)
        self.assertTrue(actual.tzinfo == timezone.utc)
        self.assertEqual(expected, actual)

    def test_to_dotnet(self):
        precision = DOT_NET_TICKS
        expected = TS_DOT_NET
        actual = precision.from_dt(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_from_date(self):
        expected = TS_UNIX
        actual = from_date_time(TS_DATE_TIME)
        self.assertEqual(expected, actual)

    def test_to_date(self):
        expected = TS_DATE_TIME.replace(microsecond=0)
        actual = to_date_time(TS_UNIX)
        self.assertEqual(expected, actual)

    def test_current(self):
        expected = int(datetime.now(timezone.utc).timestamp())
        actual = current()
        self.assertEqual(expected, actual)


class TestArgs(unittest.TestCase):
    def test_no_args(self):
        expected = datetime.now(timezone.utc)
        with unittest.mock.patch('sys.argv', ['program_name']), \
                unittest.mock.patch(
                    'tsconvert.datetime',
                    unittest.mock.Mock(now=lambda tz: expected)
                ):
            date_time, converters = _parse_args()
            self.assertEqual(expected, date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                Precision.MICROSECONDS.name.capitalize(), converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.MICROSECONDS, converters[0].precision)

    def test_precision(self):
        expected = datetime.now(timezone.utc)
        with unittest.mock.patch('sys.argv', ['program_name', '-p', 's']), \
                unittest.mock.patch(
                    'tsconvert.datetime',
                    unittest.mock.Mock(now=lambda tz: expected)
                ):
            date_time, converters = _parse_args()
            self.assertEqual(expected.replace(microsecond=0), date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                Precision.SECONDS.name.capitalize(), converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.SECONDS, converters[0].precision)

    def test_alias(self):
        expected = datetime.now(timezone.utc)
        with unittest.mock.patch(
            'sys.argv',
            ['program_name', '-p', 'javascript']
            ), \
            unittest.mock.patch(
                'tsconvert.datetime',
                unittest.mock.Mock(now=lambda tz: expected)
        ):
            date_time, converters = _parse_args()
            ms = expected.microsecond // 1000 * 1000
            self.assertEqual(expected.replace(microsecond=ms), date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                'Javascript', converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.MILLISECONDS, converters[0].precision)

    def test_timestamp(self):
        with unittest.mock.patch(
            'sys.argv',
            ['program_name', '-t', str(TS_UNIX_US)]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME, date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                'Microseconds', converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.MICROSECONDS, converters[0].precision)

    def test_timestamp_and_precision(self):
        with unittest.mock.patch(
            'sys.argv',
            ['program_name', '-p', 's', '-t', str(TS_UNIX)]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME.replace(microsecond=0), date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                'Seconds', converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.SECONDS, converters[0].precision)

    def test_date(self):
        with unittest.mock.patch(
            'sys.argv',
            ['program_name', '-d', TS_DATE_TIME.strftime(_DATE_FORMAT_STR)]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME, date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                'Microseconds', converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.MICROSECONDS, converters[0].precision)

    def test_date_and_precision(self):
        with unittest.mock.patch(
            'sys.argv',
            [
                'program_name', '-p', 's', '-d',
                TS_DATE_TIME.strftime(_DATE_FORMAT_STR)
            ]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME.replace(microsecond=0), date_time)
            self.assertEqual(1, len(converters))
            self.assertEqual(
                'Seconds', converters[0].name
            )
            self.assertEqual(EPOCH_UNIX, converters[0].epoch)
            self.assertEqual(Precision.SECONDS, converters[0].precision)

    def test_invalid_precision(self):
        with unittest.mock.patch(
            'sys.argv', ['program_name', '-p', 'x']
        ):
            with self.assertRaises(SystemExit):
                date_time, converters = _parse_args()

    def test_mismatched_precision(self):
        with unittest.mock.patch(
            'sys.argv', ['program_name', '-p', 's', '-t', str(TS_UNIX_NS)]
        ):
            with self.assertRaisesRegexp(
                ValueError,
                r'Timestamp: \d+ too large for precision: Seconds'
            ):
                date_time, converters = _parse_args()

    def test_invalid_date(self):
        with unittest.mock.patch(
            'sys.argv', [
                'program_name', '-d',
                TS_DATE_TIME.strftime('%Y-%m-%d %H:%M:%S')
            ]
        ):
            with self.assertRaises(SystemExit):
                date_time, converters = _parse_args()

    def test_verbose_timestamp(self):
        with unittest.mock.patch(
            'sys.argv',
            ['program_name', '-vp', 'ns', '-t', str(TS_UNIX_NS)]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME, date_time)
            self.assertEqual(5, len(converters))
            self.assertListEqual([
                'Seconds',
                'Milliseconds',
                'Microseconds',
                'Nanoseconds',
                '.NET Ticks',
            ], [c.name for c in converters])

    def test_verbose_date(self):
        with unittest.mock.patch(
            'sys.argv',
            [
                'program_name', '-v', '-d',
                TS_DATE_TIME.strftime(_DATE_FORMAT_STR)
            ]
        ):
            date_time, converters = _parse_args()
            self.assertEqual(TS_DATE_TIME, date_time)
            self.assertEqual(5, len(converters))
            self.assertListEqual([
                'Seconds',
                'Milliseconds',
                'Microseconds',
                'Nanoseconds',
                '.NET Ticks',
            ], [c.name for c in converters])

    def test_date_and_timestamp(self):
        with unittest.mock.patch(
            'sys.argv',
            [
                'program_name', '-t', str(TS_UNIX), '-d',
                TS_DATE_TIME.strftime(_DATE_FORMAT_STR)
            ]
        ):
            with self.assertRaises(SystemExit):
                date_time, converters = _parse_args()
