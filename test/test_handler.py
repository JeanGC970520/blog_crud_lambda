import json
from unittest.mock import patch

import handler


def make_event(method, path, body=None):
    event = {"httpMethod": method, "path": path}
    if body is not None:
        event["body"] = json.dumps(body)
    return event


def test_lambda_handler_post_posts():
    with patch("handler.table") as mock_table:
        mock_table.put_item.return_value = {}

        event = make_event(
            "POST",
            "/posts",
            {
                "title": "My Post",
                "author": "John Doe",
                "tags": ["test"],
                "image": None,
                "body": [
                    {"type": "test", "value": "Hello World"},
                ],
            },
        )
        result = handler.lambda_handler(event, None)

        assert result["statusCode"] == 201
        body = json.loads(result["body"])
        assert body["title"] == "My Post"
        assert body["author"] == "John Doe"
        assert body["tags"] == ["test"]
        assert body["image"] is None
        assert body["body"] == [{"type": "test", "value": "Hello World"}]
        assert "create_at" in body
        assert "id" in body
        mock_table.put_item.assert_called_once_with(
            Item={
                "id": body["id"],
                "create_at": body["create_at"],
                "author": "John Doe",
                "title": "My Post",
                "tags": ["test"],
                "image": None,
                "body": [{"type": "test", "value": "Hello World"}],
            }
        )


def test_lambda_handler_get_posts():
    with patch("handler.table") as mock_table:
        posts = [
            {
                "id": "1",
                "author": "John Doe",
                "created_at": 1700000000000,
                "title": "First Post",
                "tags": ["test"],
                "image": None,
                "body": [{"type": "test", "value": "Content 1"}],
            },
            {
                "id": "2",
                "author": "John Doe",
                "created_at": 1700000000000,
                "title": "Second Post",
                "tags": ["test"],
                "image": None,
                "body": [{"type": "test", "value": "Content 2"}],
            },
        ]
        mock_table.scan.return_value = {"Items": posts}

        event = make_event("GET", "/posts")
        result = handler.lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert len(body) == 2
        assert body[0]["title"] == "First Post"
        assert body[0]["author"] == "John Doe"
        assert body[0]["created_at"] is not None
        assert body[1]["title"] == "Second Post"
        assert body[1]["author"] == "John Doe"
        assert body[1]["created_at"] is not None
        mock_table.scan.assert_called_once()


def test_lambda_handler_get_post_by_id():
    with patch("handler.table") as mock_table:
        post = {
            "id": "abc-123",
            "author": "John Doe",
            "created_at": 1700000000000,
            "title": "My Post",
            "tags": ["test"],
            "image": None,
            "body": [{"type": "test", "value": "Hello World"}],
        }
        mock_table.get_item.return_value = {"Item": post}

        event = make_event("GET", "/posts/abc-123")
        result = handler.lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["id"] == "abc-123"
        assert body["title"] == "My Post"
        assert body["author"] == "John Doe"
        assert body["created_at"] is not None
        mock_table.get_item.assert_called_once_with(Key={"id": "abc-123"})


def test_lambda_handler_put_post():
    with patch("handler.table") as mock_table:
        mock_table.update_item.return_value = {}

        event = make_event(
            "PUT",
            "/posts/abc-123",
            {
                "author": "John Doe",
                "title": "Updated Title",
                "tags": ["test"],
                "body": [{"type": "test", "value": "Updated Content"}],
            },
        )
        result = handler.lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["message"] == "Post updated"
        mock_table.update_item.assert_called_once_with(
            Key={"id": "abc-123"},
            UpdateExpression="SET author=:a, title=:t, tags=:tg, image=:i, body=:c",
            ExpressionAttributeValues={
                ":a": "John Doe",
                ":t": "Updated Title",
                ":tg": ["test"],
                ":i": None,
                ":c": [{"type": "test", "value": "Updated Content"}],
            },
        )


def test_lambda_handler_delete_post():
    with patch("handler.table") as mock_table:
        mock_table.delete_item.return_value = {}

        event = make_event("DELETE", "/posts/abc-123")
        result = handler.lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["message"] == "Post deleted"
        mock_table.delete_item.assert_called_once_with(Key={"id": "abc-123"})
