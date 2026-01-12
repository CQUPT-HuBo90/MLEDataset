import json
import os
import random
import time
from pathlib import Path

CURRENT_PATH = Path(__file__).parent.resolve()
ROOT_PATH = CURRENT_PATH.parent.resolve()
DATASET_PATH = ROOT_PATH / "MLE"
DATASET_FILENAME_DICT_PATH = DATASET_PATH / "filename_dict.json"
DATASET_LOW_LIGHT_PATH = DATASET_PATH / "low-light"
DATASET_DATA_PATH = DATASET_PATH / "data"
DATASET_TRAIN_PATH = DATASET_PATH / "train"
DATASET_TEST_PATH = DATASET_PATH / "test"

_categories = {
    "b": "building",
    "i": "indoor",
    "p": "people",
    "r": "road",
    "s": "scenery",
    "v": "vehicle",
}
def parse_info_from_filename(filename: str, full_category: bool = True) -> tuple[str, str, int, str, str]:
    filename, suffix = filename.strip().split('.')

    category, index, model = filename.split('_')
    if full_category:
        category = _categories[category]

    return filename, category, int(index), model, suffix

def read_json(path: Path):
    with open(path, mode="r") as f:
        return json.load(f)

def write_json(path: Path, data: dict):
    with open(path, mode="w") as f:
        json.dump(data, f, indent=2)

def create_rng_with_seed(filename: str = "seed"):
    path = CURRENT_PATH / f"{filename}.txt"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                seed = int(f.read().strip())
                return random.Random(seed)
        except Exception:
            pass

    seed = time.time_ns()
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(seed))

    return random.Random(seed)
