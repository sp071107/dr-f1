import matplotlib.pyplot as plt
from pathlib import Path
from load_session import load_session

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_fastest_lap_telemetry(session, driver):
    """Return telemetry for a driver's fastest lap, with distance added."""
    lap = session.laps.pick_drivers(driver).pick_fastest()
    tel = lap.get_car_data().add_distance()
    return lap, tel


def plot_speed_overlay(session, driver1, driver2):
    lap1, tel1 = get_fastest_lap_telemetry(session, driver1)
    lap2, tel2 = get_fastest_lap_telemetry(session, driver2)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(tel1["Distance"], tel1["Speed"], label=f"{driver1} {lap1['LapTime']}")
    ax.plot(tel2["Distance"], tel2["Speed"], label=f"{driver2} {lap2['LapTime']}")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title(f"{session.event['EventName']} {session.event.year} Qualifying: Speed Comparison")
    ax.legend()
    fig.tight_layout()

    out = OUTPUT_DIR / f"speed_{driver1}_vs_{driver2}.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")
    plt.show()


if __name__ == "__main__":
    session = load_session(2024, "Silverstone", "Q")
    plot_speed_overlay(session, "NOR", "VER")