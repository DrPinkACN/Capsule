import random
import os
from itertools import cycle, product
import time
import re

####INIT########################################################################
# some color pre-sets for shading candidates differently:
ascii_colors_for_candidates=['38;5;220','38;5;202','38;5;200','38;5;87','38;5;189']
ascii_color_for_sentense='38;5;15'
# https://en.wikipedia.org/wiki/ANSI_escape_code
# only escape characters up to #49 allowed
################################################################################

####HELPER FUNCTIONS############################################################
# Screen Clearing between candidates/sentences
def clearscreen():
    os.system('clear')
    #time.sleep(0.05)
# Function to stylize printed text with ascii escape chars:
def style(strng, color='38;5;15', stype='c'):
    '''
    for stypes:
        c = color
        b = bold
        f = faint
        i = invert/negative
        u = underline
        r = conceal
    color selected as default
    '''
    efDict={'b':'\x1b[1m','i':'\x1b[7m','u':'\x1b[4m','r':'\x1b[8m','f':'\x1b[2m'}
    clDict={'c':'\x1b[39m','b':'\x1b[22m','i':'\x1b[27m','u':'\x1b[24m','r':'\x1b[28m','f':'\x1b[22m'}
    if stype=='c':
        effct='\x1b[{0}m'.format(str(color))
        clral=clDict[stype]
    elif stype in efDict:
        effct=efDict[stype]
        clral=clDict[stype]
    else:
        raise ValueError('invalid stype (style-type) selected, options are: '+' ,'.join(["'{0}'".format(i) for i in clDict]))
    return ''.join([effct,strng,clral])
################################################################################

####LOAD DATA###################################################################
def singleEntity(usableTextList,annotatorName,entities=None,randomize=False):
    candidates=usableTextList
    # randomize the candidate list
    if randomize:
        random.shuffle(candidates)
################################################################################

####IDENTIFY UNIQUE ENTITIES####################################################
    if entities:
        entities=[i.upper() for i in entities]
    else:
        entities=[]
        for cand in candidates:
            for i in cand.getEntCandidates():
                for ii in i[1]:
                    entities.append(ii[2])
        entities=list(set(entities))
        # also assign ascii color to each entity
    colors=cycle(ascii_colors_for_candidates)
    entDic={}
    for ent in entities: entDic[ent]=str(next(colors))
################################################################################

#####ANNOTATION INSTRUCTIONS####################################################
    instructions='''Enter the following text comands as your inputs:
 - {0} if the candidate is CORRECT
 - {1} if the candidate is INCORRECT
 - {2} if you choose to ABSTAIN from annotating, or enter through
 - {5} if you wish to SKIP the current document
 - {6} if you need to start over on the current document

 * {3} will hault the annotation process and return your annotated list
 * {4} will clear and refresh the screen.'''.format(style(' y ',stype='i'),style(' n ',stype='i'),style(' a ',stype='i'),style(' stop ',stype='i'),style(' cc ',stype='i'),style(' skip ',stype='i'),style(' back ',stype='i'))
    clearscreen()
    ################################################################################

    ####THE MAIN WORK LOOP##########################################################
    n=0
    nAnnon=0
    answer='None'
    while answer.lower()!='stop' and n<=len(candidates):
        answer='None'
        annons={'annotatorName':annotatorName,
                'annotation':[(candi[0],candi[1],candi[2],candi[3],[0 for cs in candi[2]]) for candi in candidates[n].entCandidates],
                'annotationType':'single',
                'entities':entities}
        sortedAnnon=[]
        ## sort annotation by candidate span start
        for ai in annons['annotation']:
            sortedAnnon.append((ai[0],
                                ai[1],
                                [ais for (ais,ait) in sorted(zip(ai[2],ai[3]),key=lambda x:x[0][0])],
                                [ait for (ais,ait) in sorted(zip(ai[2],ai[3]),key=lambda x:x[0][0])],
                                ai[4]))
        annons['annotation']=sortedAnnon
        for an,ai in enumerate(annons['annotation']):
            candi=(ai[1],ai[2])
            stext=candi[0].split('\n')[0]
            cands=candi[1]
            matches=[str(stext[j[0]:j[1]]) for j in cands]
            cnames=[j[2] for j in cands]
            allp=[]
            alln=[]
            for m,span in enumerate(cands):
                print(instructions)
                print('\n')
                print(style('Sentences Complete (Approx): {0} ({1}%)\nCandidates Annotated: {2}'.format(str(n),str(round(100*(n)/len(candidates),2)),str(nAnnon)),'38;5;88'))
                j,k,cname=span
                successful = False
                failed = False
                while not successful:
                    if answer.lower()=='stop' or (answer.lower()=='skip' or answer.lower()=='back'):
                        pass
                        successful=True
                        clearscreen()
                    else:
                        if not failed:
                            print('\n')
                            print(style('Sentence Candidates:',stype='b'))
                            for ent in entDic:
                                print(style(style(ent+':',entDic[ent]),stype='u'),style(' | ',entDic[ent]).join([i for i in [style(style(match,stype='i'),entDic[ent]) if (ii==m and cnames[ii]==ent) else style(match,entDic[ent]) if cnames[ii]==ent else None for ii,match in enumerate(matches)] if i]))
                            fmtsent='\n{0}{1}{2}'.format(style(stext[:j],color=ascii_color_for_sentense),style(style(stext[j:k],stype='i'),entDic[cname]),style(stext[k:],ascii_color_for_sentense))
                            fmtsent=re.sub(r'[^\x00-\x7f]|\x1b[[^0-4]?[^0-9](;\d)*m', '', fmtsent)
                            print(fmtsent)
                        answer=input(style('\n{0}?: '.format(cname),entDic[cname]))
                        if answer.lower()=='y':
                            annons['annotation'][an][4][m]=1
                            nAnnon+=1
                            successful=True
                            clearscreen()
                        elif answer.lower()=='a' or answer=='':
                            annons['annotation'][an][4][m]=0
                            successful=True
                            clearscreen()
                        elif answer.lower()=='n':
                            annons['annotation'][an][4][m]=-1
                            nAnnon+=1
                            successful=True
                            clearscreen()
                        elif answer.lower()=='cc':
                            successful=False
                            clearscreen()
                            print(instructions)
                            print('\n')
                            print(style('Sentences Complete (Approx): {0} ({1}%)\nCandidates Annotated: {2}'.format(str(n),str(round(100*(n)/len(candidates),2)),str(nAnnon)),'38;5;88'))
                        elif answer.lower()!='stop':
                            print('\nvalid options are: \x1b[4my/a/n/skip/stop\x1b[24m')
                            successful=False
                            failed = True
        candidates[n].annotateCandidates(annons)
        if not answer.lower()=='back': n+=1
    return candidates

####LOAD DATA###################################################################
def tripleKM(usableTextList,annotatorName,predicate,randomize=False):
    candidates=usableTextList
    # randomize the candidate list
    if randomize:
        random.shuffle(candidates)
################################################################################

####IDENTIFY THE MODEL##########################################################
    found=False
    n=0
    while not found:
        for kmi in candidates[0].knowModel:
            if kmi['predicate']==predicate.upper():
                model=kmi
                found=True
    entDic={}
    colors=cycle(ascii_colors_for_candidates)
    entDic[model['subject']]=str(next(colors))
    entDic[model['object']]=str(next(colors))
    entDic[model['predicate']]=str(next(colors))
################################################################################

#####ANNOTATION INSTRUCTIONS####################################################
    instructions='''Enter the following text comands as your inputs:
 - {0} if the candidate is CORRECT
 - {1} if the candidate is INCORRECT
 - {2} if you choose to ABSTAIN from annotating, or enter through
 - {5} if you wish to SKIP the current document
 - {6} if you need to start over on the current document

 * {3} will hault the annotation process and return your annotated list
 * {4} will clear and refresh the screen.'''.format(style(' y ',stype='i'),style(' n ',stype='i'),style(' a ',stype='i'),style(' stop ',stype='i'),style(' cc ',stype='i'),style(' skip ',stype='i'),style(' back ',stype='i'))
    clearscreen()
################################################################################

####THE MAIN WORK LOOP##########################################################
    n=0
    nAnnon=0
    answer='None'
    while answer.lower()!='stop' and n<=len(candidates):
        answer='None'

        annons={'annotatorName':annotatorName,
                'annotation':[
                (
                candi[0],
                candi[1],
                [pso for pso in product([csi for csi in candi[2] if csi[2]==model['subject']],[coi for coi in candi[2] if coi[2]==model['object']])],
                [pso for pso in product([csi for csi in candi[3] if csi[2]==model['subject']],[coi for coi in candi[3] if coi[2]==model['object']])],
                [0 for jki in [pso for pso in product([csi for csi in candi[2] if csi[2]==model['subject']],[coi for coi in candi[2] if coi[2]==model['object']])]]) for candi in candidates[n].entCandidates],
                'annotationType':'knowModel',
                'predicate':model['predicate'],
                'subject':model['subject'],
                'object':model['object']}
        sortedAnnon=[]
        ## sort annotation by candidate span start
        for ai in annons['annotation']:
            sortedAnnon.append((ai[0],
                                ai[1],
                                [ais for (ais,ait) in sorted(zip(ai[2],ai[3]),key=lambda x:x[0][0][0])],
                                [ait for (ais,ait) in sorted(zip(ai[2],ai[3]),key=lambda x:x[0][0][0])],
                                ai[4]))
        annons['annotation']=sortedAnnon
        for an,ai in enumerate(annons['annotation']):
            candi=(ai[1],ai[2])
            stext=candi[0].split('\n')[0]
            cands=candi[1]
            sub_matches=[str(stext[j[0][0]:j[0][1]]) for j in cands]
            sub_matches_u=[]
            for k in sub_matches:
                if not k in sub_matches_u:sub_matches_u.append(k)
            #sub_matches_u=[k for j,k in enumerate(sub_matches) if (j==0 or (j>0 and k!=sub_matches[j-1]))]
            obj_matches=[str(stext[j[1][0]:j[1][1]]) for j in cands]
            obj_matches_u=[]
            #obj_matches_u=[k for j,k in enumerate(obj_matches) if (j==0 or (j>0 and k!=obj_matches[j-1]))]
            for k in obj_matches:
                if not k in obj_matches_u:obj_matches_u.append(k)
            sub_cnames=[j[0][2] for j in cands]
            sub_cnames_u=[k for j,k in enumerate(sub_cnames) if (j==0 or (j>0 and k!=sub_cnames[j-1]))]
            obj_cnames=[j[1][2] for j in cands]
            obj_cnames_u=[]
            for k in obj_cnames:
                if not k in obj_cnames_u:obj_cnames_u.append(k)
            #obj_cnames_u=[k for j,k in enumerate(obj_cnames) if (j==0 or (j>0 and k!=obj_cnames[j-1]))]
            allp=[]
            alln=[]
            for m,span_pair in enumerate(cands):
                print(instructions)
                print('\n')
                print(style('Sentences Complete (Approx): {0} ({1}%)\nCandidates Annotated: {2}'.format(str(n),str(round(100*(n)/len(candidates),2)),str(nAnnon)),'38;5;88'))
                sub_j,sub_k,sub_cname=span_pair[0]
                obj_j,obj_k,obj_cname=span_pair[1]
                successful = False
                failed = False
                while not successful:
                    if answer.lower()=='stop' or (answer.lower()=='skip' or answer.lower()=='back'):
                        pass
                        successful=True
                        clearscreen()
                    else:
                        if not failed:
                            print('\n')
                            print(style('Sentence Candidates:',stype='b'))
                            print(style(style(model['subject']+':',entDic[model['subject']]),stype='u'),
                                  style(' | ',entDic[model['subject']]).join([i for i in [style(style(match,stype='i'),entDic[model['subject']]) if (match==stext[sub_j:sub_k]) else style(match,entDic[model['subject']]) for ii,match in enumerate(sub_matches_u)] if i]))
                            print(style(style(model['object']+':',entDic[model['object']]),stype='u'),
                                  style(' | ',entDic[model['object']]).join([i for i in [style(style(match,stype='i'),entDic[model['object']]) if (match==stext[obj_j:obj_k]) else style(match,entDic[model['object']]) for ii,match in enumerate(obj_matches_u)] if i]))
                            #subject
                            fmtsent='\n{0}{1}{2}'.format(style(stext[:sub_j],color=ascii_color_for_sentense),style(style(stext[sub_j:sub_k],stype='i'),entDic[sub_cname]),style(stext[sub_k:],ascii_color_for_sentense))
                            fmtsent=re.sub(r'[^\x00-\x7f]|\x1b[[^0-4]?[^0-9](;\d)*m', '', fmtsent)
                            print(fmtsent)
                            #object
                            fmtsent='\n{0}{1}{2}'.format(style(stext[:obj_j],color=ascii_color_for_sentense),style(style(stext[obj_j:obj_k],stype='i'),entDic[obj_cname]),style(stext[obj_k:],ascii_color_for_sentense))
                            fmtsent=re.sub(r'[^\x00-\x7f]|\x1b[[^0-4]?[^0-9](;\d)*m', '', fmtsent)
                            print(fmtsent)
                        answer=input(style('\n{0}?: '.format(model['predicate']),entDic[model['predicate']]))
                        if answer.lower()=='y':
                            annons['annotation'][an][4][m]=1
                            nAnnon+=1
                            successful=True
                            clearscreen()
                        elif answer.lower()=='a' or answer=='':
                            annons['annotation'][an][4][m]=0
                            successful=True
                            clearscreen()
                        elif answer.lower()=='n':
                            annons['annotation'][an][4][m]=-1
                            nAnnon+=1
                            successful=True
                            clearscreen()
                        elif answer.lower()=='cc':
                            successful=False
                            clearscreen()
                            print(instructions)
                            print('\n')
                            print(style('Sentences Complete (Approx): {0} ({1}%)\nCandidates Annotated: {2}'.format(str(n),str(round(100*(n)/len(candidates),2)),str(nAnnon)),'38;5;88'))
                        elif answer.lower()!='stop':
                            print('\nvalid options are: \x1b[4my/a/n/skip/stop\x1b[24m')
                            successful=False
                            failed = True
        candidates[n].annotateCandidates(annons)
        if not answer.lower()=='back': n+=1
    return candidates
