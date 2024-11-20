from pathlib import Path
from datetime import datetime
from syftbox.lib import Client
import json
import os

API_NAME = "basic_aggregation"

def aggregate(participants: list[str], datasite_path: Path):
    total = 0
    missing = []

    for user_folder in participants:
        value_file: Path = Path(datasite_path) / user_folder / "public" / "value.txt"

        if value_file.exists():
            with value_file.open("r") as file:
                total += float(file.read())
        else:
            missing.append(user_folder)

    return total, missing


def network_participants(datasite_path: Path):
    entries = os.listdir(datasite_path)

    users = []
    for entry in entries:
        if Path(datasite_path / entry).is_dir() and '@' in entry:
            users.append(entry)

    return users


def should_run() -> bool:
    INTERVAL = 20  # 20 seconds
    timestamp_file = f"./script_timestamps/{API_NAME}_last_run"
    os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
    now = datetime.now().timestamp()
    time_diff = INTERVAL  # default to running if no file exists
    if os.path.exists(timestamp_file):
        try:
            with open(timestamp_file, "r") as f:
                last_run = int(f.read().strip())
                time_diff = now - last_run
        except (FileNotFoundError, ValueError):
            print(f"Unable to read timestamp file: {timestamp_file}")
    if time_diff >= INTERVAL:
        with open(timestamp_file, "w") as f:
            f.write(f"{int(now)}")
        return True
    return False
   

if __name__ == "__main__":
    if not should_run():
        print(f"Skipping {API_NAME}, not enough time has passed.")
        exit(0)
    
    client = Client.load()

    participants = network_participants(client.datasites)

    total, missing = aggregate(participants, client.datasites)

    output_dir: Path = client.api_data(API_NAME)

    if not output_dir.is_dir():
        os.makedirs(str(output_dir), exist_ok=True)

    diff = set(participants) - set(missing)
    with open(str(output_dir) + "/results.json", "w") as json_file:
        json.dump(
            {"total": total, "missing": missing, "participants": list(diff)},
            json_file,
            indent=4,
        )
