import fastf1
from pathlib import Path

# Set up the cache folder (so data only downloads once)
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def load_session(year, grand_prix, session_type):
    """Load an F1 session, e.g. load_session(2024, 'Silverstone', 'Q')"""
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load()
    return session


if __name__ == "__main__":
    session = load_session(2024, "Silverstone", "Q")
    print(session.event["EventName"])
    print(session.results[["Abbreviation", "Position", "Q3"]].head(10))