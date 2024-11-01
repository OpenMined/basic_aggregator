from pathlib import Path
from typing import is_typeddict
from syftbox.lib import Client, json
import os


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
    exclude_dir = ["apps", ".syft"]

    entries = os.listdir(datasite_path)

    users = []
    for entry in entries:
        if Path(datasite_path / entry).is_dir() and entry not in exclude_dir:
            users.append(entry)

    return users


if __name__ == "__main__":
    client = Client.load()

    participants = network_participants(client.datasite_path.parent)

    total, missing = aggregate(participants, client.datasite_path.parent)

    output_dir : Path = Path(client.datasite_path) / "app_pipelines" / "basic_aggregation"

    if not output_dir.is_dir():
        os.mkdir(str(output_dir))
    
    
    diff = set(participants) - set(missing)
    with open(str(output_dir) + "/results.json", 'w') as json_file:
        json.dump({'total': total, "missing": missing, "participants": list(diff)}, json_file, indent=4)
