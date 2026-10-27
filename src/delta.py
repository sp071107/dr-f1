import argparse

import matplotlib.pyplot as plt
import numpy as np

from compare_laps import OUTPUT_DIR, fastest_lap_telemetry
from session_lookup import find_session


def on_common_grid(tel, lap_time, grid, track_length):
    """Resample a lap onto a shared distance grid, corrected for drift."""
    d = tel["distance"].to_numpy()
    d = d * (track_length / d[-1])
    t = tel["time"].to_numpy()
    t = t * (lap_time / t[-1])
    speed = np.interp(grid, d, tel["speed"])
    time = np.interp(grid, d, t)
    return speed, time


def plot_delta(year, place, driver1, driver2, session_name="Qualifying"):
    session_key, info = find_session(year, place, session_name)
    time1, tel1 = fastest_lap_telemetry(session_key, driver1)
    time2, tel2 = fastest_lap_telemetry(session_key, driver2)

    # Estimate track length from the two laps (OpenF1 has no distance channel)
    track_length = float(np.median([tel1["distance"].iloc[-1], tel2["distance"].iloc[-1]]))

    grid = np.arange(0, track_length, 5)
    speed1, t1 = on_common_grid(tel1, time1, grid, track_length)
    speed2, t2 = on_common_grid(tel2, time2, grid, track_length)

    # Positive delta means driver1 is ahead of driver2
    delta = t2 - t1

    title = f"{info['location']} {year} {session_name}: {driver1} vs {driver2}"
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1.5]}
    )
    ax1.plot(grid, speed1, label=f"{driver1} {time1:.3f}s")
    ax1.plot(grid, speed2, label=f"{driver2} {time2:.3f}s")
    ax1.set_ylabel("Speed (km/h)")
    ax1.set_title(title)
    ax1.legend()

    ax2.plot(grid, delta, color="black")
    ax2.axhline(0, color="grey", linewidth=0.8)
    ax2.set_ylabel(f"Gap (s)\n+ = {driver1} ahead")
    ax2.set_xlabel("Distance (m)")

    fig.tight_layout()
    out = OUTPUT_DIR / f"delta_{year}_{info['location']}_{driver1}_vs_{driver2}.png".replace(" ", "_")
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"Estimated track length: {track_length:.0f} m")
    print(f"Final gap: {delta[-1]:.3f}s (lap time difference: {time2 - time1:.3f}s)")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speed and time delta between two drivers")
    parser.add_argument("year", type=int)
    parser.add_argument("place", help='e.g. Silverstone, Monza, "Monte Carlo"')
    parser.add_argument("driver1", help="three-letter code, e.g. NOR")
    parser.add_argument("driver2", help="three-letter code, e.g. VER")
    parser.add_argument("--session", default="Qualifying", help="Qualifying, Race or Sprint")
    args = parser.parse_args()
    plot_delta(args.year, args.place, args.driver1, args.driver2, args.session)