_DAYS_PER_MONTH = [
    31,  # Jan
    28,  # Feb
    31,  # Mar
    30,  # Apr
    31,  # Mai
    30,  # Jun
    31,  # Jul
    31,  # Aug
    31,  # Sep
    30,  # Oct
    31,  # Nov
    30,  # Dec
]

assert len(_DAYS_PER_MONTH) == 12, "There are twelve months in a year."

_HOURS_AT_END_OF_MONTH = [sum(_DAYS_PER_MONTH[:m]) * 24 for m in range(1, 13)]


def get_month(hour: int) -> int:
    for month, hours in enumerate(_HOURS_AT_END_OF_MONTH, start=1):
        if hour <= hours:
            return month

    raise ValueError("Hour is too large.", hour)
