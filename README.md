# TAGME reproducibility

This repository contains resources developed within the following paper:

	F. Hasibi, K. Balog, and S.E. Bratsberg. “On the reproducibility of the TAGME Entity Linking System”,
	In proceedings of 38th European Conference on Information Retrieval (ECIR ’16), March 2016.

This study is an effort aimed at reproducing the results presented in the TAGME paper [1].

We received invaluable comments from the TAGME authors about their system, and we made these notes available [here](authors_comments.md).
These comments may inform future efforts related to the re-implementation of the TAGME system, as they cannot be found in the original paper.

This repository is structured as follows:

- `nordlys/`: Code required for running entity linkers.
- `scripts/`: Evaluation scripts.
- `lib/`: Contains libraries.
- `run-scripts.sh`: Single script that runs all the scripts for getting the results of the paper.
- [authors_comments.md](authors_comments.md): Comments from the TAGME authors and notes about our experiments.

Other resources involved in this project are [data](http://hasibi.com/files/res/data.tar.gz), [qrels](http://hasibi.com/files/res/qrels.tar.gz), and [runs](http://hasibi.com/files/res/runs.tar.gz), which are described below.

**Note:** Before running the code (`run-scripts.sh`), please read the [setup](setup.md) file and build all the required resources.


## Data

The following data files can be downloaded from [here](http://hasibi.com/files/res/data.tar.gz):

  - **Wiki-disamb30** and **Wiki-annot30**: The original datasets are published [here](http://acube.di.unipi.it/tagme-dataset/). We complement the snippets with numerical IDS, as IDs are not contained in the original datasets.
  - **ERD-dev**: The dataset is originally published by the [ERD Challenge](http://web-ngram.research.microsoft.com/ERD2014); we use it in our generalizability experiments. The files related to this dataset are prefixed with `Trec_beta`.
  - **Y-ERD**: This dataset is originally published in [2] and is available [here](http://bit.ly/ictir2015-elq). The dataset is used in our generalizability experiments.
  - **Freebase snapshot**: A snapshot of Freebase containing only proper noun entities (e.g., people and locations) is made available by the ERD challenge and is used for filtering entities in the generalizability experiments.


## Qrels

The qrel files can be downloaded from [here](http://hasibi.com/files/res/qrels.tar.gz). All qrels are tab-delimited and their format is as follows:

  - **Wiki-disamb30** and **Wiki-annot30**: The columns represent: snippet ID, confidence score, Wikipedia URI, and Wikipedia page id. The last column is not considered in the evaluation scripts.
  - **ERD-dev** and **Y-ERD**: The columns represent: query ID, confidence score (always 1), and Wikipedia URI. The entities after the second column represent an interpretation set (entity set) of the query. (If a query has multiple interpretations, there are multiple lines with that query ID.)


## Runs

The run files can be downloaded from [here](http://hasibi.com/files/res/runs.tar.gz), and categorized into two groups: reproducibility and generalizability.

  - **Reproducibility**: The naming convention for these files is *XX_YY.txt*, where XX represents the dataset and YY is the name of the method. For each file, only the first 4 columns are considered for the evaluation, which are: snippet ID, confidence score, Wikipedia URI, and mention.
  - **Generalizability**: These files are named as *XX_YY_ZZ.elq*, where XX is the dataset, YY is the name of the method, and ZZ is the entity linking threshold used for evaluation. The format of these files is similar to the corresponding qrel files.


## Contact

If you have any questions, feel free to contact Faegheh Hasibi at <faegheh.hasibi@idi.ntnu.no>.

```
[1] P. Ferragina and U. Scaiella. TAGME: On-the-fly annotation of short text fragments (by Wikipedia entities). In Proceedings of CIKM '10, pages 1625–1628, 2010.
[2] F. Hasibi, K. Balog, and S. E. Bratsberg. Entity Linking in Queries: Tasks and Evaluation. In Proceedings of ICTIR ’15, pages 171–180, 2015.
```
