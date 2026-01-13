---
tags:
- image-quality
- low-light
- enhancement
---

# MLEDataset

## Introduce

We introduce the Multi-annotated and multimodal Low light image Enhancement (MLE) dataset. This dataset consists of 1000 Enhanced Low-light Images (ELIs), which were obtained by applying 10 Low-light Image Enhancement Algorithms (LIEAs) to 100 low-light images. Each image has been meticulously annotated by subjective studies to obtain multiple attribute annotations (light, color, noise, exposure, nature, and content recovery), quality scores, and textual descriptions. The training set consists of 800 ELIs along with their corresponding annotation scores. The test set includes the remaining 200 ELIs. Spearman Rank-order Correlation Coefficient (SRCC) and Pearson Linear Correlation Coefficient (PLCC) are the key indicators for ranking the performance of the models. The final ranking will be based on the average value of the two. Under the same numerical conditions, SRCC takes precedence.

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
