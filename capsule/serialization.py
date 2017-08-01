from itertools import product

def textSerializeModel(usableTextList,predicate,descendantGenerations=1,onlySharedAncestors=True,ignore_case=True):
    '''
    for each usableText, adds features in the following format:

    [{'predicate':'name',
     'sent':sentIndex,
     'subjectCandidate':candIndex,
     'objectCandidate':candIndex,
     'subjectTokenSpan':[start,end],
     'objectTokenSpan':[start,end],
     'subjectText':text,
     'objectText':text,
     'features':['featureA',...,'featureB']},...]
    '''
    predicate=predicate.upper()

    for ti in usableTextList:
        featureList=[]
        if predicate.upper() in [ki['predicate'] for ki in ti.knowModel]:
            subList=[]
            objList=[]
            kmIdx=[ki['predicate'] for ki in ti.knowModel].index(predicate)
            subjectName=ti.knowModel[kmIdx]['subject']
            objectName=ti.knowModel[kmIdx]['object']
            for snti in ti.entCandidates:
                for i,ci in enumerate(snti[3]):
                    if ci[2]==ti.knowModel[kmIdx]['subject']:
                        # (sentIdx,candIdx,tokenStart,tokenEnd)
                        subList.append((snti[0],i,ci[0],ci[1]))
                    elif ci[2]==ti.knowModel[kmIdx]['object']:
                        objList.append((snti[0],i,ci[0],ci[1]))
                for obji,subi in product(objList,subList):
                    features=[]
                    sent=ti.document['sents'][subi[0]]
                    # token features
                    for toki in ti.availSearchToken:
                        n=0
                        subAncestSet=set()
                        subChildSet=set()
                        objAncestSet=set()
                        objChildset=set()
                        for si in range(subi[2],subi[3]):
                            if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                feat=subjectName+'_'+str(n)+'_'+str(toki)
                                features.append(feat)
                                feat=subjectName+'_has_'+str(toki)
                                features.append(feat)
                            elif not toki[:3] in ['is_','lik']:
                                feat=subjectName+'_'+str(n)+'_'+str(toki)+'='+str(sent[toki][si])
                                features.append(feat)
                                feat=subjectName+'_has_'+str(toki)+'='+str(sent[toki][si])
                                features.append(feat)
                            n+=1
                        n=0
                        for oi in range(obji[2],obji[3]):
                            if toki[:3] in ['is_','lik'] and sent[toki][oi]==True:
                                feat=objectName+'_'+str(n)+'_'+str(toki)
                                features.append(feat)
                                feat=objectName+'_has_'+str(toki)
                                features.append(feat)
                            elif not toki[:3] in ['is_','lik']:
                                feat=objectName+'_'+str(n)+'_'+str(toki)+'='+str(sent[toki][oi])
                                features.append(feat)
                                feat=objectName+'_has_'+str(toki)+'='+str(sent[toki][oi])
                                features.append(feat)
                            n+=1

                        #Ancestors
                        subAncList=[set(sent['ancestors'][si]) for si in range(subi[2],subi[3])]
                        subAncSet=set.intersection(*subAncList)
                        objAncList=[set(sent['ancestors'][oi]) for oi in range(obji[2],obji[3])]
                        objAncSet=set.intersection(*objAncList)
                        if onlySharedAncestors:
                            sharedAncSet=set.intersection(subAncSet,objAncSet)
                            for si in sharedAncSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                    feat='shared_ancestor_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=subjectName+'shared_ancesor_'+str(toki)+'='+str(sent[toki][si])
                                    features.append(feat)
                        else:
                            for si in subAncSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                    feat=subjectName+'_ancestor_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=subjectName+'_ancesor_'+str(toki)+'='+str(sent[toki][si])
                                    features.append(feat)

                            for oi in objAncSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][oi]==True:
                                    feat=objectName+'_ancestor_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=objectName+'_ancestor_'+str(toki)+'='+str(sent[toki][oi])
                                    features.append(feat)
                        #Children
                        gn=1
                        subChildDict={gn:[set(sent['children'][si]) for si in range(subi[2],subi[3])]}
                        objChildDict={gn:[set(sent['children'][oi]) for oi in range(obji[2],obji[3])]}
                        while gn<=descendantGenerations:
                            subChildSet=set.intersection(*subChildDict[gn])
                            objChildSet=set.intersection(*objChildDict[gn])
                            for si in subChildSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                    feat=subjectName+'_child_g_'+str(gn)+'_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=subjectName+'_child_g_'+str(gn)+'_'+str(toki)+'='+str(sent[toki][si])
                                    features.append(feat)
                            for oi in objChildSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][oi]==True:
                                    feat=objectName+'_child_g_'+str(gn)+'_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=objectName+'_child_g_'+str(gn)+'_'+str(toki)+'='+str(sent[toki][oi])
                                    features.append(feat)
                            gn+=1
                            subChildDict[gn]=[set(sent['children'][si]) for si in subChildDict[gn-1]]
                            objChildDict[gn]=[set(sent['children'][oi]) for oi in objChildDict[gn-1]]
                featureList.append({'predicate':predicate,
                                    'sent':subi[0],
                                    'subjectCandidate':subi[1],
                                    'objectCandidate':obji[1],
                                    'subjectTokenSpan':[subi[2],subi[3]],
                                    'objectTokenSpan':[obji[2],obji[3]],
                                    'subjectText':' '.join([sent['word'][wi] for wi in range([subi[2],subi[3]])]),
                                    'objectText':' '.join([sent['word'][wi] for wi in range([obji[2],obji[3]])]),
                                    'features':list(set(features))})
            ti.addfeatures(featureList)
