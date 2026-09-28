"""Importable functions for native-task lessons."""
import csv
import json


def mean_temperature(observations, result):
    with open(observations, newline="", encoding="utf-8") as stream:
        values = [float(row["temperature_c"]) for row in csv.DictReader(stream)]
    with open(result, "w", encoding="utf-8") as stream:
        payload = {"mean_temperature_c": sum(values) / len(values)}
        json.dump(payload, stream, sort_keys=True)
        stream.write("\n")
    return {"count": len(values)}
