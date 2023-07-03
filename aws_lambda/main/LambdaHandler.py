import json
import urllib3
import boto3
from botocore.exceptions import ClientError

def get_secret_api_key():
    secret_name = "prod/api/key/chatgpt"
    secret_key = "api-key-chatgpt"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret_response = get_secret_value_response[ 'SecretString' ]
    secret_object = json.loads(secret_response) 
    secret_api_key = secret_object['api-key-chatgpt']
    
    # Return secret
    return secret_api_key


def lambda_handler(event, context):

    api_key = get_secret_api_key()
    URL = "https://api.openai.com/v1/chat/completions"
    HEADERS = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
                "model": "gpt-3.5-turbo",
                "temperature" : 1.0,
                "messages" : [
                    {"role": "system", "content": f"You are an assistant who answers questions about the world."},
                    {"role": "user", "content": f"When is best surfing location on the Texas coast?"}
                 ]
    }
    encodedPayload = json.dumps(payload)

    http = urllib3.PoolManager()
    r = http.request('POST', URL,
                    headers=HEADERS,
                    body=encodedPayload)
                    
    resp_body = r.data.decode('utf-8')
    resp_dict = json.loads(r.data.decode('utf-8'))
    
    print( resp_body )
    print( resp_dict )
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Successful API Call from AWS Lambda to ChatGpt!')
    }