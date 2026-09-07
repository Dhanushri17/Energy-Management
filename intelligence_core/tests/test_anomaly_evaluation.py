from intelligence_core.anomaly.evaluator import evaluate_cases


def test_controlled_anomaly_cases():

    cases = [
        {
            "name": "normal_operation",
            "predicted_power": 7.0,
            "actual_power": 6.9,
            "measurement": {
                "inverter_status": "normal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": False,
        },

        {
            "name": "minor_normal_variation",
            "predicted_power": 7.0,
            "actual_power": 6.4,
            "measurement": {
                "inverter_status": "normal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": False,
        },

        {
            "name": "low_under_generation",
            "predicted_power": 7.0,
            "actual_power": 6.2,
            "measurement": {
                "inverter_status": "normal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": True,
        },

        {
            "name": "medium_under_generation",
            "predicted_power": 7.0,
            "actual_power": 5.0,
            "measurement": {
                "inverter_status": "normal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": True,
        },

        {
            "name": "high_under_generation",
            "predicted_power": 7.0,
            "actual_power": 4.0,
            "measurement": {
                "inverter_status": "abnormal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": True,
        },

        {
            "name": "critical_under_generation",
            "predicted_power": 7.0,
            "actual_power": 2.5,
            "measurement": {
                "inverter_status": "abnormal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": True,
        },

        {
            "name": "complete_generation_failure",
            "predicted_power": 7.0,
            "actual_power": 0.0,
            "measurement": {
                "inverter_status": "abnormal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": True,
        },

        {
            "name": "nighttime",
            "predicted_power": 0.05,
            "actual_power": 0.02,
            "measurement": {
                "inverter_status": "normal",
                "sensor_status": "normal",
            },
            "ground_truth_anomaly": False,
        },
    ]

    results = evaluate_cases(cases)

    for result in results:
        print(result)

    assert len(results) == len(cases)