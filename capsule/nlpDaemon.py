from spacy.en import English
import os
from uuid import uuid4
import re
#from utils import usableText


nlp = English()
print('English parser loaded')

def parser(someDocument):
    doc = nlp(someDocument)
    doc_id = uuid4().hex
    n=0
    availSearchToken = ['word','lemma','pos','tag','dep_label','ent_type']
    availReturnToken = ['word','lemma','pos','tag','dep_label','prefix',
                        'suffix','is_oov','like_url','like_num','like_email',
                        'is_stop','ent_type']
    parsedDocument={'doc_id':doc_id,'doc_text':doc.text,'sents':[]}
    for si in doc.sents:
        sent={'sent_no':n,
               'raw_text':si.text, #needed
               'idx':[ii.idx-si[0].idx for ii in si], #needed
               'idx_doc':[ii.idx for ii in si],
               'word':[ii.text for ii in si], #needed
               'lemma':[ii.lemma_ for ii in si],
               'pos':[ii.pos_ for ii in si],
               'tag':[ii.tag_ for ii in si],
               'dep_label':[ii.dep_ for ii in si],
               'prefix':[ii.prefix_ for ii in si],
               'suffix':[ii.suffix_ for ii in si],
               'prob':[ii.prob for ii in si],
               'is_oov':[ii.is_oov for ii in si],
               'like_url':[ii.like_url for ii in si],
               'like_num':[ii.like_num for ii in si],
               'like_email':[ii.like_email for ii in si],
               'is_stop':[ii.is_stop for ii in si],
               'ent_type':[ii.ent_type_ for ii in si]}
        chdrn=[]
        ancst=[]
        for ii in si:
            chdrn.append([chi.i-si[0].i for chi in ii.children])
            ancst.append([anc.i-si[0].i for anc in ii.ancestors])
        sent['children']=chdrn
        sent['ancestors']=ancst
        parsedDocument['sents'].append(sent)
        n+=1
    return (parsedDocument,availSearchToken,availReturnToken)

def vector(someText):
    return nlp(someText).vector
