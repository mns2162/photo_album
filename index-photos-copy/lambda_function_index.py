import json
import boto3
from datetime import datetime
from temp.elasticsearch import Elasticsearch

def lambda_handler(event, context):

    bucket=event['Records'][0]['s3']['bucket']['name']
    file=event['Records'][0]['s3']['object']['key']
    
    client=boto3.client('rekognition')
    
    response = client.detect_labels(
             Image={'S3Object': {
                 'Bucket': bucket,
                 'Name': file
         }}, MaxLabels=10)
    
    labels = [label['Name'] for label in response['Labels']]
    
    temp=[]
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, file)
    print(obj.get()['ResponseMetadata']['HTTPHeaders'])
    if 'x-amz-meta-customlabels' in obj.get()['ResponseMetadata']['HTTPHeaders'] :
        temp=obj.get()['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(",")
    
    labels+=temp
    
    res=[]
    
    #basic singular, plural handle
    for l in labels :
    	if(l.endswith('ies')) :
    	    result = l[:-3]+'y'
    	elif(l.endswith('s')) :
    		result = l[:-1]
    	else :
    		result = l
    	if result not in res :
    	    res.append(result)
    	    
    print(res)		
    now=datetime.now()
    
    es = Elasticsearch(
			'https://search-photos-pp3e22wqdzgvdbjgy3dcklyjcy.us-east-1.es.amazonaws.com:443',
			http_auth = ('ur_mns','Cloud_HW2')
	    )
    
    element = {
        "objectKey": file,
        "bucket": bucket,
        "createdTimestamp": now.strftime("%d/%m/%Y, %H:%M:%S"),
        "labels": res
        }
    
    response = es.index(index="photos", id=file, body=element)
    
    return {
        'statusCode': 200,
        'body': response
    }  