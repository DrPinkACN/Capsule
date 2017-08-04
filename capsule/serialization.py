from itertools import product

def textSerializeModel(usableTextDoc,predicate,descendantGenerations=1,onlySharedAncestors=True,ignore_case=True):
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

    searchTokens=[sti for sti in usableTextDoc.availSearchToken if sti!='raw_text']
    featureList=[]
    if predicate.upper() in [ki['predicate'] for ki in usableTextDoc.knowModel]:
        subList=[]
        objList=[]
        kmIdx=[ki['predicate'] for ki in usableTextDoc.knowModel].index(predicate)
        subjectName=usableTextDoc.knowModel[kmIdx]['subject']
        objectName=usableTextDoc.knowModel[kmIdx]['object']
        for snti in usableTextDoc.entCandidates:
            for i,ci in enumerate(snti[3]):
                if ci[2]==usableTextDoc.knowModel[kmIdx]['subject']:
                    # (sentIdx,candIdx,tokenStart,tokenEnd)
                    subList.append((snti[0],i,ci[0],ci[1]))
                elif ci[2]==usableTextDoc.knowModel[kmIdx]['object']:
                    objList.append((snti[0],i,ci[0],ci[1]))
            for obji,subi in product(objList,subList):
                features=[]
                sent=usableTextDoc.document['sents'][subi[0]]
                # token features
                for toki in searchTokens:
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
                        elif si<len(sent[toki]) and not toki[:3] in ['is_','lik']:
                            if sent[toki][si]:
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
                        elif oi<len(sent[toki]) and not toki[:3] in ['is_','lik']:
                            if sent[toki][oi]:
                                feat=objectName+'_'+str(n)+'_'+str(toki)+'='+str(sent[toki][oi])
                                features.append(feat)
                                feat=objectName+'_has_'+str(toki)+'='+str(sent[toki][oi])
                                features.append(feat)
                        n+=1

                    #Ancestors
                    subAncList=[set(sent['ancestors'][si]) for si in range(subi[2],subi[3]) if si<len(sent['ancestors'])]
                    if subAncList: subAncSet=set.union(*subAncList)
                    objAncList=[set(sent['ancestors'][oi]) for oi in range(obji[2],obji[3]) if oi<len(sent['ancestors'])]
                    if objAncList: objAncSet=set.union(*objAncList)
                    if onlySharedAncestors and (subAncList and objAncList):
                        sharedAncSet=set.intersection(subAncSet,objAncSet)
                        for si in sharedAncSet:
                            if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                feat='shared_ancestor_'+str(toki)
                                features.append(feat)
                            elif not toki[:3] in ['is_','lik']:
                                feat=subjectName+'shared_ancestor_'+str(toki)+'='+str(sent[toki][si])
                                features.append(feat)
                    else:
                        if subAncList:
                            for si in subAncSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][si]==True:
                                    feat=subjectName+'_ancestor_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=subjectName+'_ancestor_'+str(toki)+'='+str(sent[toki][si])
                                    features.append(feat)
                        if objAncList:
                            for oi in objAncSet:
                                if toki[:3] in ['is_','lik'] and sent[toki][oi]==True:
                                    feat=objectName+'_ancestor_'+str(toki)
                                    features.append(feat)
                                elif not toki[:3] in ['is_','lik']:
                                    feat=objectName+'_ancestor_'+str(toki)+'='+str(sent[toki][oi])
                                    features.append(feat)
                    #Children
                    gn=1
                    subChildDict={gn:[set(sent['children'][si]) for si in range(subi[2],subi[3]) if si<len(sent['children'])]}
                    objChildDict={gn:[set(sent['children'][oi]) for oi in range(obji[2],obji[3]) if oi<len(sent['children'])]}
                    while gn<=descendantGenerations:
                        if subChildDict[gn]:
                            subChildSet=set.union(*subChildDict[gn])
                        else:
                            subChildSet=set()
                        if objChildDict[gn]:
                            objChildSet=set.union(*objChildDict[gn])
                        else:
                            objChildSet=set()
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
                        subChildDict[gn]=[set(sent['children'][si]) for si in subChildSet if si<len(sent['children'])]
                        objChildDict[gn]=[set(sent['children'][oi]) for oi in objChildSet if oi<len(sent['children'])]
            featureList.append({'predicate':predicate,
                                'sent':subi[0],
                                'subjectCandidate':subi[1],
                                'objectCandidate':obji[1],
                                'subjectTokenSpan':[subi[2],subi[3]],
                                'objectTokenSpan':[obji[2],obji[3]],
                                'subjectText':' '.join([sent['word'][wi] for wi in range(subi[2],subi[3]) if wi<len(sent['word'])]),
                                'objectText':' '.join([sent['word'][wi] for wi in range(obji[2],obji[3]) if wi<len(sent['word'])]),
                                'features':list(set(features))})

    return featureList
