import boto3
import os
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
s3 = boto3.client('s3')

TABLE_NAME = 'Officers'
BUCKET_NAME = 'officers-profile-photos'

def lambda_handler(event, context):
    try:
        table = dynamodb.Table(TABLE_NAME)

        # Check if OfficerID is provided
        if event.get('queryStringParameters') and 'OfficerID' in event['queryStringParameters']:
            officer_id = event['queryStringParameters']['OfficerID']
            response = table.get_item(Key={'OfficerID': officer_id})

            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Officer not found'})
                }

            officer = response['Item']
            photo_key = f"{officer_id}.jpg"
            photo_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{photo_key}"
            officer['PhotoS3URL'] = photo_url

            return {
                'statusCode': 200,
                'body': json.dumps(officer)
            }

        # If no OfficerID, return all officers
        response = table.scan()
        officers = response.get('Items', [])

        # Add photo URLs for each officer
        for officer in officers:
            officer_id = officer['OfficerID']
            photo_key = f"{officer_id}.jpg"
            photo_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{photo_key}"
            officer['PhotoS3URL'] = photo_url

        return {
            'statusCode': 200,
            'body': json.dumps(officers)
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'details': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'details': str(e)})
        }
