import boto3
client = boto3.client(
    'textract',
    region_name = 'us-east-1',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
)

def extract(image: str):

    with open(image, 'rb') as f:
        response = client.analyze_document(
            Document={'Bytes': f.read()},
            FeatureTypes=['FORMS', 'TABLES']
        )

    # Extract key-value pairs (e.g., "Buy": "86")
    for item in response['Blocks']:
        if item['BlockType'] == 'KEY_VALUE_SET':
            key = next(v['Text'] for v in item['EntityTypes'] if v['Type'] == 'KEY')
            value = next(v['Text'] for v in item['EntityTypes'] if v['Type'] == 'VALUE')
            print(f"{key}: {value}")