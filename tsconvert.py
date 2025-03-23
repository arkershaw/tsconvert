#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = [
    'Precision', 'EPOCH_UNIX', 'EPOCH_AD', 'TSConverter', 'UNIX_SECONDS',
    'DOT_NET_TICKS', 'from_date_time', 'to_date_time', 'current'
]

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Tuple, List


class Precision(Enum):
    SECONDS = 1
    MILLISECONDS = 1_000
    MICROSECONDS = 1_000_000
    DOT_NET_TICKS = 10_000_000
    NANOSECONDS = 1_000_000_000


_DATE_FORMAT_STR = '%Y-%m-%dT%H:%M:%S.%f'
EPOCH_UNIX = datetime(1970, 1, 1, tzinfo=timezone.utc)
EPOCH_AD = datetime(1, 1, 1, tzinfo=timezone.utc)


class TSConverter:
    def __init__(self,
                 epoch: datetime = EPOCH_UNIX,
                 precision: Precision = Precision.SECONDS,
                 name: str | None = None,
                 ):
        self.epoch = epoch
        self.precision = precision
        if name is None:
            self.name = precision.name.capitalize()
        else:
            self.name = name

    def from_dt(self, dt: datetime) -> int:
        diff = dt.astimezone(timezone.utc) - self.epoch
        if self.precision == Precision.SECONDS:
            ts = diff // timedelta(seconds=1)
        elif self.precision == Precision.MILLISECONDS:
            ts = diff // timedelta(milliseconds=1)
        elif self.precision == Precision.MICROSECONDS:
            ts = diff // timedelta(microseconds=1)
        elif self.precision == Precision.NANOSECONDS:
            # No nanoseconds in Python timedelta.
            ts = diff // timedelta(microseconds=1) * 1000
        elif self.precision == Precision.DOT_NET_TICKS:
            ts = diff // timedelta(microseconds=1) * 10
        else:
            raise ValueError(f'Unknown precision: {self.precision}')
        return ts

    def to_dt(self, timestamp: int) -> datetime:
        try:
            if self.precision == Precision.SECONDS:
                ts = self.epoch + timedelta(seconds=timestamp)
            elif self.precision == Precision.MILLISECONDS:
                ts = self.epoch + timedelta(milliseconds=timestamp)
            elif self.precision == Precision.MICROSECONDS:
                ts = self.epoch + timedelta(microseconds=timestamp)
            elif self.precision == Precision.NANOSECONDS:
                ts = self.epoch + timedelta(microseconds=(timestamp // 1_000))
            elif self.precision == Precision.DOT_NET_TICKS:
                ts = self.epoch + timedelta(microseconds=timestamp // 10)
            else:
                raise ValueError(f'Unknown precision: {self.precision}')
            return ts
        except OverflowError:
            raise ValueError((
                f'Timestamp: {timestamp} too large '
                f'for precision: {self.precision.name.capitalize()}'
            ))


# Seconds since 1970-01-01 00:00:00
UNIX_SECONDS = TSConverter(EPOCH_UNIX, Precision.SECONDS, 'UNIX Seconds')
# .NET ticks are ten-millionths of a second since 0001-01-01 00:00:00
DOT_NET_TICKS = TSConverter(EPOCH_AD, Precision.DOT_NET_TICKS, '.NET Ticks')


def from_date_time(
    date: datetime,
    converter: TSConverter = UNIX_SECONDS
) -> int:
    return converter.from_dt(date)


def to_date_time(
    timestamp: int,
    converter: TSConverter = UNIX_SECONDS
) -> datetime:
    return converter.to_dt(timestamp)


def current(converter: TSConverter = UNIX_SECONDS) -> int:
    return converter.from_dt(datetime.now(timezone.utc))


def _truncate_date_time(
    dt: datetime,
    precision: Precision
) -> datetime:
    if precision == Precision.SECONDS:
        return dt.replace(microsecond=0)
    elif precision == Precision.MILLISECONDS:
        ms = dt.microsecond // 1000 * 1000
        return dt.replace(microsecond=ms)
    else:
        return dt


def _parse_args() -> Tuple[datetime, List[TSConverter]]:
    import argparse

    def validate_date(value):
        try:
            return (
                datetime.strptime(value, _DATE_FORMAT_STR)
                .replace(tzinfo=timezone.utc)
            )
        except ValueError:
            raise argparse.ArgumentTypeError(f'Invalid date/time: {value}.')

    mappings: Dict[str, TSConverter] = {
        's': TSConverter(EPOCH_UNIX, Precision.SECONDS),
        'ms': TSConverter(EPOCH_UNIX, Precision.MILLISECONDS),
        'us': TSConverter(EPOCH_UNIX, Precision.MICROSECONDS),
        'ns': TSConverter(EPOCH_UNIX, Precision.NANOSECONDS),
    }

    aliases: Dict[str, TSConverter] = {
        'unix': UNIX_SECONDS,
        # Javascript timestamps use UNIX epoch and millisecond precision.
        'javascript': TSConverter(
            EPOCH_UNIX, Precision.MILLISECONDS, 'Javascript'
        ),
        # Cassandra timestamps use UNIX epoch and
        # microsecond precision by default.
        'cassandra': TSConverter(
            EPOCH_UNIX, Precision.MICROSECONDS, 'Cassandra'
        ),
        'dotnet': DOT_NET_TICKS,
    }

    parser = argparse.ArgumentParser(
        description='Timestamp Converter',
    )
    parser.add_argument(
        '-v',
        dest='verbose',
        action='store_true',
        default=False,
        help='Output all precisions.'
    )
    parser.add_argument(
        '-p',
        dest='precision',
        default='us',
        choices=list(mappings.keys()) + list(aliases.keys()),
        help='Timestamp precision.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d',
        dest='date_time',
        type=validate_date,
        default=None,
        help='The date and time. Example: 2018-03-03T12:00:00.000'
    )
    group.add_argument('-t', dest='timestamp', type=int,
                       default=None, help='The timestamp value.')
    args = parser.parse_args()

    if args.precision in mappings:
        converter = mappings[args.precision]
    elif args.precision in aliases:
        converter = aliases[args.precision]
    else:
        raise ValueError(f'Unknown precision: {args.precision}')

    if args.date_time:
        date_time = args.date_time
    elif args.timestamp:
        date_time = converter.to_dt(args.timestamp)
    else:
        date_time = datetime.now(timezone.utc)

    if args.verbose:
        converters = list(mappings.values()) + [aliases['dotnet']]
    else:
        date_time = _truncate_date_time(date_time, converter.precision)
        converters = [converter]

    return date_time, converters


def _main() -> None:
    date_time, converters = _parse_args()
    print(f'Date (UTC): {date_time}')

    for converter in converters:
        value = converter.from_dt(date_time)
        print(f'{converter.name}: {value}')


if __name__ == '__main__':
    _main()
