import json
import logging
import uuid

import boto3

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localstack:4566")

table = dynamodb.Table("posts")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def create_post(body):

    post = {"id": str(uuid.uuid4()), "title": body["title"], "content": body["content"]}

    table.put_item(Item=post)

    return response(201, post)


def get_posts():

    result = table.scan()

    return response(200, result["Items"])


def get_post(post_id):

    result = table.get_item(Key={"id": post_id})

    if "Item" not in result:
        return response(404, {"message": "Post not found"})

    return response(200, result["Item"])


def update_post(post_id, body):

    table.update_item(
        Key={"id": post_id},
        UpdateExpression="SET title=:t, content=:c",
        ExpressionAttributeValues={":t": body["title"], ":c": body["content"]},
    )

    return response(200, {"message": "Post updated"})


def delete_post(post_id):

    table.delete_item(Key={"id": post_id})

    return response(200, {"message": "Post deleted"})


def lambda_handler(event, _):

    logger.debug(f"Received event:\n{json.dumps(event)}\n")

    method = event["httpMethod"]
    path = event["path"]

    try:
        logger.debug(f"Processing request: {method} {path}")
        if method == "POST" and path == "/posts":
            body = json.loads(event["body"])
            return create_post(body)

        if method == "GET" and path == "/posts":
            return get_posts()

        if method == "GET" and path.startswith("/posts/"):
            post_id = path.split("/")[-1]
            return get_post(post_id)

        if method == "PUT" and path.startswith("/posts/"):
            post_id = path.split("/")[-1]
            body = json.loads(event["body"])
            return update_post(post_id, body)

        if method == "DELETE" and path.startswith("/posts/"):
            post_id = path.split("/")[-1]
            return delete_post(post_id)

        return response(404, {"message": "Route not found"})
    except Exception as e:
        logger.error(f"Error logging request: {e}")
