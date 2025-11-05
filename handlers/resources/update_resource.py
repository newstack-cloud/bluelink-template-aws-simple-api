"""
Sample handler for updating resources using AWS Lambda and DynamoDB.

This is a demonstration file showing how an AWS Lambda handler can be implemented
with boto3 for DynamoDB access. For production use, add proper error handling,
validation, and monitoring.

This example showcases AWS Lambda best practices:
- Environment variable configuration for DynamoDB table name
- boto3 for AWS service access
- Proper error handling and validation
- API Gateway compatible response format
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
# The TABLE_NAME environment variable is automatically injected by Bluelink
# based on the link to the resourceStore in the blueprint
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'resources')
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle PATCH /resources/{resourceId} requests.

    This handler demonstrates AWS Lambda with DynamoDB integration:
    - Table name injected via environment variable from Bluelink links
    - boto3 for DynamoDB operations
    - Proper error handling for missing resources
    - API Gateway compatible response format

    Args:
        event: API Gateway request event containing path parameters, body, headers, etc.
        context: Lambda execution context with runtime information

    Returns:
        API Gateway compatible response with statusCode and body
    """

    # Extract resource ID from path parameters
    resource_id = event.get("pathParameters", {}).get("resourceId")

    if not resource_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Missing resourceId in path"
            })
        }

    # Parse request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Invalid JSON in request body"
            })
        }

    # Validate that we have at least one field to update
    if not body:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Request body cannot be empty"
            })
        }

    try:
        # First, check if the resource exists
        response = table.get_item(Key={'id': resource_id})

        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Resource with id '{resource_id}' not found"
                })
            }

        # Build update expression dynamically based on provided fields
        update_expression = "SET updatedAt = :updated_at"
        expression_attribute_values = {
            ':updated_at': datetime.utcnow().isoformat() + 'Z'
        }

        # Add title if provided
        if 'title' in body:
            update_expression += ", title = :title"
            expression_attribute_values[':title'] = body['title']

        # Add description if provided
        if 'description' in body:
            update_expression += ", description = :description"
            expression_attribute_values[':description'] = body['description']

        # Update the item in DynamoDB
        update_response = table.update_item(
            Key={'id': resource_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )

        # Return the updated resource
        updated_resource = update_response['Attributes']

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(updated_resource)
        }

    except ClientError as e:
        # Handle DynamoDB errors
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']

        print(f"DynamoDB error: {error_code} - {error_message}")

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Failed to update resource",
                "details": error_message
            })
        }

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {str(e)}")

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal server error",
                "details": str(e)
            })
        }
