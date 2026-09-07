from backend.app.ml.prediction_model import predict_power


class IntelligenceCore:
    """
    Intelligence Core for the AI Energy Management System.

    Responsibilities:
    - solar power prediction
    - expected vs actual comparison
    - anomaly detection
    - historical comparison
    - quantitative analysis
    - data-quality analysis
    - evidence package generation

    The FastAPI backend must only call this module.
    """

    def analyze(
        self,
        measurement_data: dict,
        historical_data: list[dict] | None = None,
    ) -> dict:
        """
        Analyze a measurement and return an evidence package.

        historical_data contains previous measurements from the
        same plant. Database access remains outside the
        Intelligence Core.
        """

        irradiance = measurement_data.get("irradiance")
        temperature = measurement_data.get("temperature")
        actual_power = measurement_data.get("ac_power")

        predicted_power = None
        deviation_percent = None

        # 1. Prediction
        if irradiance is not None and temperature is not None:
            predicted_power = predict_power(irradiance, temperature)

        # 2. Expected vs Actual Comparison
        if actual_power is not None and predicted_power is not None:
            if predicted_power != 0:
                deviation_percent = (
                    abs(actual_power - predicted_power)
                    / predicted_power
                ) * 100

        # 3. Anomaly Detection
        anomaly_detected = False
        anomaly_type = None
        anomaly_score = None
        severity = None

        if deviation_percent is not None:
            anomaly_score = round(deviation_percent, 2)

            if deviation_percent > 10:
                anomaly_detected = True
                anomaly_type = "POWER_DEVIATION"
                severity = "HIGH"

            elif deviation_percent >= 5:
                anomaly_detected = True
                anomaly_type = "POWER_DEVIATION"
                severity = "MEDIUM"

            else:
                anomaly_detected = False
                anomaly_type = None
                severity = "LOW"

        # 4. Historical Comparison
        historical_comparison = None

        if historical_data and actual_power is not None:
            historical_powers = [
                item.get("ac_power")
                for item in historical_data
                if item.get("ac_power") is not None
            ]

            if historical_powers:
                historical_average = (
                    sum(historical_powers) / len(historical_powers)
                )

                historical_deviation_percent = None

                if historical_average != 0:
                    historical_deviation_percent = (
                        abs(actual_power - historical_average)
                        / historical_average
                    ) * 100

                historical_comparison = {
                    "historical_average_power": round(
                        historical_average, 2
                    ),
                    "current_actual_power": actual_power,
                    "deviation_from_historical_average_percent": (
                        round(historical_deviation_percent, 2)
                        if historical_deviation_percent is not None
                        else None
                    ),
                    "historical_samples": len(historical_powers),
                }

        # 5. Quantitative Analysis
        quantitative_analysis = {
            "predicted_power": predicted_power,
            "actual_power": actual_power,
            "absolute_power_difference": None,
            "prediction_accuracy_percent": None,
            "historical_average_power": None,
            "difference_from_historical_average": None,
        }

        if predicted_power is not None and actual_power is not None:
            absolute_power_difference = abs(
                actual_power - predicted_power
            )

            quantitative_analysis["absolute_power_difference"] = round(
                absolute_power_difference, 2
            )

            if predicted_power != 0:
                prediction_accuracy = (
                    1
                    - (absolute_power_difference / predicted_power)
                ) * 100

                prediction_accuracy = max(0, prediction_accuracy)

                quantitative_analysis[
                    "prediction_accuracy_percent"
                ] = round(prediction_accuracy, 2)

        if historical_comparison is not None:
            historical_average = historical_comparison[
                "historical_average_power"
            ]

            quantitative_analysis[
                "historical_average_power"
            ] = historical_average

            if historical_average is not None:
                quantitative_analysis[
                    "difference_from_historical_average"
                ] = round(
                    actual_power - historical_average,
                    2,
                )

        # 6. Data Quality Analysis
        quality_fields = [
            "plant_id",
            "timestamp",
            "irradiance",
            "temperature",
            "dc_voltage",
            "dc_current",
            "ac_power",
            "battery_soc",
            "inverter_status",
        ]

        missing_fields = [
            field
            for field in quality_fields
            if measurement_data.get(field) is None
        ]

        data_quality = {
            "status": (
                "COMPLETE"
                if not missing_fields
                else "INCOMPLETE"
            ),
            "missing_fields": missing_fields,
            "usable_for_analysis": len(missing_fields) == 0,
        }

        # 7. Evidence Findings
        findings = []

        if (
            predicted_power is not None
            and actual_power is not None
        ):
            if deviation_percent is not None:
                if deviation_percent < 5:
                    findings.append(
                        "Actual power is close to predicted power."
                    )
                elif deviation_percent < 10:
                    findings.append(
                        "Actual power shows a moderate deviation "
                        "from predicted power."
                    )
                else:
                    findings.append(
                        "Actual power shows a significant deviation "
                        "from predicted power."
                    )

            if (
                quantitative_analysis[
                    "prediction_accuracy_percent"
                ] is not None
                and quantitative_analysis[
                    "prediction_accuracy_percent"
                ] >= 95
            ):
                findings.append(
                    "Prediction accuracy is high."
                )

        if historical_comparison is not None:
            historical_deviation = (
                historical_comparison[
                    "deviation_from_historical_average_percent"
                ]
            )

            if (
                historical_deviation is not None
                and historical_deviation < 5
            ):
                findings.append(
                    "Current power is close to the historical average."
                )
            elif historical_deviation is not None:
                findings.append(
                    "Current power differs from the historical average."
                )

        if (
            measurement_data.get("inverter_status")
            == "NORMAL"
        ):
            findings.append(
                "Inverter status is reported as normal."
            )

        if (
            measurement_data.get("battery_soc") is not None
        ):
            findings.append(
                "Battery state of charge is available for analysis."
            )

        if data_quality["usable_for_analysis"]:
            findings.append(
                "All required measurement fields are available."
            )
        else:
            findings.append(
                "Missing measurement fields may reduce "
                "diagnostic reliability."
            )

        # 8. Evidence Package
        evidence = {
            "power_prediction": {
                "predicted_power": predicted_power,
                "actual_power": actual_power,
                "deviation_percent": (
                    round(deviation_percent, 2)
                    if deviation_percent is not None
                    else None
                ),
            },
            "anomaly": {
                "detected": anomaly_detected,
                "type": anomaly_type,
                "severity": severity,
                "score": anomaly_score,
            },
            "historical": historical_comparison,
            "quantitative": quantitative_analysis,
            "operating_conditions": {
                "irradiance": irradiance,
                "temperature": temperature,
                "battery_soc": measurement_data.get(
                    "battery_soc"
                ),
                "inverter_status": measurement_data.get(
                    "inverter_status"
                ),
            },
            "data_quality": data_quality,
            "findings": findings,
        }

        return {
            "predicted_power": predicted_power,
            "actual_power": actual_power,
            "deviation_percent": (
                round(deviation_percent, 2)
                if deviation_percent is not None
                else None
            ),
            "anomaly": {
                "detected": anomaly_detected,
                "type": anomaly_type,
                "score": anomaly_score,
            },
            "severity": severity,
            "historical_comparison": historical_comparison,
            "quantitative_analysis": quantitative_analysis,
            "data_quality": data_quality,
            "evidence": evidence,
        }