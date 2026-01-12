import argparse

from common import parse_info_from_filename, write_json, DATASET_DATA_PATH, DATASET_FILENAME_DICT_PATH, \
    DATASET_LOW_LIGHT_PATH
from common import read_json, create_rng_with_seed

def main(restore: bool):
    if restore:
        if not DATASET_FILENAME_DICT_PATH.exists():
            return
        filename_dict = read_json(DATASET_FILENAME_DICT_PATH)
        for origin, renamed in filename_dict.items():
            file = DATASET_DATA_PATH / renamed
            file.rename(file.with_name(origin))
        DATASET_FILENAME_DICT_PATH.unlink()
    else:
        if DATASET_FILENAME_DICT_PATH.exists():
            return
        rand = create_rng_with_seed()
        filename_dict = {}
        for low_light_file in list(DATASET_LOW_LIGHT_PATH.iterdir()):
            if not low_light_file.is_file():
                continue
            file_prefix = f"{low_light_file.stem}_"
            data_file_group = []
            for data_file in DATASET_DATA_PATH.iterdir():
                if not data_file.is_file() or not data_file.name.startswith(file_prefix):
                    continue
                data_file_group.append(data_file)
            rand.shuffle(data_file_group)
            filename_dict_by_low_light = {}
            for data_file in data_file_group:
                _, category, index, model, _ = parse_info_from_filename(data_file.name, full_category=False)
                filename_dict_by_low_light[data_file.name] = f"{category}_{index}_{chr(ord('A') + len(filename_dict_by_low_light.keys()))}{data_file.suffix}"
                data_file.rename(data_file.with_name(filename_dict_by_low_light[data_file.name]))
            filename_dict.update(filename_dict_by_low_light)
        write_json(DATASET_FILENAME_DICT_PATH, filename_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--restore",
        action="store_true",
    )
    args = parser.parse_args()

    main(args.restore)
