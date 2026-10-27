import matplotlib.pyplot as plt
import numpy as np

from compare_laps import OUTPUT_DIR, SESSION_KEY, fastest_lap_telemetry

TRACK_LENGTH_M = 5891  # Silverstone lap length


def on_common_grid(tel, lap_time, grid):
    """Resample a lap onto a shared distance grid, corrected for drift."""
    d = tel["distance"].to_numpy()
    d = d * (TRACK_LENGTH_M / d[-1])
    t = tel["time"].to_numpy()
    t = t * (lap_time / t[-1])
    speed = np.interp(grid, d, tel["speed"])
    time = np.interp(grid, d, t)
    return speed, time


def plot_delta(session_key, driver1, driver2):
    time1, tel1 = fastest_lap_telemetry(session_key, driver1)
    time2, tel2 = fastest_lap_telemetry(session_key, driver2)

    grid = np.arange(0, TRACK_LENGTH_M, 5)
    speed1, t1 = on_common_grid(tel1, time1, grid)
    speed2, t2 = on_common_grid(tel2, time2, grid)

    # Positive delta means driver1 is ahead of driver2
    delta = t2 - t1

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1.5]}
    )
    ax1.plot(grid, speed1, label=f"{driver1} {time1:.3f}s")
    ax1.plot(grid, speed2, label=f"{driver2} {time2:.3f}s")
    ax1.set_ylabel("Speed (km/h)")
    ax1.set_title("Silverstone 2024 Qualifying: Speed and Time Delta")
    ax1.legend()

    ax2.plot(grid, delta, color="black")
    ax2.axhline(0, color="grey", linewidth=0.8)
    ax2.set_ylabel(f"Gap (s)\n+ = {driver1} ahead")
    ax2.set_xlabel("Distance (m)")

    fig.tight_layout()
    out = OUTPUT_DIR / f"delta_{driver1}_vs_{driver2}.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    print(f"Final gap: {delta[-1]:.3f}s (should match the lap time difference)")
    plt.show()


if __name__ == "__main__":
    plot_delta(SESSION_KEY, "NOR", "VER")