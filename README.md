# Python scripts for parliamentary corpus analysis

This repository contains the Python scripts used for the article's computational workflow. The scripts are organised according to the main stages of the analysis: downloading parliamentary records in PDF format, reading textual content from PDF files, counting sittings and words, producing keyword-count datasets, and generating the figures included in the article.

The parliamentary records used in this study are institutional materials of the Chamber of Deputies and the Senate and are publicly available for consultation and use through their official websites. However, since it is not entirely clear whether the full corpus may be redistributed by third parties through a public repository, the downloaded database of sittings has not been included in the GitHub repository. For reasons of caution, the repository provides the Python scripts, derived datasets and figures used in the article, while the original records remain accessible from the official institutional sources, subject to their continued availability and current access conditions.

The scripts were developed and executed in **Spyder 6**, using **Python 3.11.11** packaged by **conda-forge**, within an **IPython 8.37.0** interactive environment.

## Repository structure

### 1_Downloading_PDF_Records

This folder contains the scripts used to download parliamentary records in PDF format from the public parliamentary repositories of the Chamber of Deputies and the Senate.

The download scripts generate or read the URLs of the parliamentary sittings, save the PDF files locally with standardised filenames, and create log files documenting the outcome of each request.

The acquisition procedure was designed as a controlled and incremental form of harvesting. The scripts introduce pauses between requests and proceed through bounded chronological or institutional units, rather than through aggressive or massive simultaneous access.

Some download scripts may also appear in the separate `Camera` and `Senato` folders, which preserve the Chamber- and Senate-specific acquisition scripts used during the workflow.

Main libraries used in this stage include:

- `requests`
- `pandas`
- `pathlib`
- `time`
- `random`
- `re`

### 2_Count_Word_Senate_Chamber

This folder contains the scripts used to count sittings, words, characters and selected keyword occurrences in the Chamber and Senate corpora.

The main corpus-size dataset used for the article was produced directly from the downloaded PDF files. The counting script scans the Chamber and Senate PDF folders, extracts the year from each filename, reads the textual content of each document, counts words, and aggregates the results by year and parliamentary body. The resulting dataset is then used for the descriptive statistics and visualisations in the article.

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
- `PyPDF2`

### 3_Graph_1_2_Python_Output

This folder contains the scripts and output figures for the first two graphs.

These figures visualise the annual distribution of parliamentary activity in the Chamber and Senate corpora, including:

- total sittings by year;
- total words by year.

The graphs were generated from derived yearly datasets using `pandas`, `openpyxl` and `matplotlib`.

Main libraries used in this stage include:

- `pandas`
- `matplotlib`
- `openpyxl`
- `os`

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