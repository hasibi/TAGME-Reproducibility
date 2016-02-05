#TAGME reproducibility

This repository contains resources developed for the paper *"On the Reproducibility of the TAGME Entity Linking System"*.


## Data

The following datasets are used in the paper:

  - **Wiki-disamb30** and **Wiki-annot30**: The original datasets are available [here](http://acube.di.unipi.it/tagme-dataset/). As the original datasets do not contain snippets IDs, we assigned numerical IDs to the snippets. The snippets with the corresponding IDs are under ``data/``.
  - **ERD-dev**: The dataset is available from the [ERD Challenge website](http://web-ngram.research.microsoft.com/ERD2014).
  - **Y-ERD**: The dataset is available [here](http://bit.ly/ictir2015-elq).


## Qrels

The qrel files are under ``qrels/``. All qrels are tab-delimited and their format is as follows:

  - **Wiki-disamb30** and **Wiki-annot30**: The columns represent: snippet ID, confidence score, Wikipedia URI, and Wikipedia page id. The last column is not considered in the evaluation scripts.
  - **ERD-dev** and **Y-ERD**: The columns represent: query ID and confidence score (always 1), and Wikipedia URI. All the entities after the second column represent the interpretation set (entity set) of the query.



## Runs

The files are under ``runs/``, categorized into two groups: Reproducibility (``runs/reproducibility/``) and Generalizability (``runs/generalizability/``). The naming convention for all the run files is *XXX_YYY.txt*, where XXX represents the dataset and YYY represents the name of the method. All qrels are tab-delimited and their format is as follows:

  - **Wiki-disamb30_YYY.txt** and **Wiki-annot30_YYY.txt**: Only the first 4 columns are considered for the evaluation, which are: snippet ID, confidence score, Wikipedia URI, and mention.
  - **ERD-dev_YYY.txt** and **Y-erd_YYY.txt**: The format is similar to the corresponding qrel files.

## Evaluation scripts

The evaluation metrics are under ``evaluation-scripts/`` and are as follows:

  - **eval_disamb.py**: Used to evaluate disambiguation phase. 
  - **eval_annot.py** and **eval_topics.py**: Used to evaluate end-to-end performance. The scripts Compute filter out results below a specific threshold (i.e.; 0.2) and compute *annotation* and *topics* metrics, respectively.
  - **eval_strict.py**: Used to evaluate the performance for the task of entity linking in queries.



## Instructions to run the evaluation scripts

To run the evaluation scripts, use the command ``python evaluation-scripts/eval_XXX.py qrels/qrels_YYY.txt runs/reproducibility/ZZZ.txt``. Here is some examples:

*Reproducibility:*
- ``python evaluation-scripts/eval_disamb.py qrels/qrels_Wiki-disamb30.txt runs/reproducibility/Wiki-disamb30_TAGME-API.txt``
- ``python evaluation-scripts/eval_annot.py qrels/qrels_Wiki-annot30.txt runs/reproducibility/Wiki-annot30_TAGME-wp10.txt``
- ``python evaluation-scripts/eval_topics.py qrels/qrels_Wiki-annot30.txt runs/reproducibility/Wiki-annot30_Dexter.txt``
	
*Generalizability:*
- ``python evaluation-scripts/eval_strict.py qrels/qrels_Y-ERD.txt runs/generalizability/Y-ERD_TAGME-wp12.txt``
- ``python evaluation-scripts/eval_strict.py qrels/qrels_ERD-dev.txt runs/generalizability/ERD-dev_TAGME-API.txt``
