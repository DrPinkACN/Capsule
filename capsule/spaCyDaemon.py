import spacy
from spacy.language import EntityRecognizer
from spacy.gold import GoldParse
import pickle
import random
from configparser import ConfigParser as SafeConfigParser
import os
import time
import json
import datetime


print('initializing...')
config = SafeConfigParser()
config.read('daemonSpacy.config')
data_dir = config.get('config','data_dir')
results_file = config.get('config','results_file')
training_pkl = config.get('config','training_data')

with open(training_pkl,'rb') as fn:
    train_data=pickle.load(fn)

nlp = spacy.load('en', entity=False, parser=False)
ner = EntityRecognizer(nlp.vocab, entity_types=['DRUG', 'CONDITION'])

for itn in range(5):
    random.shuffle(train_data)
    for raw_text, entity_offsets in train_data:
        doc = nlp.make_doc(raw_text)
        gold = GoldParse(doc, entities=entity_offsets)

        ner.update(doc, gold)

ner.model.end_training()

orig_data=[i for i in os.listdir(data_dir) if i[-3:].lower()=='tsv']
print('daemon started')
while 1:
    time.sleep(0.2)
    new_data=[i for i in os.listdir(data_dir) if i[-3:].lower()=='tsv']
    if new_data!=orig_data:
        t0=time.time()
        time.sleep(0.1)
        print('parsing document')
        with open(data_dir+new_data[0],'r') as fn:
            fdoc=fn.read()
        doc=nlp(fdoc)
        ner(doc)

        ent_results=[]
        for ent in doc.ents:
            result={
            'ent_type':ent.label_,
            'ent_text':ent.text,
            'ent_start':ent.start_char,
            'ent_end':ent.end_char,
            'parent_text':ent.doc.text
            }
            ent_results.append(result)
        allResults={"done":1,"results":ent_results}
        with open(data_dir+results_file,'w') as fr:
            ftext=json.dumps(allResults,indent=4)
            fr.write(ftext)

        os.remove(data_dir+new_data[0])
        t1=time.time()
        print('time to complete:', datetime.timedelta(seconds=t1-t0))
