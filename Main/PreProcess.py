import string
import pandas as pd

import json

from sqlalchemy import text, create_engine
from ChatGpt import ChatGptEngine
from Parser import parsechildMap
OPENAI_API_KEY = "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"

designation={'chief executive officer': 1,
 'chief executive': 1,
 'ceo': 1,
 'md/ceo': 1,
 'managing partner': 1,
 'managing director': 1,
 'founder': 1,
 'director': 1,
 'owner': 1,
 'chairman': 1,
 'president': 1,
 'executive director': 1,
 'co-founder': 1,
 'co founder': 1,
 'group managing director': 1,
 'group ceo': 1}



prompt='\n\n\n\nfrom above text Give me the name and designation in json format {"name":"designation"}' 

possible_links='\n\n\n\n i will provide you list of links using them select top  possible links  having ceo,founder,managing director or any board member information contain in that link'



def IdealBatch(text1):
    batch=[]
    text1=text1.lower()
    roleMapIndex={}
    splitTextDot=text1.split(".")
   
    for i,check_sentence in enumerate(splitTextDot):
        for role in designation:
            if role in check_sentence:
                if role in roleMapIndex:
                    roleMapIndex[role].append(i)
                    
                else:
                    roleMapIndex[role]=[i]
    index={}
    for key,value in roleMapIndex.items():
        for el in value:
            index[el]=1
    index=sorted(index.keys(),reverse=False)
    
    
    
    if index:
        if len(index)==1:
            batch.extend([".".join(splitTextDot[index[0]-75:index[0]+75])])
        else:
            
            buffer=0
            end=0
            
            for i in range(len(index)):
                if i==len(index)-1:
                    buffer=75
                else:
                    
                    buffer+=abs(index[i]-index[i+1])
                if buffer<75:
                    
                    pass
                else:
                    
                    start = index[i] - 75
                    if start <= end:
                        start = end +1
                    batch.extend([".".join(splitTextDot[start:index[i]+75])])
                    end=index[i]+75
                    buffer=0
                    
        
    return batch        




def reduceChildLinkContent(data):
    
    if len(data)>10:
        temp_result=ChatGptEngine(OPENAI_API_KEY,str(data.keys()),possible_links)
        possible_link_parent={}
        limit_on_link=8
        for childLink,childText in data.items():
            if limit_on_link<1:
                break
            if childLink in temp_result:
                possible_link_parent[childLink]=childText+" ."
                limit_on_link-=1
            
        count_link_return=len(possible_link_parent)
        
        if count_link_return!=0:
            data=possible_link_parent
        
    return data



def nameDesignationInfo(data):
    
    result={}
    for childLink,childText in data.items():
        
        total_chatgpt_hit=0
        
        batches={}
        limit_on_link=10
        
        if limit_on_link<1:
            break
        limit_on_link-=1
        batch=IdealBatch(childText)
        if batch:
            batches[childLink]=batch
        for childLink,batch in batches.items():
            
            tempResult=""
            limit=3
            for each_batch in batch:
                if limit<1:
                    break
                batchResult=ChatGptEngine(OPENAI_API_KEY,each_batch,prompt)
                total_chatgpt_hit+=1
                if batchResult:
                    tempResult+=batchResult
                limit-=1
            childbatchResult=ChatGptEngine(OPENAI_API_KEY,tempResult,prompt)
            total_chatgpt_hit+=1
            try:
                childbatchResult=json.loads(childbatchResult)
                result[childLink]=childbatchResult
            except:
                pass
    return result





def ceo_data(data):   
    data=reduceChildLinkContent(data)
    Result=nameDesignationInfo(data)

    Result=parsechildMap(Result)

    return Result
