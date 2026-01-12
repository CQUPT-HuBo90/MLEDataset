import argparse
import json
import shutil
from dataclasses import dataclass, asdict
from math import ceil, floor
from pathlib import Path
from typing import Optional, TypeVar, Callable

import pandas  # ty:ignore[unresolved-import]

from common import ROOT_PATH, DATASET_PATH, parse_info_from_filename, create_rng_with_seed, read_json, \
    DATASET_FILENAME_DICT_PATH


@dataclass
class Sample:
    id: str
    split: Optional[str]
    index: int
    category: str
    model: str
    file: str
    file_name: Optional[str]
    origin_file: str
    mos: float
    light: float
    color: float
    noise: float
    exposure: float
    nature: float
    content_recovery: float
    description: str

    def _gen_metadata(self):
        self.file_name = Path(self.file).name

    def _hind_infos(self):
        self.mos = -1.0
        self.light = -1.0
        self.color = -1.0
        self.noise = -1.0
        self.exposure = -1.0
        self.nature = -1.0
        self.content_recovery = -1.0
        self.description = "The image..."

    def as_test(self, for_contest: bool):
        if for_contest:
            self._hind_infos()
        self.split = "test"
        self._gen_metadata()

    def as_train(self, for_test: bool):
        if for_test:
            self._hind_infos()
        self.split = "training"
        self._gen_metadata()

@dataclass
class Group:
    id: str
    split: Optional[str]
    index: int
    category: str
    avg_mos: float
    items: list[Sample]

    def set_split(self, split: str, for_contest: bool, for_test: bool):
        self.split = split
        for item in self.items:
            if split == "training":
                item.as_train(for_test=for_test)
            elif split == "test":
                item.as_test(for_contest=for_contest)


def find_by_stem(dir_path: Path, stem: str):
    for p in dir_path.iterdir():
        if p.is_file() and p.stem == stem:
            return p
    return None

def read_dataset_from_txt(for_contest: bool) -> list[Sample]:
    temp: dict = {}
    with open(DATASET_PATH / "data2.txt", "r") as f:
        head_skipped = False
        for line in f:
            if not head_skipped:
                head_skipped = True
                continue
            filename, mos, description = line.strip().split(maxsplit=2)
            temp[filename] = {
                "mos": float(mos),
                "description": description
            }
    datasets: list[Sample] = []
    with open(DATASET_PATH / "shuxing.txt", "r") as f:
        head_skipped = False
        for line in f:
            if not head_skipped:
                head_skipped = True
                continue
            filename, light, color, noise, exposure, nature, content_recovery = line.strip().split(maxsplit=7)
            id, category, index, model, suffix = parse_info_from_filename(filename)

            if for_contest:
                if not DATASET_FILENAME_DICT_PATH.exists():
                    raise Exception("you should rename dataset first")
                filename_dict = read_json(DATASET_FILENAME_DICT_PATH)
                id, _, _, _, _ = parse_info_from_filename(filename_dict[filename])

            exist_item = temp[filename]
            if exist_item is None:
                print(f"id {filename} not exist")
                continue
            file = DATASET_PATH / "data" / f"{id}.{suffix}"
            datasets.append(Sample(
                id=id,
                split=None,
                index=index,
                category=category,
                model=model,
                file=str(file.relative_to(ROOT_PATH)),
                file_name=None,
                origin_file=str(find_by_stem(DATASET_PATH / "low-light", f"{category[:1]}_{index}").relative_to(ROOT_PATH)),
                light=float(light),
                color=float(color),
                noise=float(noise),
                exposure=float(exposure),
                nature=float(nature),
                content_recovery=float(content_recovery),
                mos=float(exist_item["mos"]),
                description=exist_item["description"],
            ))
    return datasets

def group_dataset_by_origin(datasets: list[Sample]) -> list[Group]:
    group_datasets: dict[str, Group] = {}
    for dataset in datasets:
        group_id = f"{dataset.category}_{dataset.index}"
        group_dataset = group_datasets.get(group_id, None)
        if group_dataset is None:
            group_dataset = Group(
                id=group_id,
                split=None,
                index=dataset.index,
                category=dataset.category,
                avg_mos=0,
                items=[],
            )
        group_dataset.avg_mos += dataset.mos
        group_dataset.items.append(dataset)
        group_datasets[group_id] = group_dataset
    results = list(group_datasets.values())
    for result in results:
        result.avg_mos /= len(result.items)
    return results


ItemT = TypeVar('ItemT')
def bucket_by_unit_interval(data: list[ItemT], field_getter: Callable[[ItemT], float]) -> dict[tuple[int, int], list[Group]]:
    if not data:
        return {}

    data = sorted(data, key=field_getter)

    min_v = field_getter(data[0])
    max_v = field_getter(data[-1])

    start = floor(min_v)
    end = ceil(max_v)

    buckets = {(i, i + 1): [] for i in range(start, end)}

    for item in data:
        v = field_getter(item)
        idx = floor(v)
        if idx >= end:
            idx = end - 1
        buckets[(idx, idx + 1)].append(item)

    return buckets

FieldT = TypeVar('FieldT')
def split_by_field(data: list[ItemT], field_getter: Callable[[ItemT], FieldT]) -> dict[FieldT, list[ItemT]]:
    groups: dict[FieldT, list[ItemT]] = {}
    for item in data:
        attr = field_getter(item)
        if attr not in groups:
            groups[attr] = []
        groups[attr].append(item)
    return groups

def split_8_2(total: int, carry_err: float) -> tuple[int, int, float]:
    ideal_test = total * 0.2 + carry_err
    test_count = round(ideal_test)
    test_count = max(0, min(test_count, total))
    new_err = ideal_test - test_count
    train_count = total - test_count
    return train_count, test_count, new_err

def main(for_contest: bool, for_test: bool):
    rand = create_rng_with_seed()

    datasets = read_dataset_from_txt(for_contest=for_contest)
    group = group_dataset_by_origin(datasets=datasets)

    buckets = bucket_by_unit_interval(group, lambda group_item: group_item.avg_mos)
    all_groups: list[Group] = []
    for _, bucket in buckets.items():
        category_buckets = split_by_field(bucket, lambda bucket_item: bucket_item.category)
        bucket_train: list[Group] = []
        bucket_test: list[Group] = []
        split_error = 0.0
        for category, category_bucket in category_buckets.items():
            all_groups += category_bucket
            bucket_size = len(category_bucket)
            train_count, _, split_error = split_8_2(bucket_size, split_error)
            rand.shuffle(category_bucket)
            bucket_train += category_bucket[:train_count]
            bucket_test += category_bucket[train_count:]
        for group in bucket_train:
            group.set_split("training", for_contest=for_contest, for_test=for_test)
        for group in bucket_test:
            group.set_split("test", for_contest=for_contest, for_test=for_test)
    all_groups.sort(key=lambda x: (x.category, x.avg_mos))
    split_distribution = pandas.DataFrame([asdict(group) for group in all_groups])
    split_distribution = split_distribution.drop(columns=["items"])
    split_distribution.to_csv(ROOT_PATH / f"split_distribution.csv", index=False)

    datasets = split_by_field(datasets, lambda dataset_item: dataset_item.split)

    for split, dataset in datasets.items():
        if for_contest:
            for dataset_item in dataset:
                origin_path = (ROOT_PATH / dataset_item.file).resolve()
                target_base_path = origin_path.parent.parent / split
                target_base_path.mkdir(exist_ok=True, parents=True)
                target_path = target_base_path / origin_path.name
                dataset_item.file = str(target_path.relative_to(ROOT_PATH))
                shutil.copy2(origin_path, target_path)
        dataset.sort(key=lambda x: (x.split, x.category, x.index, x.id))
        data_frame = pandas.DataFrame([asdict(item) for item in dataset])
        drop_columns = ["split", "index", "category"]
        if for_contest:
            drop_columns += ["model", "origin_file"]
            if split == "test":
                drop_columns += ["mos", "light", "color", "noise", "exposure", "nature", "content_recovery"]
        data_frame = data_frame.drop(columns=drop_columns)
        output_name = "" if for_contest else "-release"
        data_frame.drop(columns=["file_name"]).to_json(ROOT_PATH / f"MLE-{split}{output_name}.json", orient="records", index=False, indent=2)
        data_frame.drop(columns=["file"]).to_csv(DATASET_PATH / split / "metadata.csv", index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--for-contest",
        action="store_true",
        help="enable contest mode"
    )
    parser.add_argument(
        "--for-test",
        action="store_true",
        help="enable test mode"
    )
    args = parser.parse_args()

    main(for_contest=args.for_contest, for_test=args.for_test)
