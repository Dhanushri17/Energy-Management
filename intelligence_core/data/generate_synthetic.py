"""
Physics-grounded synthetic renewable-energy dataset generator.

The generated dataset represents a solar plant with:
- environmental measurements
- electrical measurements
- load
- battery storage
- grid import/export
- inverter/sensor status
- optional injected anomalies

Power-flow identity for normal samples:

    generation + grid_import
        =
    load + grid_export + battery_charge_power

Battery convention:
- positive battery_power = charging
- negative battery_power = discharging

The anomaly marker is evaluation-only ground truth.
It should never be used as an inference feature.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def solar_elevation(hour: float) -> float:
    """
    Approximate solar elevation factor.

    Returns a value between 0 and 1.
    """
    x = (hour - 6.0) / 12.0 * np.pi

    if x <= 0 or x >= np.pi:
        return 0.0

    return float(np.sin(x))


def generate_dataset(
    days: int = 30,
    freq: str = "15min",
    plant_id: str = "SOLAR_001",
    panel_capacity_kw: float = 10.0,
    seed: int = 42,
    anomaly_rate: float = 0.0,
) -> pd.DataFrame:
    """
    Generate a synthetic solar-energy dataset.

    Parameters
    ----------
    days:
        Number of days to generate.

    freq:
        Sampling frequency.

    plant_id:
        Plant identifier.

    panel_capacity_kw:
        Nominal solar generation capacity.

    seed:
        Random seed for reproducibility.

    anomaly_rate:
        Fraction of eligible daytime samples receiving an injected anomaly.
    """

    rng = np.random.default_rng(seed)

    periods_per_day = int(
        pd.Timedelta("1D") / pd.Timedelta(freq)
    )

    total_periods = days * periods_per_day

    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=total_periods,
        freq=freq,
    )

    n = len(timestamps)

    # ------------------------------------------------------------------
    # ENVIRONMENTAL CONDITIONS
    # ------------------------------------------------------------------

    hour_decimal = (
        timestamps.hour
        + timestamps.minute / 60.0
    )

    day_of_year = timestamps.dayofyear.to_numpy()

    elevation = np.array(
        [solar_elevation(h) for h in hour_decimal]
    )

    # Slowly changing daily weather condition.
    daily_cloud = rng.uniform(0.65, 1.00, size=days)

    cloud_factor = np.repeat(
        daily_cloud,
        periods_per_day,
    )

    cloud_factor = np.clip(
        cloud_factor
        + rng.normal(0.0, 0.04, size=n),
        0.20,
        1.05,
    )

    # Irradiance in W/m².
    irradiance = (
        1000.0
        * elevation
        * cloud_factor
    )

    irradiance += rng.normal(
        0.0,
        18.0,
        size=n,
    )

    irradiance = np.clip(
        irradiance,
        0.0,
        None,
    )

    # Panel temperature.
    ambient_temperature = (
        24.0
        + 7.0
        * np.sin(
            2
            * np.pi
            * (hour_decimal - 7.0)
            / 24.0
        )
    )

    panel_temperature = (
        ambient_temperature
        + 0.025 * irradiance
        + rng.normal(0.0, 1.5, size=n)
    )

    # ------------------------------------------------------------------
    # SOLAR ELECTRICAL OUTPUT
    # ------------------------------------------------------------------

    temperature_coefficient = 0.004

    temperature_factor = np.clip(
        1.0
        - temperature_coefficient
        * (panel_temperature - 25.0),
        0.75,
        1.05,
    )

    dc_power_kw = (
        panel_capacity_kw
        * (irradiance / 1000.0)
        * temperature_factor
    )

    dc_power_kw += rng.normal(
        0.0,
        0.05,
        size=n,
    )

    dc_power_kw = np.clip(
        dc_power_kw,
        0.0,
        panel_capacity_kw,
    )

    inverter_efficiency = rng.normal(
        0.97,
        0.005,
        size=n,
    )

    inverter_efficiency = np.clip(
        inverter_efficiency,
        0.94,
        0.99,
    )

    ac_power_kw = (
        dc_power_kw
        * inverter_efficiency
    )

    ac_power_kw = np.clip(
        ac_power_kw,
        0.0,
        None,
    )

    # ------------------------------------------------------------------
    # ELECTRICAL MEASUREMENTS
    # ------------------------------------------------------------------

    dc_voltage = (
        500.0
        + 20.0
        * elevation
        + rng.normal(0.0, 4.0, size=n)
    )

    dc_voltage = np.clip(
        dc_voltage,
        400.0,
        550.0,
    )

    dc_current = np.divide(
        dc_power_kw * 1000.0,
        dc_voltage,
        out=np.zeros(n),
        where=dc_voltage != 0,
    )

    # ------------------------------------------------------------------
    # LOAD
    # ------------------------------------------------------------------

    load_power_kw = (
        2.0
        + 0.45
        * np.sin(
            2
            * np.pi
            * (hour_decimal - 6.0)
            / 24.0
        )
        + rng.normal(0.0, 0.20, size=n)
    )

    load_power_kw = np.clip(
        load_power_kw,
        0.8,
        3.2,
    )

    # ------------------------------------------------------------------
    # BATTERY + GRID POWER FLOW
    # ------------------------------------------------------------------

    battery_soc = np.zeros(n)

    battery_voltage = np.zeros(n)

    battery_current = np.zeros(n)

    battery_power_kw = np.zeros(n)

    import_power_kw = np.zeros(n)

    export_power_kw = np.zeros(n)

    # Initial battery state of charge.
    previous_soc = 50.0

    battery_capacity_kwh = 20.0

    max_charge_power_kw = 4.0

    max_discharge_power_kw = 4.0

    charge_efficiency = 0.95

    discharge_efficiency = 0.95

    min_soc = 5.0

    max_soc = 100.0

    timestep_hours = (
        pd.Timedelta(freq).total_seconds()
        / 3600.0
    )

    for i in range(n):

        generation = ac_power_kw[i]

        load = load_power_kw[i]

        net_power = generation - load

        # --------------------------------------------------------------
        # SURPLUS GENERATION
        # --------------------------------------------------------------

        if net_power > 0:

            available_surplus = net_power

            available_charge_power = min(
                available_surplus,
                max_charge_power_kw,
            )

            available_soc_room_kwh = (
                (max_soc - previous_soc)
                / 100.0
                * battery_capacity_kwh
            )

            max_charge_from_soc = (
                available_soc_room_kwh
                / (
                    timestep_hours
                    * charge_efficiency
                )
                if timestep_hours > 0
                else 0.0
            )

            charge_power = min(
                available_charge_power,
                max_charge_from_soc,
            )

            battery_power_kw[i] = charge_power

            stored_energy_kwh = (
                charge_power
                * timestep_hours
                * charge_efficiency
            )

            current_soc = (
                previous_soc
                + (
                    stored_energy_kwh
                    / battery_capacity_kwh
                    * 100.0
                )
            )

            current_soc = np.clip(
                current_soc,
                min_soc,
                max_soc,
            )

            remaining_surplus = max(
                available_surplus
                - charge_power,
                0.0,
            )

            export_power_kw[i] = (
                remaining_surplus
            )

            import_power_kw[i] = 0.0

        # --------------------------------------------------------------
        # POWER DEFICIT
        # --------------------------------------------------------------

        else:

            deficit = abs(net_power)

            available_discharge_power = min(
                deficit,
                max_discharge_power_kw,
            )

            available_soc_energy_kwh = (
                (previous_soc - min_soc)
                / 100.0
                * battery_capacity_kwh
            )

            max_discharge_from_soc = (
                available_soc_energy_kwh
                * discharge_efficiency
                / timestep_hours
                if timestep_hours > 0
                else 0.0
            )

            discharge_power = min(
                available_discharge_power,
                max_discharge_from_soc,
            )

            # Negative means battery discharging.
            battery_power_kw[i] = (
                -discharge_power
            )

            discharged_energy_kwh = (
                discharge_power
                * timestep_hours
                / discharge_efficiency
            )

            current_soc = (
                previous_soc
                - (
                    discharged_energy_kwh
                    / battery_capacity_kwh
                    * 100.0
                )
            )

            current_soc = np.clip(
                current_soc,
                min_soc,
                max_soc,
            )

            remaining_deficit = max(
                deficit
                - discharge_power,
                0.0,
            )

            import_power_kw[i] = (
                remaining_deficit
            )

            export_power_kw[i] = 0.0

        battery_soc[i] = current_soc

        # Battery voltage is derived from SOC.
        battery_voltage[i] = (
            48.0
            + 0.08
            * (current_soc - 50.0)
        )

        battery_voltage[i] = np.clip(
            battery_voltage[i],
            44.0,
            56.0,
        )

        # Current is derived from actual battery power.
        battery_current[i] = np.divide(
            battery_power_kw[i] * 1000.0,
            battery_voltage[i],
            out=np.zeros(1),
            where=battery_voltage[i] != 0,
        )[0]

        previous_soc = current_soc

    # ------------------------------------------------------------------
    # GRID
    # ------------------------------------------------------------------

    grid_voltage = rng.normal(
        230.0,
        2.0,
        size=n,
    )

    grid_frequency = rng.normal(
        50.0,
        0.05,
        size=n,
    )

    grid_status = np.full(
        n,
        "available",
        dtype=object,
    )

    # ------------------------------------------------------------------
    # INVERTER / SENSOR STATUS
    # ------------------------------------------------------------------

    inverter_status = np.full(
        n,
        "normal",
        dtype=object,
    )

    inverter_fault_code = np.full(
        n,
        np.nan,
    )

    sensor_status = np.full(
        n,
        "normal",
        dtype=object,
    )

    # ------------------------------------------------------------------
    # ANOMALY INJECTION
    # ------------------------------------------------------------------

    is_injected_anomaly = np.zeros(
        n,
        dtype=bool,
    )

    if anomaly_rate > 0:

        daytime_indices = np.where(
            irradiance > 100.0
        )[0]

        anomaly_count = int(
            len(daytime_indices)
            * anomaly_rate
        )

        if anomaly_count > 0:

            anomaly_indices = rng.choice(
                daytime_indices,
                size=anomaly_count,
                replace=False,
            )

            for idx in anomaly_indices:

                anomaly_type = rng.choice(
                    [
                        "under_generation",
                        "sensor_fault",
                        "inverter_fault",
                    ]
                )

                is_injected_anomaly[idx] = True

                if anomaly_type == "under_generation":

                    factor = rng.choice(
                        [
                            0.85,
                            0.70,
                            0.50,
                            0.20,
                        ]
                    )

                    ac_power_kw[idx] *= factor

                elif anomaly_type == "sensor_fault":

                    sensor_status[idx] = "abnormal"

                    irradiance[idx] = np.nan

                elif anomaly_type == "inverter_fault":

                    inverter_status[idx] = "abnormal"

                    inverter_fault_code[idx] = 101.0

                    ac_power_kw[idx] *= 0.50

    # ------------------------------------------------------------------
    # DATAFRAME
    # ------------------------------------------------------------------

    df = pd.DataFrame(
        {
            "plant_id": plant_id,
            "timestamp": timestamps,
            "source": "solar",

            "irradiance": irradiance,
            "panel_temperature": panel_temperature,

            "dc_voltage": dc_voltage,
            "dc_current": dc_current,
            "ac_power": ac_power_kw,

            "battery_soc": battery_soc,
            "battery_voltage": battery_voltage,
            "battery_current": battery_current,
            "battery_temperature": (
                panel_temperature
                + rng.normal(0.0, 1.0, size=n)
            ),

            "load_power": load_power_kw,

            "grid_status": grid_status,
            "grid_voltage": grid_voltage,
            "grid_frequency": grid_frequency,

            "import_power": import_power_kw,
            "export_power": export_power_kw,

            "inverter_status": inverter_status,
            "inverter_fault_code": inverter_fault_code,

            "sensor_status": sensor_status,

            # Evaluation-only ground truth.
            "is_injected_anomaly": (
                is_injected_anomaly
            ),
        }
    )

    return df


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Generate synthetic renewable-energy data."
        )
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--freq",
        type=str,
        default="15min",
    )

    parser.add_argument(
        "--plant-id",
        type=str,
        default="SOLAR_001",
    )

    parser.add_argument(
        "--panel-capacity-kw",
        type=float,
        default=10.0,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.0,
    )

    parser.add_argument(
        "--out",
        type=str,
        required=True,
    )

    args = parser.parse_args()

    df = generate_dataset(
        days=args.days,
        freq=args.freq,
        plant_id=args.plant_id,
        panel_capacity_kw=args.panel_capacity_kw,
        seed=args.seed,
        anomaly_rate=args.anomaly_rate,
    )

    output_path = Path(args.out)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Generated {len(df)} rows -> {output_path}"
    )


if __name__ == "__main__":
    main()