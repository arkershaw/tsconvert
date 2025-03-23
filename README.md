# tsconvert

A library and command-line utility for converting between dates and different timestamp formats.

Supports seconds/milliseconds/microseconds since an arbitrary epoch, plus .NET ticks.

## Command-Line Usage

To get the current time as a timestamp in various formats:

`python tsconvert.py -v`

To convert a timestamp from UNIX epoch with millisecond precision to a UTC date/time:

`python tsconvert.py -p ms -t 1520078462345`

To convert a UTC date/time to a UNIX timestamp (second precision):

`python tsconvert.py -p unix -d 2018-03-03T12:01:02.000`

To convert between timestamp types, use the verbose parameter (can also be used with a date):

`python tsconvert.py -vp dotnet -t 636556752623456780`

### Supported Precision

* s: Seconds
* ms: Milliseconds
* us: Microseconds
* ns: Nanoseconds (will be truncated to microsecond precision)

### Aliases

* unix
* javascript
* cassandra
* dotnet

## Library Usage

```
from datetime import datetime, timezone
from tsconvert import *

converter = TSConverter(EPOCH_UNIX, Precision.MILLISECONDS)

converter.from_dt(datetime.now(timezone.utc))
converter.to_dt(1520078462345)
```