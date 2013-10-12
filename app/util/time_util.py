from datetime import datetime

EPOCH = datetime(1970, 1, 1)


def epoch_seconds(timestamp):
    """Returns the number of seconds from the epoch to date."""
    return (timestamp - EPOCH).total_seconds()