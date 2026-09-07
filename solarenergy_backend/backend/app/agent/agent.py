class DiagnosisAgent:
    """
    Offline Diagnosis Agent.

    Responsibilities:
    - investigate anomalies
    - evaluate structured evidence
    - generate possible causes
    - rank possible causes
    - determine probable cause
    - estimate confidence
    - generate recommendations

    The Intelligence Core produces the evidence.
    This agent interprets that evidence.

    No external LLM or cloud AI service is used.
    """

    def analyze(self, evidence_package: dict) -> dict:
        # ---------------------------------------------------------
        # 1. Extract structured evidence
        # ---------------------------------------------------------

        evidence = evidence_package.get("evidence") or {}

        power_prediction = (
            evidence.get("power_prediction") or {}
        )

        anomaly = evidence.get("anomaly") or {}

        historical = (
            evidence.get("historical") or {}
        )

        quantitative = (
            evidence.get("quantitative") or {}
        )

        operating_conditions = (
            evidence.get("operating_conditions") or {}
        )

        data_quality = (
            evidence.get("data_quality") or {}
        )

        findings = evidence.get("findings") or []

        # ---------------------------------------------------------
        # 2. Read evidence values
        # ---------------------------------------------------------

        detected = anomaly.get("detected", False)
        anomaly_type = anomaly.get("type")
        severity = anomaly.get("severity")

        deviation = power_prediction.get(
            "deviation_percent"
        )

        prediction_accuracy = quantitative.get(
            "prediction_accuracy_percent"
        )

        historical_deviation = historical.get(
            "deviation_from_historical_average_percent"
        )

        irradiance = operating_conditions.get(
            "irradiance"
        )

        battery_soc = operating_conditions.get(
            "battery_soc"
        )

        inverter_status = operating_conditions.get(
            "inverter_status"
        )

        data_usable = data_quality.get(
            "usable_for_analysis",
            True,
        )

        # ---------------------------------------------------------
        # 3. No anomaly case
        # ---------------------------------------------------------

        if not detected:
            return {
                "diagnosis": (
                    "No significant operational anomaly detected."
                ),
                "probable_cause": "NORMAL_VARIATION",
                "confidence": 0.90,
                "recommendation": (
                    "Continue normal monitoring of the "
                    "solar plant."
                ),
                "action": "CONTINUE_MONITORING",
                "priority": "LOW",
            }

        # ---------------------------------------------------------
        # 4. Generate hypotheses
        # ---------------------------------------------------------

        hypotheses = []

        # Inverter performance
        inverter_score = 0.0

        if anomaly_type == "POWER_DEVIATION":
            inverter_score += 0.40

        if deviation is not None and deviation >= 10:
            inverter_score += 0.30

        if inverter_status not in (
            None,
            "NORMAL",
        ):
            inverter_score += 0.30

        hypotheses.append(
            {
                "cause": "INVERTER_PERFORMANCE",
                "score": inverter_score,
            }
        )

        # Low irradiance
        irradiance_score = 0.0

        if irradiance is not None and irradiance < 300:
            irradiance_score += 0.70

        if deviation is not None and deviation >= 5:
            irradiance_score += 0.30

        hypotheses.append(
            {
                "cause": "LOW_IRRADIANCE",
                "score": irradiance_score,
            }
        )

        # Battery condition
        battery_score = 0.0

        if battery_soc is not None and battery_soc < 20:
            battery_score += 0.70

        if battery_soc is not None and battery_soc >= 90:
            battery_score += 0.70

        if deviation is not None and deviation >= 5:
            battery_score += 0.30

        hypotheses.append(
            {
                "cause": "BATTERY_CONDITION",
                "score": battery_score,
            }
        )

        # Sensor/data quality
        data_quality_score = 0.0

        if not data_usable:
            data_quality_score = 1.0

        hypotheses.append(
            {
                "cause": "SENSOR_DATA_QUALITY",
                "score": data_quality_score,
            }
        )

        # ---------------------------------------------------------
        # 5. Use additional evidence to adjust reasoning
        # ---------------------------------------------------------

        for hypothesis in hypotheses:
            cause = hypothesis["cause"]

            if cause == "INVERTER_PERFORMANCE":
                if inverter_status not in (
                    None,
                    "NORMAL",
                ):
                    hypothesis["score"] += 0.10

                if prediction_accuracy is not None:
                    if prediction_accuracy < 90:
                        hypothesis["score"] += 0.10

            elif cause == "LOW_IRRADIANCE":
                if irradiance is not None and irradiance < 200:
                    hypothesis["score"] += 0.10

            elif cause == "BATTERY_CONDITION":
                if (
                    battery_soc is not None
                    and (
                        battery_soc < 10
                        or battery_soc >= 95
                    )
                ):
                    hypothesis["score"] += 0.10

            elif cause == "SENSOR_DATA_QUALITY":
                if not data_usable:
                    hypothesis["score"] += 0.10

        # ---------------------------------------------------------
        # 6. Historical evidence
        # ---------------------------------------------------------

        if historical_deviation is not None:
            if historical_deviation >= 10:
                for hypothesis in hypotheses:
                    if hypothesis["cause"] in (
                        "INVERTER_PERFORMANCE",
                        "LOW_IRRADIANCE",
                        "BATTERY_CONDITION",
                    ):
                        hypothesis["score"] += 0.05

        # ---------------------------------------------------------
        # 7. Findings provide additional context
        # ---------------------------------------------------------

        if findings:
            for finding in findings:
                finding_lower = finding.lower()

                if "inverter" in finding_lower:
                    for hypothesis in hypotheses:
                        if (
                            hypothesis["cause"]
                            == "INVERTER_PERFORMANCE"
                        ):
                            hypothesis["score"] += 0.02

                if "historical average" in finding_lower:
                    for hypothesis in hypotheses:
                        if (
                            hypothesis["cause"]
                            == "INVERTER_PERFORMANCE"
                        ):
                            hypothesis["score"] += 0.01

        # ---------------------------------------------------------
        # 8. Rank hypotheses
        # ---------------------------------------------------------

        hypotheses.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        best_hypothesis = hypotheses[0]

        probable_cause = best_hypothesis["cause"]

        confidence = round(
            min(best_hypothesis["score"], 1.0),
            2,
        )

        # ---------------------------------------------------------
        # 9. Generate diagnosis and recommendation
        # ---------------------------------------------------------

        if probable_cause == "INVERTER_PERFORMANCE":

            diagnosis = (
                "The available evidence indicates that "
                "inverter performance may be contributing "
                "to the power deviation."
            )

            recommendation = (
                "Inspect inverter operating conditions "
                "and verify inverter performance."
            )

            action = "INSPECT_INVERTER"

            priority = severity or "MEDIUM"

        elif probable_cause == "LOW_IRRADIANCE":

            diagnosis = (
                "The available evidence indicates that "
                "low solar irradiance may be contributing "
                "to reduced generation."
            )

            recommendation = (
                "Continue monitoring solar irradiance "
                "and generation as irradiance conditions "
                "change."
            )

            action = "MONITOR_IRRADIANCE"

            priority = "MEDIUM"

        elif probable_cause == "BATTERY_CONDITION":

            diagnosis = (
                "The battery state of charge may be "
                "contributing to the observed operating "
                "condition."
            )

            recommendation = (
                "Review battery operating conditions "
                "and consider appropriate battery "
                "management action."
            )

            action = "REVIEW_BATTERY"

            priority = "MEDIUM"

        elif probable_cause == "SENSOR_DATA_QUALITY":

            diagnosis = (
                "Incomplete measurement data limits "
                "the reliability of the anomaly diagnosis."
            )

            recommendation = (
                "Verify sensor measurements and restore "
                "missing measurement data before making "
                "operational decisions."
            )

            action = "VERIFY_SENSORS"

            priority = "HIGH"

        else:

            diagnosis = (
                "The available evidence does not strongly "
                "support a specific operational cause."
            )

            recommendation = (
                "Continue monitoring and collect "
                "additional evidence."
            )

            action = "CONTINUE_MONITORING"

            priority = "LOW"

        # ---------------------------------------------------------
        # 10. Return diagnosis result
        # ---------------------------------------------------------

        return {
            "diagnosis": diagnosis,
            "probable_cause": probable_cause,
            "confidence": confidence,
            "recommendation": recommendation,
            "action": action,
            "priority": priority,
        }