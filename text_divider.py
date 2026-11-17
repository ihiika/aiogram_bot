from config import TELEGRAM_MESSAGE_LIMIT


def split_records(list_of_records: list[str], limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    ready_parts = []
    current_part = ''
    for record in list_of_records:
        if len(current_part) + len(record) <= limit:
            current_part += record
        else:
            ready_parts.append(current_part)
            current_part = record
    ready_parts.append(current_part)
    return ready_parts
