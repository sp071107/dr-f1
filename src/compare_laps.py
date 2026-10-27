from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from load_openf1 import load_drivers, load_laps
from openf1_client import get

SESSION_KEY = 9554  # Silverstone 2024 Qualifying
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def driver_number(session_key, acronym):
    drivers = load_drivers(session_key)
    row = drivers[drivers["name_acronym"] == acronym]
    if row.empty:
        raise ValueError(f"Driver {acronym} not found in this session")
    return int(row.iloc[0]["driver_number"])


def fastest_lap_telemetry(session_key, acronym):
    """Return (lap_time_seconds, telemetry dataframe) for a driver's fastest lap."""
    number = driver_number(session_key, acronym)

    laps = load_laps(session_key)
    laps = laps[laps["driver_number"] == number].dropna(subset=["lap_duration", "date_start"])
    lap = laps.loc[laps["lap_duration"].idxmin()]

    start = pd.to_datetime(lap["date_start"])
    end = start + pd.Timedelta(seconds=float(lap["lap_duration"]))

    car = pd.DataFrame(
        get(
            "car_data",
            session_key=session_key,
            driver_number=number,
            **{"date>": start.isoformat(), "date<": end.isoformat()},
        )
    )
    car["date"] = pd.to_datetime(car["date"])
    car = car.sort_values("date").reset_index(drop=True)

    # OpenF1 has no distance channel, so integrate speed over time
    t = (car["date"] - car["date"].iloc[0]).dt.total_seconds().to_numpy()
    speed_ms = car["speed"].to_numpy() / 3.6
    car["time"] = t
    car["distance"] = np.concatenate([[0], np.cumsum(speed_ms[1:] * np.diff(t))])

    return float(lap["lap_duration"]), car


def plot_speed_overlay(session_key, driver1, driver2):
    time1, tel1 = fastest_lap_telemetry(session_key, driver1)
    time2, tel2 = fastest_lap_telemetry(session_key, driver2)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(tel1["distance"], tel1["speed"], label=f"{driver1} {time1:.3f}s")
    ax.plot(tel2["distance"], tel2["speed"], label=f"{driver2} {time2:.3f}s")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Silverstone 2024 Qualifying: Speed Comparison")
    ax.legend()
    fig.tight_layout()

    out = OUTPUT_DIR / f"speed_{driver1}_vs_{driver2}.png"
    
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    plt.show()


if __name__ == "__main__":
    plot_speed_overlay(SESSION_KEY, "NOR", "VER")