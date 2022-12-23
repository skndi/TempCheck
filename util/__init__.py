from enum import Enum
import datetime


class Period(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


def get_up_to_date(period: Period):
    current_time = datetime.datetime.utcnow()

    if period == Period.DAY:
        up_to = current_time - datetime.timedelta(days=1)
    elif period == Period.WEEK:
        up_to = current_time - datetime.timedelta(weeks=1)
    elif period == Period.MONTH:
        up_to = current_time - datetime.timedelta(days=30)
    elif period == Period.YEAR:
        up_to = current_time - datetime.timedelta(days=365)
    else:
        raise ValueError("Value received is not Period")

    return up_to
