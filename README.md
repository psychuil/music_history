# Last.fm crwaler

This allows you to get your last.fm history into a local csv in the format of year, month, artist, plays.
Might grow into something slightly cooler in the future.

## Getting Started

Download it, install the required libreries, and run via cli.

### Prerequisites

I wanna figure out poetry, so no requirements.txt for now. Just pip it.

```
pip install bs4 requests threading argparse pandas lxml
```

### Using

```
f'python lastfm.py --user {username} --years {firstYear}-{lastYear} --filename {nameForCsv}'
```
filename param is optional, default is 'lastFM_{user}.csv'
