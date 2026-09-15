from datetime import datetime, timezone


def convert_to_datetime(str_datetime: str) -> datetime:
    datetime_instance = datetime.strptime(
        str_datetime,
        "%Y-%m-%dT%H:%M:%S.%fZ",
    )
    return datetime_instance.replace(tzinfo=timezone.utc)
