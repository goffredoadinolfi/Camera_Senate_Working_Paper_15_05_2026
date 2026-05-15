# Python scripts for parliamentary corpus analysis

This repository contains the Python scripts used for the article's computational workflow. The scripts are organised according to the main stages of the analysis: downloading parliamentary records, extracting text, counting sittings and words, producing keyword-count datasets, and generating the figures included in the article.

The scripts were developed and executed in **Spyder 6**, using **Python 3.11.11** packaged by **conda-forge**, within an **IPython 8.37.0** interactive environment.

## Repository structure

### 1_Downloading_Act_Extract_Txt

This folder contains the scripts used to download parliamentary records and extract text from PDF files.

The workflow includes two operations:

1. automated downloading of PDF files from public parliamentary repositories;
2. conversion of the downloaded PDF files into plain-text TXT files.

The download scripts generate or read the URLs of the parliamentary sittings, save the PDF files locally with standardised filenames, and create log files documenting the outcome of each request.

The PDF-to-TXT scripts extract textual content from the downloaded files and save one TXT file per parliamentary sitting. Where necessary, the scripts also handle two-column page layouts in order to reconstruct the reading order of the parliamentary records.

Main libraries used in this stage include:

- `requests`
- `pandas`
- `pathlib`
- `time`
- `random`
- `re`
- `PyMuPDF` / `fitz`

### 2_Count_Word_Senate_Chamber

This folder contains the scripts used to count sittings, words, characters and selected keyword occurrences in the Chamber and Senate corpora.

These scripts work on the TXT files produced in the previous stage and aggregate the results by year and parliamentary body. They produce derived datasets used for the descriptive statistics and visualisations in the article.

Typical outputs include yearly counts of:

- parliamentary sittings;
- total words;
- total characters;
- selected political keywords;
- Chamber/Senate comparisons.

Main libraries used in this stage include:

- `pandas`
- `os`
- `pathlib`
- `re`

### 3_Graph_1_2_Python_Output

This folder contains the scripts and output figures for the first two graphs.

These figures visualise the annual distribution of parliamentary activity in the Chamber and Senate corpora, including:

- total sittings by year;
- total words by year.

The graphs were generated from derived yearly datasets using `pandas` and `matplotlib`.

Main libraries used in this stage include:

- `pandas`
- `matplotlib`

### 4_Graph_3_4_War_Democracy_Socialism

This folder contains the scripts and output figures for the keyword graphs.

The scripts generate:

- a line graph comparing the annual raw occurrences of *guerra* in the Senate and Chamber corpora;
- a multi-panel figure comparing selected political keywords, including *democrazia*, *socialismo*, *suffragio*, *fascismo* and *assemblea costituente*.

The dashed line represents the Senate and the continuous line represents the Chamber. The graphs use raw yearly counts and should therefore be read together with the general corpus-size indicators, especially the yearly number of words.

Main libraries used in this stage include:

- `pandas`
- `matplotlib`
- `openpyxl`
- `os`

## Computational environment

The scripts were developed and executed in the following environment:

```text
Spyder 6
Python 3.11.11 | packaged by conda-forge
IPython 8.37.0
```

The main Python libraries used across the workflow were:

```text
requests
pandas
matplotlib
openpyxl
PyMuPDF
```

Some scripts also use standard Python libraries, including:

```text
os
pathlib
time
random
re
unicodedata
typing
```

## Reproducibility note

The scripts are provided as the preserved computational artefact used in the article. Some parts of the code were developed with the assistance of large language models and then manually checked, adapted and executed by the author. For this reason, the shared scripts, rather than the prompts alone, constitute the reproducible record of the computational workflow.

The repository aims to document the actual workflow used to move from public parliamentary records to derived textual datasets and visualisations.

## Data availability

The full processed TXT corpus may not be included in the repository if its size is too large. However, the scripts document how the corpus was produced from publicly available parliamentary records.

Where possible, the repository includes the derived datasets used to generate the figures, together with the corresponding output images.

## Suggested order of execution

A typical workflow follows this sequence:

1. download the parliamentary records in PDF format;
2. convert the PDFs into TXT files;
3. count sittings, words, characters and selected keyword occurrences;
4. aggregate the results by year and parliamentary body;
5. generate the figures used in the article.

## Citation

If this repository is cited, please refer to it as the Python code repository accompanying the article.

