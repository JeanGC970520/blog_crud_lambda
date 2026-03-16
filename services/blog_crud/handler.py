import datetime as dt
import json
import logging
import uuid

import boto3
import pydantic
import pytz

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localstack:4566")

table = dynamodb.Table("posts")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PostRequestModel(pydantic.BaseModel):
    """Pydantic model for validating incoming blog post requests.

    Attributes:
        author (str): The author of the blog post.
        create_at (int | None): Unix timestamp of when the post was created. Defaults to None.
        title (str): The title of the blog post.
        tags (list[str]): List of tags associated with the blog post.
        image (str | None): URL or path to the blog post's featured image. Defaults to None.
        body (list[dict[str, str]]): List of content blocks, each containing:
            - type (str): Content block type ("head", "para", "quote", "image", or "code")
            - value (str): The content value for the block
    """

    author: str
    create_at: int | None = None
    title: str
    tags: list[str]
    image: str | None = None
    body: list[dict[str, str]]


class PostResponseModel(PostRequestModel):
    id: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def create_post(post: PostRequestModel):

    mexico_tz = pytz.timezone("America/Mexico_City")
    # Multiplying by 1000 to convert seconds to milliseconds
    created_at = int(dt.datetime.now(tz=mexico_tz).timestamp() * 1000)

    post_response = PostResponseModel(**post, create_at=created_at)

    table.put_item(Item=post_response.model_dump())

    return response(201, post_response.model_dump())


def get_posts() -> dict:

    result = table.scan()

    return response(200, result["Items"])


def get_post(post_id: str) -> dict:

    result = table.get_item(Key={"id": post_id})

    if "Item" not in result:
        return response(404, {"message": "Post not found"})

    return response(200, result["Item"])


def update_post(post_id: str, post: PostRequestModel) -> dict:

    post_request = PostRequestModel(**post)

    table.update_item(
        Key={"id": post_id},
        UpdateExpression="SET author=:a, title=:t, tags=:tg, image=:i, body=:c",
        ExpressionAttributeValues={
            ":a": post_request.author,
            ":t": post_request.title,
            ":tg": post_request.tags,
            ":i": post_request.image,
            ":c": post_request.body,
        },
    )

    return response(200, {"message": "Post updated"})


def delete_post(post_id: str) -> dict:

    table.delete_item(Key={"id": post_id})

    return response(200, {"message": "Post deleted"})


def lambda_handler(event, _):

    logger.debug(f"Received event:\n{json.dumps(event)}\n")

    method = event["httpMethod"]
    path = event["path"]

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
