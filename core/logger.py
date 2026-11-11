import csv
import os

FILE = "threat_log.csv"

def log(alert):

    file_exists = os.path.isfile(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["type", "mac", "old_ip", "new_ip"])

        writer.writerow([
            alert["type"],
            alert["mac"],
            alert["old_ip"],
            alert["new_ip"]
        ])