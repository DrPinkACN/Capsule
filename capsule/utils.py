import re

class usableText:
    '''
    The usableText class is intended to expose parsed text tokens for regex
    searching and dictionary matching. text from a document is to be stored as
    sentences.

    Use any regular expression with knowlege that tokens will be conatinated
    into a single string, joined with spaces.

    Initial required arguments:
        - parsedDocument: accepts dictionary containing document text, doc_id,
          and a list of parsed sentences and their tokens
        - availSearchToken: a list of available search tokens
        - availReturnToken: a list of available return tokens that can be
          returned as search results

    Callable methods:
        - regexFind(pattern,search_token,return_token,leadToken,trailToken,sent_no):
            * pattern: your regular expression that you want to search. Make
              sure to input as raw text (r'your pattern') or things could get
              screwy.
            * search_token: the spanned tokens you want to search for your regex
              pattern in. If word is chosen, then the search is preformed on the
              sentence text (mainly to preserve intuative punctuation spacing).
            OPTIONAL
            * return_token: the optional token to return in addition to the word
              span that matches the search. Returned as a dict of tuples, e.g.:
              {lead:(LEADTOKEN2,LEADTOKEN1),
               match:(MATCHTOKEN1,MATCHTOKEN2,MATCHTOKEN3),
               trail:(TRAILTOKEN1,TRAILTOKEN2)}
            * leadToken: how many leading tokens to include in optional return
              of search matched tokens.
            * trailToken: how many trailing tokens to include in optional return
              of search matched tokens.
            * sent_no: optional index of sentece to be searched. Searching all
              if set to None.
            * ignore_case: self explanitory. default to True
    '''
    def __init__(self,parsedDocument,availSearchToken,availReturnToken):
        self.document=parsedDocument
        self.availSearchToken=availSearchToken
        self.availReturnToken=availReturnToken
        self.entCandidates=[]
        self.annotation=None
        self.knowModel=[]
        self.features=[]

    def __str__(self):
        return 'doc_id: {doc_id}\ndoc_text: {doc_text}'.format(**self.document)

    def __repr__(self):
        return 'doc_id: {doc_id}\ndoc_text: {doc_text}'.format(**self.document)

    def regexFind(self,pattern,search_token,return_token=None,leadToken=0,trailToken=0,sent_no=None,ignore_case=True):
        # start with some validation
        if not search_token in self.availSearchToken:
            raise Exception("search_token = \x1b[7m'{0}'\x1b[27m is not a valid token, select one of the following instead: ".format(search_token)+" ,".join(self.availSearchToken))
        try:
            if sent_no:
                sent_no=int(sent_no)
                if abs(sent_no)>=len(self.document['sents']) or sent_no<0: raise
        except:
            raise Exception("\x1b[7msent_no\x1b[27m must be an integer list index of magnetude less than the total number of sentences in the document")
        try:
            if ignore_case:
                pat=re.compile(pattern,flags=re.I)
            else:
                pat=re.compile(pattern)
        except:
            raise Exception("Better check your regex pattern and make sure it is re.compile() compatable.")
        matches=[]
        for sent in self.document['sents']:
            if sent_no==None or sent['sent_no']==sent_no:
                if search_token!='raw_text':
                    t2match=' '.join(sent[search_token])
                else:
                    t2match=sent['raw_text']
                if pat.search(t2match):
                    sent_matches = {'doc_id':self.document['doc_id'],
                                 'sent_no':sent['sent_no'],
                                 'spans':[],
                                 'token_spans':[]}
                    for fi in pat.finditer(t2match):
                        if search_token=='word':
                            tokenStart=[i for i,idx in enumerate(sent['idx']) if idx<=fi.start()][-1]
                            tokenEnd=[i for i,idx in enumerate(sent['idx']) if idx<=fi.end()][-1]
                        else:
                            tokenStart=len([i for i in t2match[:fi.start()].strip().split(' ') if i!=''])
                            tokenEnd=tokenStart+len(t2match[fi.start():fi.end()].strip().split(' '))-1
                        sent_matches['token_spans'].append((tokenStart,tokenEnd+1))
                        sent_matches['spans'].append((sent['idx'][tokenStart],sent['idx'][tokenEnd]+len(sent['word'][tokenEnd])))
                    matches.append(sent_matches)
        if return_token:
            matches=self.showTokens(matches, return_token=return_token,leadToken=leadToken,trailToken=trailToken)
        return matches

    def compose(self,opPatternTokenTuple,ignore_case=True):
        '''
        a recursive function to handle the composition

        accepts list of tuples of (pattern, token) to find the union (u), intersection (i), 'd' for difference, 's' for sub-span intersection, and 'z' for sub-span difference.".
        e.g., ('u',(r'NOUN\sNOUN','pos'),(r'\bfast\sperson\b','word'))
        '''
        op=opPatternTokenTuple[0].lower()
        if not op in ['u','i','d','s','z']:
            raise Exception("Valid set operations are 'u' for union, 'i' for intersection, 'd' for difference, 's' for sub-span intersection, and 'z' for sub-span difference.")
        try:
            pat0=opPatternTokenTuple[1][0]
            tok0=opPatternTokenTuple[1][1]
            m0=self.regexFind(pat0, tok0, ignore_case=ignore_case)
        except:
            m0=self.compose(opPatternTokenTuple[1], ignore_case=ignore_case)
        try:
            pat1=opPatternTokenTuple[2][0]
            tok1=opPatternTokenTuple[2][1]
            m1=self.regexFind(pat1, tok1, ignore_case=ignore_case)
        except:
            m1=self.compose(opPatternTokenTuple[2], ignore_case=ignore_case)
        compDocs=[]
        m0s=set()
        m1s=set()
        for m0i in m0:
            for ss,ts in zip(m0i['spans'],m0i['token_spans']):
                m0s.add((m0i['sent_no'],ss,ts))
        for m1i in m1:
            for ss,ts in zip(m1i['spans'],m1i['token_spans']):
                m1s.add((m1i['sent_no'],ss,ts))
        if op=='i':
            m3s=m0s.intersection(m1s)
        elif op=='u':
            m3s=m0s.union(m1s)
        elif op=='d':
            m3s=m0s.difference(m1s)
        elif op=='s' or op=='z':
            m3s=set()
            for m0i in m0s:
                for m1i in m1s:
                    if m0i[1][0]<=m1i[1][0] and m0i[1][1]>=m1i[1][1]:
                        m3s.add(m0i)
            if op =='z':
                m3s=m0s.difference(m3s)
        sentset=set([m3i[0] for m3i in m3s])
        for sno in sentset:
            compDocs.append({
            'doc_id':m0[0]['doc_id'],
            'sent_no':sno,
            'spans':sorted([m3i[1] for m3i in m3s if m3i[0]==sno],key=lambda x: x[0]),
            'token_spans':sorted([m3i[2] for m3i in m3s if m3i[0]==sno],key=lambda x: x[0])
            })
        return compDocs

    def showTokens(self, spanList, return_token='word',leadToken=0,trailToken=0,sent_no=None):
        '''
        provides tokens for span lists:
        * spanList: the spans you wish to return the tokens for.
        * return_token: the optional token to return in addition to the word
          span that matches the search. Returned as a dict of tuples, e.g.:
          {lead:(LEADTOKEN2,LEADTOKEN1),
           match:(MATCHTOKEN1,MATCHTOKEN2,MATCHTOKEN3),
           trail:(TRAILTOKEN1,TRAILTOKEN2)}
        * leadToken: how many leading tokens to include in optional return
          of search matched tokens.
        * trailToken: how many trailing tokens to include in optional return
          of search matched tokens.
        * sent_no: optional index of sentece to be searched. Searching all
          if set to None.
        * ignore_case: self explanitory. default to True
        '''
        if return_token and (not return_token in self.availReturnToken):
            raise Exception("return_token = \x1b[7m'{0}'\x1b[27m is not a valid token, select one of the following instead: ".format(return_token)+" ,".join(self.__availReturnToken))
        try:
            leadToken=int(leadToken)
            if leadToken<0: raise
        except:
            raise Exception("\x1b[7mleadToken\x1b[27m must be a positive integer")
        try:
            trailToken=int(trailToken)
            if trailToken<0: raise
        except:
            raise Exception("\x1b[7mtrailToken\x1b[27m must be a positive integer")
        try:
            if sent_no:
                sent_no=int(sent_no)
                if abs(sent_no)>=len(self.document['sents']) or sent_no<0: raise
        except:
            raise Exception("\x1b[7msent_no\x1b[27m must be an integer list index of magnetude less than the total number of sentences in the document")
        if spanList:
            try:
                if self.document['doc_id']!=spanList[0]['doc_id']: raise
            except:
                raise Exception("This method can only return tokens for span lists from the same document.")
        matches=[]
        for si in spanList:
            sent=self.document['sents'][si['sent_no']]
            sent_matches = si
            sent_matches['return_token']=[]
            for ti in si['token_spans']:
                tokenStart=ti[0]
                tokenEnd=ti[1]
                if leadToken>0:
                    leadTkns=sent[return_token][:tokenStart][-leadToken:]
                else:
                    leadTkns=[]
                rts={'lead':leadTkns,
                     'match':sent[return_token][tokenStart:tokenEnd],
                     'trail':sent[return_token][tokenEnd:][:trailToken]}
                sent_matches['return_token'].append(rts)
            matches.append(sent_matches)
        return matches

    def entCandidateAdd(self,spanList,entName):
        '''
        Stores entity candidate(s) in the self.entCandidate list in the following
        format:
            [
                (sent_no,'sentence text',[(span_start,span_end,'ENTITY'),...],
                   [(token_start,token_end,'ENTITY'),...]),
                (...),
                ...
            ]
        '''
        try:
            entName=str(entName).upper()
        except:
            raise Exception('Entity name (entName) must be a string.')
        if spanList:
            try:
                if self.document['doc_id']!=spanList[0]['doc_id']: raise
            except:
                raise Exception("This method can only return tokens for span lists from the same document.")
        if not self.entCandidates:
            self.entCandidates=[]
        cands=[]
        setWithCands=[eci[0] for eci in self.entCandidates]
        for si in spanList:
            cands+=[(si['sent_no'],self.document['sents'][si['sent_no']]['raw_text'],[(ss[0],ss[1],entName) for ss in si['spans']],[(ts[0],ts[1],entName) for ts in si['token_spans']])]
        for ci in cands:
            if ci[0] in setWithCands:
                swc=self.entCandidates[setWithCands.index(ci[0])]
                self.entCandidates[setWithCands.index(ci[0])]=(swc[0],swc[1],swc[2]+ci[2],swc[3]+ci[3])
            else:
                self.entCandidates.append(ci)

    def knowModelAdd(self,pred,subj,objt):#,allow_rev=False,allow_over=True,priority='object'):
        '''
        This method is used to create a knowledge model (a triple) for candidates
        one is interested in linking via a predicate ("Dog(subject) bites(predicate) man(object)").

        Args:
            pred: the predicate of the knowledge model (verb-like) | type=string
            subj: the subject of the model | type=string
            objt: the object of the model | type=string
            allow_rev: is the reverse of an annotated entity allowed | type=bool
            allow_over: allow spans for subj and objt to overlap | type=bool
            priority: accepts "subject" or "object" and determinse which to cycle through first during annotating

        Returns:
            a list of dictionaries with knowledge models to be annotated. For example:

            [
            {'predicate':'TREATMENT',
             'subject':'DRUG',
             'object':'CONDITION'},
             {...},
             ...
            ]
        '''
        #if not priority.lower() in ['subject','object']:
        #    raise Exception("The priority parameter only accepts only 'object' or 'subject.'")

        model={'predicate':pred.upper(),
               'subject':subj.upper(),
               'object':objt.upper()}

        self.knowModel.append(model)

    #def

    def entCandidateClear(self):
        '''
        clears the candidate list
        '''
        self.entCandidates=[]
        self.features=[]

    def getEntCandidates(self):
        '''
        returns part of the candidate list:
        [
            ('sentence text',[(span_start,span_end,'ENTITY'),(...)]),
            (...),
            ...
        ]
        spaCy's entity recognition training accepts this format.
        '''
        return [(ci[1],ci[2]) for ci in self.entCandidates]

    def annotateCandidates(self,annotation):
        self.annotation=annotation

    def addfeatures(self,featuresList):
        '''
        Add features as a document of keys:

        {'entity':'name',
         'sentence':index,
         'candidate':index,
         'features':['featureA',...,'featureB']}

        or

        {'predicate':'name',
         'subjectSentence':sentIndex,
         'objectSentence':sentIndex,
         'subjectCandidate':candIndex,
         'objectCandidate':candIndex,
         'features':['featureA',...,'featureB']}
        '''
        self.features+=featuresList
