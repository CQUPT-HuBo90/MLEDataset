from datasets import load_dataset  # ty:ignore[unresolved-import]

def main():
    dataset = load_dataset(
        "CQUPT-HuBo90/MLEDataset",
        split="train",
    )
    for i in range(5):
        print(dataset[i])


if __name__ == '__main__':
    main()
