import string
import pandas as pd
import os
import json

from sqlalchemy import text, create_engine
import requests


import logging
from ChatGpt import ChatGptEngine
import argparse


    


parser = argparse.ArgumentParser(description="A simple script to greet someone.")
parser.add_argument("--name", type=int,required=True, help="The name of the person to greet.")

args = parser.parse_args()
filename=args.name
print(filename)







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

##Log

logging.basicConfig(filemode="w",filename=f"logs/{filename}.log",level=logging.INFO)
logging.info(f"PID:={os.getpid()}")
# Set up the connection parameters
db_username = 'postgres'
db_password = 'postgres321123'
db_host = 'scrape.cpf8ws5bn2fs.ap-south-1.rds.amazonaws.com'
db_port = '5432'
db_name = 'tempuse'
schema_name = 'new_ceo'

# Create the database engine with the specified schema
engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}?options=-csearch_path%3D{schema_name}')

def DirectInsert(website:string,childLink:string ,raw_data:string,total_chatgpt_hit:int):
    
    pd.DataFrame({"parent":website,"childlink":childLink,"raw_chatgpt_result":raw_data,"total_hit_chatgpt":total_chatgpt_hit},index=[0]).to_sql("raw_ceo_data",con=engine,if_exists='append',index=True)
    


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
            # batch.append([index[0]-75,index[0]+75])
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
                    # batch.append([start,index[i]+75])
                    end=index[i]+75
                    buffer=0
                    
        
    return batch

        
        
        
        
result_j={}
with engine.connect() as conn:
    result=conn.execute(text("select parent from raw_ceo_data"))
    for website in result:
        result_j[website[0]]=1
        
    result=conn.execute(text("select parent from priority_website"))
    for website in result:
        result_j[website[0]]=1

        

        
logging.info(f"total website NER/Parse already {len(result_j)}")

data=json.load(open(f"Batches/{filename}.json","r"))

logging.info(f"loaded..{len(data)}")
i=0
prompt='\n\n\n\nfrom above text Give me the name and designation in json format {"name":"designation"}' 
OPENAI_API_KEY = "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"



possible_links='\n\n\n\n i will provide you list of links using them select top  possible links  having ceo,founder,managing director or any board member information contain in that link'

requests.post("http://35.154.0.179/Alert-system", 
    data=f" pid {os.getpid()} ,start screen/filename {filename} 😀".encode(encoding='utf-8'))

for website,text1 in data.items():
    try:
        result_j[website]
        logging.info(f"old {i}.{website}")
    except :
        
        try:
            total_chatgpt_hit=0
            if len(text1)>10:
                temp_result=ChatGptEngine(OPENAI_API_KEY,str(text1.keys()),possible_links)
                total_chatgpt_hit+=1
                possible_link_parent={}
                limit_on_link=8
                for childLink,childText in text1.items():
                    if limit_on_link<1:
                        break
                    if childLink in temp_result:
                        possible_link_parent[childLink]=childText+" ."+childLink
                        limit_on_link-=1
                    
                count_link_return=len(possible_link_parent)
                logging.warning(f"website having more than 10 child ,{website},{count_link_return}")
                
                if count_link_return!=0:
                    text1=possible_link_parent
                
            
           
            batches={}
            limit_on_link=10
            for childLink,childText in text1.items():
                if limit_on_link<1:
                    break
                limit_on_link-=1
                batch=IdealBatch(childText)
                if batch:
                    batches[childLink]=batch
            
            FinalResult={}
            for childLink,batch in batches.items():
                
                tempResult=""
                limit=3
                for each_batch in batch:
                    if limit<1:
                        break
                    batchResult=ChatGptEngine(OPENAI_API_KEY,each_batch,prompt)
                    total_chatgpt_hit+=1
                    tempResult+=batchResult
                    limit-=1
                
                childbatchResult=ChatGptEngine(OPENAI_API_KEY,tempResult,prompt)
                # FinalResult[childLink]=childbatchResult
                total_chatgpt_hit+=1
                
                result_upload={"childlink":childLink,"raw-result":childbatchResult,"parent":website}
                result_upload=json.dumps(result_upload) 
                DirectInsert(website,childLink,result_upload,total_chatgpt_hit)
                logging.info(f"child {i}.{childLink}-->hit {total_chatgpt_hit}")
                
            
            
        except Exception as e:
            logging.critical(f"{website}\n--:={e}")
    i+=1
    # if i==10:
    #     exit()
    if i!=0 and i%100==0:
        requests.post("http://35.154.0.179/Alert-system", 
                data=f"file/screen {filename} compleated {i} 😀".encode(encoding='utf-8'))
            
requests.post("http://35.154.0.179/Alert-system", 
    data=f" compleated screen {filename} 😀".encode(encoding='utf-8'))