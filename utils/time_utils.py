import datetime


def get_current_date() -> datetime:
    """
    Factory current date.
    :return:
    """
    return datetime.datetime.now(datetime.timezone.utc)
