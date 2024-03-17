import attrs


def asdict(alert) -> dict | None:
    res = attrs.asdict(alert)
    return res
