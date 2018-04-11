# Automatic query correction & completion project 

## Description

### Define a baseline for query correction

* tokenize text into words (use spacy or a "naive" tokenization)
* use an existing tool for isolated non-word detection and correction (e.g. hanspell)
* rerank candidates by using a probabilistic n-gram language model (LM)

## Usage

### Process wikipedia dumps

Complete process to
* download a .bz2 wikipedia dump file
* decompress the archive
* extract plain text from wikipedia xml file (using the [WikiExtractor.py](https://github.com/attardi/wikiextractor) script)
* split text into sentences and preprocess them
    * lowercase text
    * remove digits
    * remove punctuation marks
    * remove non Latin characters
    * \[*FIXME*\]: uses the external [regex](https://pypi.python.org/pypi/regex/) library, therefore it's quite slow
* count the number of occurrences of tokens (words and characters)
* plot the count and coverage of tokens with respect to a minimum number of occurrences filter
* filter the list of words with respect to their number of occurrences

As a result, this process allows us to define
* a word vocabulary
* the textual corpus needed to train a n-gram LM

```bash
$ scripts/prepare_wikipedia -h
usage: prepare_wikipedia [-h] conf

Download, decompress, extract and clean wikipedia dump data

positional arguments:
    conf        input config file (yml)

optional arguments:
    -h, --help  show this help message and exit
```

### Train n-gram language models

Use the [SRILM](http://www.speech.sri.com/projects/srilm/) toolkit to
* generate n-gram counts based on a word vocabulary and a sentence-per-line corpus
* estimate an open-class language model using the modified Knesser-Ney smoothing technnique

The resulting language model will allow us to compute the log-probability of a sequence of words.

```bash
$ scripts/train_ngram_lm -h
Objective: train a probabilistic n-gram language model

Usage:   scripts/train_ngram_lm <yaml_config_file>
Example: scripts/train_ngram_lm conf/model/config_train_lm_wiki-fr.yml
```


## Docker execution

### Process wikipedia dumps 

```bash
$ docker-compose run --rm devel \
    scripts/prepare_wikipedia \
    conf/data/config_download_clean_wiki-fr.yml
```

Configuration

```yaml
---
res: /mnt/data/ml/qwant/datasets/wikipedia/fr-articles/
actions:
  - download
  - decompress
  - extract
  - preprocess
  - plot_word_occurrences
  - define_word_vocabulary
  - plot_char_occurrences
  - define_char_vocabulary
download:
  input: https://dumps.wikimedia.org/frwiki/latest/frwiki-latest-pages-articles.xml.bz2
  output: frwiki-latest-pages-articles.xml.bz2
decompress:
  input: frwiki-latest-pages-articles.xml.bz2
  output: frwiki-latest-pages-articles.xml
extract:
  input: frwiki-latest-pages-articles.xml
  output: frwiki-latest-pages-articles.jsonl
  args:
    - --quiet
    - --json
    - --bytes 30G
    - --processes 2
    - --no-templates
    - --filter_disambig_pages
    - --min_text_length 50
preprocess:
  input: frwiki-latest-pages-articles.jsonl
  output: frwiki-latest-pages-articles.txt
  kwargs:
    ignore_digits: True
    apostrophe: fr
    ignore_punctuation: noise-a
    tostrip: False
    keepalnum: True
plot_word_occurrences:
  input: frwiki-latest-pages-articles.txt
  output: plots/frwiki-latest-pages-articles_words.png
  kwargs:
    mins: [1, 2, 3, 5, 10, 100]
    left_lim: [0, 3000000]
    right_lim: [95, 100.4]
define_word_vocabulary:
  input: frwiki-latest-pages-articles.txt
  output: frwiki-latest-pages-articles_voc-top500k-words.json
  kwargs:
    topn: 500000
plot_char_occurrences:
  input: frwiki-latest-pages-articles.txt
  output: plots/frwiki-latest-pages-articles_chars.png
  kwargs:
    mins: [1, 2, 3, 5, 10, 100, 1000, 10000, 100000]
    left_lim: [0, 750]
    right_lim: [99.5, 100.04]
define_char_vocabulary:
    input: frwiki-latest-pages-articles.txt
    output: frwiki-latest-pages-articles_voc-chars.json
```

Output

```
INFO [2018-04-10 11:50:58,460] [ccquery] Executing download action
INFO [2018-04-10 11:50:58,461] [ccquery.preprocessing.wiki_extraction] Download wikipedia dump
INFO [2018-04-10 12:22:37,021] [ccquery] Executing decompress action
INFO [2018-04-10 12:22:37,022] [ccquery.preprocessing.wiki_extraction] Decompress wikipedia dump
INFO [2018-04-10 12:33:29,653] [ccquery] Executing extract action
INFO [2018-04-10 12:33:29,653] [ccquery.preprocessing.wiki_extraction] Extract plain text from Wikipedia by executing the command:
    WikiExtractor.py \
        frwiki-latest-pages-articles.xml \
        --quiet \
        --json \
        --bytes 30G \
        --processes 2 \
        --no-templates \
        --filter_disambig_pages \
        --min_text_length 50 \
        -o - > frwiki-latest-pages-articles.jsonl
INFO [2018-04-10 14:31:33,687] [ccquery] Executing preprocess action
INFO [2018-04-10 14:31:33,687] [ccquery.preprocessing.wiki_extraction] Extract clean sentences
INFO [2018-04-10 17:01:10,611] [ccquery] Executing plot_word_occurrences action
INFO [2018-04-10 17:06:48,838] [ccquery.preprocessing.vocabulary] Read 2,522,623 words with 589,297,641 occurrences
INFO [2018-04-10 17:06:48,838] [ccquery.preprocessing.vocabulary] Save histogram on word occurrences
INFO [2018-04-10 17:06:51,791] [ccquery] Executing define_word_vocabulary action
INFO [2018-04-10 17:06:54,006] [ccquery.preprocessing.vocabulary] Saved
    500,000 words out of 2,522,623
    (19.82% unique words, 99.24% coverage of word occurrences)
INFO [2018-04-10 17:06:54,089] [ccquery.preprocessing.vocabulary] Save word counts in json file
INFO [2018-04-10 17:06:56,272] [ccquery.preprocessing.vocabulary] Save words in text file
INFO [2018-04-10 17:06:57,198] [ccquery] Executing plot_char_occurrences action
INFO [2018-04-10 17:23:13,536] [ccquery.preprocessing.vocabulary] Read 641 chars with 3,400,942,936 occurrences
INFO [2018-04-10 17:23:13,536] [ccquery.preprocessing.vocabulary] Save histogram on char occurrences
INFO [2018-04-10 17:23:13,845] [ccquery] Executing define_char_vocabulary action
INFO [2018-04-10 17:23:13,845] [ccquery.preprocessing.vocabulary] Save char counts in json file
INFO [2018-04-10 17:23:13,847] [ccquery.preprocessing.vocabulary] Save chars in text file
INFO [2018-04-10 17:23:13,848] [ccquery] Finished.
```

The plot on the word occurrences  
![Word occurrences](data/frwiki-latest-pages-articles_words.png)

The plot on the character occurrences  
![Character occurrences](data/frwiki-latest-pages-articles_chars.png)

### Train n-gram language models

```bash
$ docker-compose run --rm srilm \
    scripts/train_ngram_lm \
    conf/model/config_train_lm_wiki-fr.yml
```

Configuration

```yaml
---
order: 3
vocab: /mnt/data/ml/qwant/datasets/wikipedia/fr-articles/frwiki-latest-pages-articles_voc-top500k-words.txt
corpus: /mnt/data/ml/qwant/datasets/wikipedia/fr-articles/frwiki-latest-pages-articles.txt
smoothing: -gt1min 0 -kndiscount2 -gt2min 0 -interpolate2 -kndiscount3 -gt3min 0 -interpolate3
pruning: 1e-9
counts: /mnt/data/ml/qwant/models/ngrams/wikipedia/fr-articles/counts_order3_500kwords_frwiki-latest-pages-articles.txt
model: /mnt/data/ml/qwant/models/ngrams/wikipedia/fr-articles/lm_order3_500kwords_modKN_prune1e-9_frwiki-latest-pages-articles.arpa
```

Output

```bash
Launch n-gram counting
    ngram-count \
        -order 3 \
        -text frwiki-latest-pages-articles.txt \
        -unk -vocab frwiki-latest-pages-articles_voc-top500k-words.txt \
        -sort -write counts_order3_500kwords_frwiki-latest-pages-articles.txt \
        -debug 2

29,642,700 sentences, 589,297,641 words, 4,486,608 OOVs
Finished at 09:44:22, after 486 seconds

Launch LM training
    make-big-lm \
        -order 3 \
        -unk -read counts_order3_500kwords_frwiki-latest-pages-articles.txt \
        -name aux -lm lm_order3_500kwords_modKN_prune1e-9_frwiki-latest-pages-articles.arpa \
        -gt1min 0 -kndiscount2 -gt2min 0 -interpolate2 -kndiscount3 -gt3min 0 -interpolate3 \
        -prune 1e-9 \
        -debug 2

using ModKneserNey for 1-grams
using ModKneserNey for 2-grams
using ModKneserNey for 3-grams
warning: distributing 0.000334545 left-over probability mass over all 500002 words

discarded       1 2-gram contexts containing pseudo-events
discarded  453443 3-gram contexts containing pseudo-events

pruned    3273196 2-grams
pruned   90005564 3-grams

writing    500003 1-grams
writing  34918094 2-grams
writing  64693601 3-grams

Finished at 10:31:58, after 2856 seconds

Generated a model of 2.9G
```
