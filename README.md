<img src="https://www.hq.nasa.gov/office/pao/History/diagrams/gemini4.gif" width="500"/>

# Capsule
Some tools for NLP, candidate extraction, annotation, and serialization built on top of spaCy.

Inspired by useful stuff in [snorkel](https://github.com/HazyResearch/snorkel).

***This library is very much a work in progress. Use at your own risk!***

## Requirements

- Python3
- spaCy
- (optional if you want some progress bars) tqdm

## How to use

### Searching and returning spans
The usableText class in [utils.py](https://github.com/DrPinkACN/Capsule/blob/master/capsule/utils.py) is where most of the functionality of this tool resides. The missionControl.py script shows step by step use of this tool on some FDA drug label data. Let's walk through the current working pieces:

First, import the needed pieces:

```python
from capsule.nlpDaemon import parser
from capsule import usableText
import re, pickle, json, spacy
from collections import defaultdict, Counter
```

Then, load in some data:

```python
with open('data/DrugLabels.pkl','rb') as fn:
    docs=pickle.load(fn)
````

One can then inspect each document as a separate usable text object, or intantiate all docs into a list of usableText objects, like this:

```python
utext=[]
for n,i in enumerate(docs):
    try:
        utext.append(usableText(*parser(i)))
    except:
        print('doc {} did not parse in'.format(n))
        pass
```

Now, let's see what we can do to one usable doc, now that it has been parsed and has some methods associated.

```python
>>> udoc=utext[11]
>>> udoc
doc_id: 1db301753abb4a3bb27d6e5085d817f
doc_text: Plasma-Lyte M and 5% Dextrose Injection (Multiple Electrolytes and Dextrose Injection, Type 2, USP) is indicated as a source of water, electrolytes, and calories or as an alkalinizing agent.
```
That looks simple enough. each document gets a unique id and the raw input is stored. Now we can use capsule to look for patterns and return tokens on varying scales of abstraction. This is done with regular expression spans.

```python
>>> udoc.regexFind(pattern=r'(ADJ)*(\s?NOUN)+',search_token='pos',return_token='word',leadToken=2,trailToken=2)
[{'doc_id': '1db301753abb4a3bb27d6e5085d817f',
  'return_token': [{'lead': ['and', '5'],
    'match': ['%'],
    'trail': ['Dextrose', 'Injection']},
   {'lead': ['as', 'a'], 'match': ['source'], 'trail': ['of', 'water']},
   {'lead': ['source', 'of'],
    'match': ['water'],
    'trail': [',', 'electrolytes']},
   {'lead': ['water', ','], 'match': ['electrolytes'], 'trail': [',', 'and']},
   {'lead': [',', 'and'], 'match': ['calories'], 'trail': ['or', 'as']},
   {'lead': ['an', 'alkalinizing'], 'match': ['agent'], 'trail': ['.']}],
  'sent_no': 0,
  'spans': [(19, 20),
   (118, 124),
   (128, 133),
   (135, 147),
   (153, 161),
   (184, 189)],
  'token_spans': [(6, 7), (25, 26), (27, 28), (29, 30), (32, 33), (37, 38)]}]
```

The `return_token` can be almost anything spaCy has available. The `search_token` is a little more limited. Mainly, we leave out any boolian tokens from search, not because we can't activate these later, but we haven't tested regex spans with 1s and 0s:

```python
>>> udoc.availSearchToken
['word', 'lemma', 'pos', 'tag', 'dep_label', 'ent_type', 'raw_text']

>>> udoc.availReturnToken
['word',
 'lemma',
 'pos',
 'tag',
 'dep_label',
 'prefix',
 'suffix',
 'is_oov',
 'like_url',
 'like_num',
 'like_email',
 'is_stop',
 'ent_type']
```

These spans can be captured as extity candidates, but before that, one may want to compose a set of these search pattern outputs to refine the candidate set even further. For this, there is a method available for composing many patterns together using common set functionality. The method to do this is `.compose()`, which allows you to make unions (flag: 'u'), intersections (flag: 'i'), differences (flag: 'd'), sub-span intersections (flag: 's'), and sub-span differences (flag: 'z'). The compose method accepts tuples of tuples formatted as `('flag',('patternA','tokenA'),('patternB','tokenB'))` pattern/token tuple pairs can be substituted with flag/searchA/searchB tuples to create a composition tree.

```python
>>> udoc.compose(('z',(r'(ADJ)*(\s?NOUN)+','pos'),(r'water','lemma')))
[{'doc_id': '1db301753abb4a3bb27d6e5085d8173f',
  'sent_no': 0,
  'spans': [(19, 20), (118, 124), (135, 147), (153, 161), (184, 189)],
  'token_spans': [(6, 7), (25, 26), (29, 30), (32, 33), (37, 38)]}]

>>>udoc.showTokens(udoc.compose(('z',(r'(ADJ)*(\s?NOUN)+','pos'),(r'water','lemma'))),return_token='word')
  [{'doc_id': '1db301753abb4a3bb27d6e5085d8173f',
  'return_token': [{'lead': [], 'match': ['%'], 'trail': []},
   {'lead': [], 'match': ['source'], 'trail': []},
   {'lead': [], 'match': ['electrolytes'], 'trail': []},
   {'lead': [], 'match': ['calories'], 'trail': []},
   {'lead': [], 'match': ['agent'], 'trail': []}],
  'sent_no': 0,
  'spans': [(19, 20), (118, 124), (135, 147), (153, 161), (184, 189)],
  'token_spans': [(6, 7), (25, 26), (29, 30), (32, 33), (37, 38)]}]
```

### Entity candidates, knowledge models, and annotation/judgement

**forthcoming**

### Serialization of candidates

**forthcoming**
