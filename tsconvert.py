#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone

EPOCH_UNIX = datetime(1970, 1, 1, tzinfo=timezone.utc)
EPOCH_AD = datetime(1, 1, 1, tzinfo=timezone.utc)

SECONDS = 1
MILLISECONDS = 2
MICROSECONDS = 3
DOTNETTICKS = 4


class Timestamp:
    def __init__(self, epoch=EPOCH_UNIX, precision=SECONDS):
        self.epoch = epoch
        self.precision = precision

    def from_date(self, date: datetime):
        diff = date.astimezone(timezone.utc) - self.epoch
        if self.precision == SECONDS:
            ts = diff / timedelta(seconds=1)
        elif self.precision == MILLISECONDS:
            ts = diff / timedelta(milliseconds=1)
        elif self.precision == MICROSECONDS:
            ts = diff / timedelta(microseconds=1)
        elif self.precision == DOTNETTICKS:
            ts = (diff / timedelta(microseconds=1)) * 10
        else:
            raise ValueError('Unknown precision: {0}'.format(self.precision))
        return int(ts)

    def to_date(self, timestamp: int):
        if self.precision == SECONDS:
            ts = self.epoch + timedelta(seconds=timestamp)
        elif self.precision == MILLISECONDS:
            ts = self.epoch + timedelta(milliseconds=timestamp)
        elif self.precision == MICROSECONDS:
            ts = self.epoch + timedelta(microseconds=timestamp)
        elif self.precision == DOTNETTICKS:
            ts = self.epoch + timedelta(microseconds=timestamp / 10)
        else:
            raise ValueError('Unknown precision: {0}'.format(self.precision))
        return ts


# Seconds since 1970-01-01 00:00:00
UNIX = Timestamp(epoch=EPOCH_UNIX, precision=SECONDS)
# Milliseconds since 1970-01-01 00:00:00
JAVASCRIPT = Timestamp(epoch=EPOCH_UNIX, precision=MILLISECONDS)
# Default is microseconds since 1970-01-01 00:00:00
CASSANDRA = Timestamp(epoch=EPOCH_UNIX, precision=MICROSECONDS)
# .NET ticks are ten-millionths of a second since 0001-01-01 00:00:00
DOTNET = Timestamp(epoch=EPOCH_AD, precision=DOTNETTICKS)


def from_date(date: datetime, format: Timestamp = UNIX):
    return format.from_date(date)


def to_date(timestamp: int, format: Timestamp = UNIX):
    return format.to_date(timestamp)


def current(format: Timestamp = UNIX):
    return format.from_date(datetime.now(timezone.utc))


def _main():
    import sys
    import argparse

    def validate_date(value):
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
        except ValueError:
            raise argparse.ArgumentTypeError('Invalid date/time: {0}.'.format(value))

    mappings = {
        'unix': (UNIX, 'UNIX'),
        'javascript': (JAVASCRIPT, 'Javascript'),
        'cassandra': (CASSANDRA, 'Cassandra'),
        'dotnet': (DOTNET, '.NET Ticks')
    }

    parser = argparse.ArgumentParser(description='Timestamp Converter')
    parser.add_argument('-f', '--format', dest='format', default='unix', choices=['unix', 'javascript', 'cassandra', 'dotnet'], help='Timestamp input format.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--date', dest='date', type=validate_date, default=None, help='The date and time. Example: 2021-04-30T01:55:01.001')
    group.add_argument('-t', '--timestamp', dest='timestamp', type=int, default=None, help='The timestamp value.')
    args = parser.parse_args()

    if args.date:
        dt = args.date
    elif args.timestamp:
        if args.format in mappings:
            format = mappings[args.format][0]
        else:
            sys.exit('Unknown format: {0}'.format(args.format))
        dt = format.to_date(args.timestamp)
    else:
        dt = datetime.now(timezone.utc)

    print('Date (UTC): {0}'.format(dt))

    for format in mappings.values():
        name = format[1]
        value = format[0].from_date(dt)
        print('{0}: {1}'.format(name, value))


if __name__ == '__main__':
    _main()
