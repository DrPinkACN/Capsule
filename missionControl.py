import re, pickle, json
from collections import defaultdict, Counter
import spacy
from capsule.nlpDaemon import parser
from capsule import usableText
from tqdm import tqdm #progress bar

with open('data/3000DrugLabels.pkl.txt','rb') as fn:
    docs=pickle.load(fn)

utext=[]
for n,i in enumerate(docs):
    try:
        utext.append(usableText(*parser(i)))
    except:
        print('doc {} did not parse in'.format(n))
        pass

sws=[]
with open(r'stopWords.txt','r') as f:
    for i in f.readlines():
        sws.append(re.sub(r'\r?\n?','',i))

stopwordAdd={'children','adults','years','risk','part','high risk','other','use','face','scalp','grade','rats','surgery',
            'risks','women','men','method','useful','due','concentration','adult patients','patients','need','species',
            'active','oral','solution','urge','urgency','frequency','short-term','control','result','tablets','strains',
            'microorganisms','conditions','adolescents','children 4 years','age','4 years','2 years','children 2 years',
            'manifestations','physician','judgment','children 5 years','children 12 years'}

relationshipWords={'treatment','treats','therapy','adjunctive','monotherapy','indicated','relief','eradication','introduction',
                  'local','topical','management','patients','improve','prevention','adjunctive therapy','topical treatment',
                  'regimen','attacks','reversal','production','symptoms','temporary relief','adjunct','inhibition',
                  'correction','recommended','source of','maintain'}

sws+=list(stopwordAdd)+list(relationshipWords)
sws=list(set(sws))

## using the lemma for the stop words:
import spacy
nlp=spacy.load('en')
swslemma=set()
for i in nlp(' '.join(sws)):
    swslemma.add(i.lemma_)
swslemma=list(swslemma)

####Condition Candidate Extractor (CE)########
cond_pos_regx=r'\b((ADJ\s(PART|CONJ)?\s?)?(ADJ)\s)?(NOUN|PROPN)((\s(NUM))?\s(NOUN|PROPN))*\b'
sws_regx=r'\b('+r'|'.join(swslemma)+r')\b'

CEcondition=('z',(cond_pos_regx,'pos'),(sws_regx,'lemma'))

####Drug CE##########
drug_pos_regx=r'\b((NOUN|PROPN|NUM|ADJ)\s?)*(CONJ\s)?((NOUN|PROPN|NUM)\s?)+((PUNCT)(\s(NOUN|PROPN|NUM))+)?\b'
CEdrug=('z',(drug_pos_regx,'pos'),(sws_regx,'lemma'))

##extraction and adding to usabletext##
for i,u in enumerate(tqdm(utext)):
    utext[i].entCandidateClear()
    utext[i].entCandidateAdd(u.compose(CEcondition),'CONDITION')
    utext[i].entCandidateAdd(u.compose(CEdrug),'DRUG')

##add a knowledge model##
for i,u in enumerate(tqdm(utext)):
    utext[i].knowModelAdd('treatment', 'drug', 'condition')

## do some annotation
from capsule.annotation import singleEntity, tripleKM

## loads annotation CLI tool I designed around a dark terminal, but might work just as well on light backgrounds
autext=singleEntity(utext, 'phil',entities=['DRUG','CONDITION'],randomize=True)

akmutext=tripleKM(utext, 'phil','treatment',randomize=True)

#serialize data
from capsule.serialization import textSerializeModel as tsm
tsm(utext,'treatment')

## grab annotations for training spacy ner
aCands=[]
for ai in autext:
    try:
        for bi in ai.annotation['annotation']:
            aCands.append((bi[1],[x for x,y in zip(bi[2],bi[4]) if y==1]))
    except:
        pass
