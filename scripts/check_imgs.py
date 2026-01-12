from pathlib import Path

from PIL import Image  # ty:ignore[unresolved-import]

from common import DATASET_LOW_LIGHT_PATH, DATASET_DATA_PATH, ROOT_PATH, DATASET_TRAIN_PATH, DATASET_TEST_PATH


def check_image(filepath: Path):
    try:
        with Image.open(filepath) as img:
            img.verify()
    except Exception as e:
        raise e

    try:
        with Image.open(filepath) as img:
            img.load()
    except Exception as e:
        raise e

def batch_check_image(filepath: Path):
    if not filepath.exists():
        return
    for data_file in list(filepath.iterdir()):
        if data_file.suffix == ".csv":
            continue
        try:
            check_image(data_file)
        except Exception as e:
            print_error(data_file, e)

def print_error(filepath: Path, err: Exception):
    print(f"a file may not available: {filepath.relative_to(ROOT_PATH)}, reason: {err}")

def main():
    batch_check_image(DATASET_DATA_PATH)
    batch_check_image(DATASET_LOW_LIGHT_PATH)
    batch_check_image(DATASET_TRAIN_PATH)
    batch_check_image(DATASET_TEST_PATH)
    print("image check finished")

if __name__ == '__main__':
    main()
