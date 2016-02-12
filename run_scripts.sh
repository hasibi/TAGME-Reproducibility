#!/usr/bin/env bash

# NOTES:
#   1. Before running this script, download the `data` folder from `http://hasibi.com/files/res/data.tar.gz`
#      and put it under the main repository directory (i.e., tagme-rep/data)
#   2. For all of the experiments we get all linked entities by setting the threshold to 0.
#      Later, in the evaluation scripts we filter out the entities below a certain threshold.

# ===============
# Reproducibility
# ===============

# TAGME-API - Wiki-Disamb30
python -m nordlys.tagme.tagme_api -data wiki-disamb30
python -m scripts.evaluator_disamb qrels/qrels_wiki-disamb30.txt output/wiki-disamb30_tagmeAPI.txt

# TAGME-API - Wiki-Annot30
python -m nordlys.tagme.tagme_api -data wiki-annot30
python -m scripts.evaluator_annot qrels/qrels_wiki-annot30.txt output/wiki-annot30_tagmeAPI.txt 0.2
python -m scripts.evaluator_topics qrels/qrels_wiki-annot30.txt output/wiki-annot30_tagmeAPI.txt 0.2

# TAGME-our(wiki10)
python -m nordlys.tagme.tagme -data wiki-annot30 
python -m scripts.evaluator_annot qrels/qrels_wiki-annot30.txt output/wiki-annot30_tagme_wiki10.txt 0.2
python -m scripts.evaluator_topics qrels/qrels_wiki-annot30.txt output/wiki-annot30_tagme_wiki10.txt 0.2

# Dexter
python -m nordlys.tagme.dexter_api -data wiki-annot30 
python -m scripts.evaluator_annot qrels/qrels_wiki-annot30.txt output/wiki-annot30_dexter.txt 0.2
python -m scripts.evaluator_topics qrels/qrels_wiki-annot30.txt output/wiki-annot30_dexter.txt 0.2



# ================
# Generalizability
# ================

# TAGME API - ERD-dev
python -m nordlys.tagme.tagme_api -data erd-dev
python -m scripts.to_elq output/erd-dev_tagmeAPI.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_erd-dev.txt output/erd-dev_tagmeAPI_0.1.elq

# TAGME API - Y-ERD
python -m nordlys.tagme.tagme_api -data y-erd
python -m scripts.to_elq output/y-erd_tagmeAPI.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_y-erd.txt output/y-erd_tagmeAPI_0.1.elq

#TAGME-wp10 - ERD-dev
python -m nordlys.tagme.tagme -data erd-dev 
python -m scripts.to_elq output/erd-dev_tagme_wiki10.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_erd-dev.txt output/erd-dev_tagme_wiki10_0.1.elq

#TAGME-wp10 - Y-ERD
python -m nordlys.tagme.tagme -data y-erd 
python -m scripts.to_elq output/y-erd_tagme_wiki10.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_y-erd.txt output/y-erd_tagme_wiki10_0.1.elq

#TAGME-wp12 - ERD-dev
python -m nordlys.tagme.tagme -data erd-dev 
python -m scripts.to_elq output/erd-dev_tagme_wiki12.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_erd-dev.txt output/erd-dev_tagme_wiki12_0.1.elq

#TAGME-wp12 - Y-ERD
python -m nordlys.tagme.tagme -data y-erd 
python -m scripts.to_elq output/y-erd_tagme_wiki12.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_y-erd.txt output/y-erd_tagme_wiki12_0.1.elq

# Dexter - ERD-dev
python -m nordlys.tagme.dexter_api -data erd-dev 
python -m scripts.to_elq output/erd-dev_dexter.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_erd-dev.txt output/erd-dev_dexter_0.1.elq

# Dexter - Y-ERD
python -m nordlys.tagme.dexter_api -data y-erd 
python -m scripts.to_elq output/y-erd_dexter.txt 0.1
python -m scripts.evaluator_strict qrels/qrels_y-erd.txt output/y-erd_dexter_0.1.elq
