## Data Loading

### Step 1: Download Datasets

+ Option 1: [HuggingFace](https://huggingface.co/datasets/CQUPT-HuBo90/MLEDataset)
+ Option 2: [GitHub](https://github.com/CQUPT-HuBo90/MLEDataset)
+ Option 3: [BaiduYun](https://pan.baidu.com/s/1SrULywHnR_e3W70SuAaJ-w)（提取码：xmcr）

### Step 2: Load Dataset Using huggingface

Install `datasets[vision]`:

```shell
pip install datasets[vision]
```

Sample code:

```python
from datasets import DownloadConfig, load_dataset

# loading dataset
ledataset_origin = load_dataset(
    path="CQUPT-HuBo90/MLEDataset", # or use the full path if you had already downloaded dataset to custom local path.
    split="train",
)
```
