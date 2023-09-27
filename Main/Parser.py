import pandas as pd




designation_dict={'chief executive officer': 1,
"founder & managing director":1,
 'chief executive': 1,
 'ceo': 1,
 'managing partner': 1,
 'managing director': 1,
 'founder': 1,
 'owner': 1,
 'chairman': 1,
 'director': 1,
 'executive director': 1,
 'co-founder': 1,
 'cofounder': 1,
 'co founder': 1,
 'group managing director': 1,
 }



def LengthFormat2(data,ignor_list_name):
    result={}
    
    keys=[key for key in data.keys()]
    try:
        if data["name"].lower()  in ignor_list_name:
            return result
            
    except:
        return {}
    else:

        if "name" in keys and "designation" in keys:
            try:
                designation=data["designation"].lower()
                for role in designation_dict:
                    
                    if role in designation:
                        if data["designation"] in result:
                            
                            result[data["designation"].lower()].add(data["name"].lower())
                        else:
                            result[data["designation"].lower()]={data["name"].lower()}
            except:pass
        if "name" in keys and "title" in keys:
            try:
                
                designation=data["title"].lower()
                for role in designation_dict:
                    if role in designation:
                        if data["title"] in result:
                            result[data["title"].lower()].add(data["name"])
                        else:
                            result[data["title"].lower()]={data["name"]}
            except:pass
    return result



def ExactDesignationMatch(data,ignor_list_name,result):
    for designation , name in data.items():
        
        try:
            name=name.lower()
        
            designation=designation.lower()
            designation_dict[designation]
            if name  in ignor_list_name:
                pass
            else:
                
                if designation in result:
                    result[designation].add(name)
                else:
                    result[designation]={name}
                
        except:
            pass
    for name,designation in data.items():
        
        try:
            name=name.lower()
        
            designation=designation.lower()
            designation_dict[designation]
            if name  in ignor_list_name:
                pass
            else:
                
                if designation in result:
                    result[designation].add(name)
                else:
                    result[designation]={name}
        except:
            pass
    return result

def PartialCheckDesignation(data,ignor_list_name,result):
    ## IN checking
    for name , designation in data.items():
        try:
            name=name.lower()
            designation=designation.lower()
            for role in designation_dict:
                if role in designation:
                    if name  in ignor_list_name:
                        pass
                    else:

                        if designation in result:
                            
                            result[designation].add(name)
                        else:
                            result[designation]={name}
        except:
            pass
                    
    for designation , name in data.items():
        try:
            name=name.lower()
            designation=designation.lower()
            for role in designation_dict:
                if role in designation:
                    if name  in ignor_list_name:
                        pass
                    else:
                        if designation in result:
                            result[designation].add(name)
                        else:
                            result[designation]={name}
        except:
            pass
    return result
    
    
def Extract(data):
    ignor_list_name=["name","title","example","unknown","not specified","n/a","ceo","founder","owner","president","partner","director","managing"," director","cheif","officer","unspecified","not mentioned","md/ceo","designation","chairman","not provided","value","mission","vision","executive","m.d"]
    
    result={}
    if len(data)==2:
        
        keys=[key.lower() for key in data.keys() if key!=None]
 
        if "name" in keys and ("designation" in keys or "title" in keys) :
            result=LengthFormat2(data,ignor_list_name)
      
    
    
    result=ExactDesignationMatch(data,ignor_list_name,result)
    result=PartialCheckDesignation(data,ignor_list_name,result)
    
    for people_designation,names_list in result.items():
        key1=people_designation.lower()
        pople_name_update=[]
        for role in designation_dict:
            if role in key1:
                for ele in names_list:
                    if ele in ignor_list_name or role in ele:
                        pass
                    else:
                        flag=True
                        for item in ignor_list_name:
                            if item in ele:
                                flag=False
                                break
                        if flag:
                            if ele not in pople_name_update and (ele!="in" or ele!="the" or ele!="not" or ele!="of"):
                                pople_name_update.append(ele)
            result[people_designation]=pople_name_update
    return result



def ComputeNameDesignationMap(nameDesignationmap,temp_parse,link)->dict:
    for designation,list_name in temp_parse.items():
        for people in list_name:
            if people in nameDesignationmap:
                nameDesignationmap[people]["designation"].add(designation)
                nameDesignationmap[people]["childlink"].add(link)
            else:
                nameDesignationmap[people]={"designation":{designation},"childlink":{link}}
    return nameDesignationmap
















def combineEachlinkWithbatchesresult(childMap):
    websiteChildlinkCeoName={}
    for link ,value in childMap.items():     
        nameDesignationmap={}       
        if type(value)==dict:
            temp_parse=Extract(value)
            
            temp=ComputeNameDesignationMap(nameDesignationmap,temp_parse,link)
            nameDesignationmap={**nameDesignationmap,**temp}

            
        elif type(value)==list:
            for each_batch in value:
                temp_parse=Extract(each_batch)
                temp=ComputeNameDesignationMap(nameDesignationmap,temp_parse,link)
                nameDesignationmap={**nameDesignationmap,**temp}


        websiteChildlinkCeoName[link]=nameDesignationmap
        
    return websiteChildlinkCeoName


def ParsedResult(websiteChildlinkCeoName):
    update_websiteChildlinkCeoName={
        "links":[],
        "people_name":[],
        "designation":[]
    }


    for parent,ceo_data in websiteChildlinkCeoName.items():                    
        for name ,ceo_data in ceo_data.items():
            if name:
                update_websiteChildlinkCeoName["designation"].append(",".join(ceo_data["designation"]))
                update_websiteChildlinkCeoName["people_name"].append(name)
                update_websiteChildlinkCeoName["links"].append(parent)


    return update_websiteChildlinkCeoName


def parsechildMap(childMap):
    websiteChildlinkCeoName=combineEachlinkWithbatchesresult(childMap) #Input {link:chatgpt_result,}

    return ParsedResult(websiteChildlinkCeoName)