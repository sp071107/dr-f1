from openf1_client import get


def find_session(year, place, session_name="Qualifying"):
    """Find an OpenF1 session_key by year, place and session type."""
    for field in ("location", "country_name"):
        sessions = get("sessions", year=year, session_name=session_name, **{field: place})
        if sessions:
            return int(sessions[0]["session_key"]), sessions[0]
    raise ValueError(f"No {session_name} found for {place} {year}")