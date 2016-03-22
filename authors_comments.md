# Authors' comments

In our study aimed at reproducing the results in [1], only parts of the results were reproducible.
Later on, the TAGME authors clarified some of the issues that surfaced.
We list these comments below, as they may inform future efforts related to the re-implementation of TAGME.

We also include some additional notes on our experiments, which clarify our reasoning behind certain decisions.

## TAGME authors' comments

*The comments below are taken from our personal communication with the TAGME authors. Most of these are direct quotes, but we made minor editorial changes and structured them by topic.*

**Important note:** In this section "we" refers to the TAGME authors; to avoid ambiguity, we will refer to our implementation as the "ECIR'16 implementation."

### Implementation:

- The TAGME paper [1] represents “version 1” of TAGME, while the source code and the TAGME API are “version 2”. In the second version, the epsilon value been changed and the value of tau has been decreased.

- TAGME uses wiki page-to-page link records (enwiki-xxx-pagelinks.sql.gz), while the ECIR'16 implementation extracts links from the body of the pages (enwiki-xxx-pages-articles.xml.bz2). This affects the computation of relatedness, as the former source contains 20% more links than the latter.

- TAGME version 2 uses a list of stop words to create alternative spots and we add them to the list of available spots during pre-processing phase. In other words, when a spot like "president of the united states" is found, 2 spots are created: (i) "president of the united states", and "president united states". Then these two spots are added to the anchor dictionary. However, TAGME does not perform any stop word removal during the parsing phase.

- In TAGME version 2 the parsing method for anchors starting with 'the','a','an' has changed. We ignore those prefixes and use only the remaining part. So version 2 can never find 'the firebrand' but only 'firebrand'.

-  TAGME performs two extra filtering before the pruning step.
  * Filtering of mentions that are contained in a longer mention.
  * Filtering base on link probability threshold. In Version 1 this threshold was set to 0.02, but in version 2, it is set to 0.1. The code related to this filtering is line 87 of `TagmeParser.java` in TAGME source code:
  ```
  this.minLinkProb = TagmeConfig.get().getSetting(MODULE).getFloatParam(PARAM_MIN_LP, DEFAULT_MIN_LP);
  ```

### Evaluation:

- For the experiments in [1], we used only 1.4M out of 2M snippets from WIKI-DISAMB30, as Weka could not load more than that into memory. From WIKI-ANNOT30 we used all snippets, the difference is merely a matter of approximation.

- The evaluation metrics used for end-to-end performance (topics and annot metrics) are micro-averaged.

- The evaluation metrics for the disambiguation phase are micro-averaged (prec = TP / TP+FP, recall = TP / total number of test cases) and are computed as follows:
  1. annotate the fragment
  2. search for the mention in the result
  3. if you don't find it, ignore it
  4. if you find it:
      - if it is correct, increment the number of the true positive
      - if it's not correct, increment the number of the false positive



## Our additional comments on the TAGME authors' comments :)

- For the sake of reproducibility, we had to use the closest Wikipedia dump to the original experiments, that is dump from April 2010. The page-to-page link records for this dump are not available any more and therefore we had to extract them from the body of Wikipedia pages (enwiki-20100408-pages-articles.xml.bz2).
- The TAGME datasets (Wiki-annot and Wiki-disamb) contain IDs of the pages, which have changed over time in Wikipedia. We addressed this issue as follows:
  * We converted the page ids of datasets to the corresponding page titles the dump of 2010.
  * For all the experiments, we converted the page titles to URIs based on the [Wikipedia instructions](https://en.wikipedia.org/wiki/Wikipedia:Page_name#Spaces.2C_underscores_and_character_coding).

  Using this method, the URIs used in our experiments are consistent with the TAGME datasets. Since the generalizability datasets are originally created based on DBpedia URIs, they result in minor difference (due to encodings). However, the differences are negligible and do not affect the overall conclusion.


```
[1] P. Ferragina and U. Scaiella. TAGME: On-the-fly annotation of short text fragments (by Wikipedia entities). In Proceedings of CIKM '10, pages 1625–1628, 2010.
```
