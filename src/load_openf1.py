import pandas as pd

from openf1_client import get

SESSION_KEY = 9554  # Silverstone 2024 Qualifying


def load_drivers(session_key):
    df = pd.DataFrame(get("drivers", session_key=session_key))
    return df.drop_duplicates("driver_number")


def load_laps(session_key):
    return pd.DataFrame(get("laps", session_key=session_key))


if __name__ == "__main__":
    drivers = load_drivers(SESSION_KEY)[["driver_number", "name_acronym", "team_name"]]
    laps = load_laps(SESSION_KEY).dropna(subset=["lap_duration"])

    fastest = laps.loc[laps.groupby("driver_number")["lap_duration"].idxmin()]
    table = (
        fastest.merge(drivers, on="driver_number")
        [["name_acronym", "team_name", "lap_number", "lap_duration"]]
        .sort_values("lap_duration")
        .head(10)
    )
    print(table.to_string(index=False))