TAGME reproducibility
=====================

This repository contains resources developed within the following paper:

	F. Hasibi, K. Balog, and S.E. Bratsberg. “On the reproducibility of  the TAGME Entity Linking System”, In proceedings of 38th European Conference on Information Retrieval (ECIR ’16), Padova, Italy, March 2016.
	
The paper is an affort on reporoducing the results presented in [1].
We recieved invaluable feedbacks from the TAGME authors about their system, which are available at ``tagme_authors_comments.md``.
We believe these comments facilitate future efforts on reproducing TAGME results.


This repository is structured as follows:
  
- `nordlys/`: Code required for running entity linkers.
- `scripts/`: Evaluation scripts.
- `run-scripts.sh`: All the scripts for gettings the results of the paper.

Other resources involved in this project are [data](http://hasibi.com/files/res/data.tar.gz), [qrels](http://hasibi.com/files/res/qrels.tar.gz), and [runs](http://hasibi.com/files/res/runs.tar.gz), which are described below.

**Note:** Before running the code, please read the `setup.md` file and build all the required resources.


## Data

All data sources can be downloaded from [here](http://hasibi.com/files/res/data.tar.gz) and include:

  - **Wiki-disamb30** and **Wiki-annot30**: The original datasets are published [here](http://acube.di.unipi.it/tagme-dataset/). As the original datasets do not contain snippets IDs, we assigned numerical IDs to the snippets.
  - **ERD-dev**: The dataset is originaly published by the [ERD Challenge](http://web-ngram.research.microsoft.com/ERD2014), and we use it for generalizibility experiments. The files related to this dataset are prefixed by `Trec_beta`.
  - **Y-ERD**: This dataset is originily published in [2] and is available [here](http://bit.ly/ictir2015-elq). The dataset is used for generalizibility experiments.
  - **Freebase snapshot**: A snapshot of Freebase containing only proper noun entities (e.g., people and locations) is published by the ERD challenge and is used for filtering entities in the generalizibility experiments.


## Qrels

The qrel files are under ``qrels/``. All qrels are tab-delimited and their format is as follows:

  - **Wiki-disamb30** and **Wiki-annot30**: The columns represent: snippet ID, confidence score, Wikipedia URI, and Wikipedia page id. The last column is not considered in the evaluation scripts.
  - **ERD-dev** and **Y-ERD**: The columns represent: query ID and confidence score (always 1), and Wikipedia URI. All the entities after the second column represent the interpretation set (entity set) of the query.



## Runs

The files are under ``runs/``, categorized into two groups: Reproducibility (``runs/reproducibility/``) and Generalizability (``runs/generalizability/``). The naming convention for all the run files is *XXX_YYY.txt*, where XXX represents the dataset and YYY represents the name of the method. All qrels are tab-delimited and their format is as follows:

  - **Wiki-disamb30_YYY.txt** and **Wiki-annot30_YYY.txt**: Only the first 4 columns are considered for the evaluation, which are: snippet ID, confidence score, Wikipedia URI, and mention.
  - **ERD-dev_YYY.txt** and **Y-erd_YYY.txt**: The format is similar to the corresponding qrel files.


```
[1] P. Ferragina and U. Scaiella. TAGME: On-the-fly annotation of short text fragments (by Wikipedia entities). In Proceedings of CIKM '10, pages 1625–1628, 2010.
[2] F. Hasibi, K. Balog, and S. E. Bratsberg. Entity Linking in Queries: Tasks and Evaluation. In Proceedings of the ICTIR ’15, pages 171–180, 2015.
```