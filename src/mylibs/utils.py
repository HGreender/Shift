def validate_date(date_str: str) -> None:
    try:
        datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(
            f"Given '{date_str}'. Expected: 'YYYY-MM-DD'."
        )