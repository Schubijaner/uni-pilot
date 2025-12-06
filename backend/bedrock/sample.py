import boto3
import json


client = boto3.client('bedrock-runtime', region_name='us-east-1')


body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello from AWS Bedrock!'"
        }
    ]
})

try:
    response = client.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=body
    )

    response_body = json.loads(response['body'].read())
    print("✅ SUCCESS!")
    print(f"Claude says: {response_body['content'][0]['text']}")

except Exception as e:
    print(f"❌ ERROR: {e}") 