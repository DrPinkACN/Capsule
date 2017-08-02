<img src="https://www.hq.nasa.gov/office/pao/History/diagrams/gemini4.gif" width="500"/>

# Capsule
Some tools for NLP, candidate extraction, annotation, and serialization built on top of spaCy

## Requirements

- Python3
- spaCy
- (optional if you want some progress bars) tqdm

## How to
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
