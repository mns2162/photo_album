import json
import boto3
from temp.elasticsearch import Elasticsearch

def lambda_handler(event, context):
    # TODO implement
    input = event["params"]["querystring"]["query"]
     
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='KeywordExtractor',
        botAlias='QueryProcessor',
        userId='megha',
        inputText= input,
        activeContexts=[
        ]
    )
    output = []
    
    for op in response["message"].split() :
        if op not in ["keyword2","keyword3"] :
            output.append(op)
        
    res=[]
    
    #basic singular, plural handle
    for op in output :
    	if(op.endswith('ies')) :
    		res.append(op[:-3]+'y')
    	elif(op.endswith('s')) :
    		res.append(op[:-1])
    	else :
    		res.append(op)
    
    res = ''.join(res)
    print(res)
    es = Elasticsearch(
    	'https://search-photos-pp3e22wqdzgvdbjgy3dcklyjcy.us-east-1.es.amazonaws.com:443',
    	http_auth = ('ur_mns','Cloud_HW2')
    	)
    	
    query ={
        "query":{
                    "match": {
                      "labels"  :res
                      }
        }
    }
    
    result = es.search(index="photos", body=query, size=15)['hits']['hits']
    
    photos=[]
    for r in result :
        photos.append(r["_id"])        
    
    return photos