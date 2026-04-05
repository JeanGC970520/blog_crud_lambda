import json
from unittest.mock import patch

from services.blog_crud import handler


def make_event(method, path, body=None, query_params=None):
    """Helper to create Lambda events."""
    event = {"httpMethod": method, "path": path}
    if body is not None:
        event["body"] = json.dumps(body)
    if query_params:
        event["queryStringParameters"] = query_params
    return event


class TestCreatePost:
    """Tests for POST /posts endpoint."""

    def test_create_post_success(self):
        """Test successful blog post creation."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.put_item.return_value = {}

            event = make_event(
                "POST",
                "/posts",
                {
                    "title": "My Post",
                    "author": "John Doe",
                    "tags": ["test", "blog"],
                    "image": "https://example.com/image.jpg",
                    "body": [
                        {"type": "para", "value": "Hello World"},
                        {"type": "code", "value": "print('hello')"},
                    ],
                },
            )
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 201
            body = json.loads(result["body"])
            assert body["title"] == "My Post"
            assert body["author"] == "John Doe"
            assert body["tags"] == ["test", "blog"]
            assert body["image"] == "https://example.com/image.jpg"
            assert len(body["body"]) == 2
            assert "create_at" in body
            assert isinstance(body["create_at"], int)
            assert "id" in body
            mock_table.put_item.assert_called_once()

    def test_create_post_minimal_data(self):
        """Test creating post with only required fields."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.put_item.return_value = {}

            event = make_event(
                "POST",
                "/posts",
                {
                    "title": "Simple Post",
                    "author": "Jane Doe",
                    "tags": ["simple"],
                    "body": [{"type": "para", "value": "Content"}],
                },
            )
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 201
            body = json.loads(result["body"])
            assert body["image"] is None
            assert body["create_at"] is not None


class TestGetPosts:
    """Tests for GET /posts endpoint."""

    def test_get_all_posts(self):
        """Test retrieving all posts without pagination."""
        with patch("services.blog_crud.handler.table") as mock_table:
            posts = [
                {
                    "id": "1",
                    "author": "John Doe",
                    "create_at": 1700000000000,
                    "title": "First Post",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": "Content 1"}],
                },
                {
                    "id": "2",
                    "author": "Jane Doe",
                    "create_at": 1700000000000,
                    "title": "Second Post",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": "Content 2"}],
                },
            ]
            mock_table.scan.return_value = {"Items": posts}

            event = make_event("GET", "/posts")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert len(body) == 2
            assert body[0]["title"] == "First Post"
            assert body[1]["title"] == "Second Post"
            mock_table.scan.assert_called_once_with(Limit=100)

    def test_get_all_posts_by_author(self):
        """Test retrieving all posts filtered by author."""
        with patch("services.blog_crud.handler.table") as mock_table:
            posts = [
                {
                    "id": "1",
                    "author": "John Doe",
                    "create_at": 1700000000000,
                    "title": "First Post",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": "Content 1"}],
                },
                {
                    "id": "3",
                    "author": "John Doe",
                    "create_at": 1700000000001,
                    "title": "Third Post",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": "Content 3"}],
                },
            ]
            mock_table.query.return_value = {"Items": posts}

            event = make_event("GET", "/posts", query_params={"author": "John Doe"})
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert len(body) == 2
            assert all(post["author"] == "John Doe" for post in body)
            assert body[0]["title"] == "First Post"
            assert body[1]["title"] == "Third Post"
            mock_table.query.assert_called_once()
            call_kwargs = mock_table.query.call_args.kwargs
            assert call_kwargs["IndexName"] == "author-index"

    def test_get_posts_by_author_empty_result(self):
        """Test retrieving posts by author with no results."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.query.return_value = {"Items": []}

            event = make_event("GET", "/posts", query_params={"author": "NonExistent"})
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body == []
            mock_table.query.assert_called_once()

    def test_get_posts_by_author_with_pagination(self):
        """Test retrieving posts by author with pagination."""
        with patch("services.blog_crud.handler.table") as mock_table:
            posts_page1 = [
                {
                    "id": str(i),
                    "author": "John Doe",
                    "create_at": 1700000000000,
                    "title": f"Post {i}",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": f"Content {i}"}],
                }
                for i in range(1, 51)
            ]
            posts_page2 = [
                {
                    "id": str(i),
                    "author": "John Doe",
                    "create_at": 1700000000000,
                    "title": f"Post {i}",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": f"Content {i}"}],
                }
                for i in range(51, 76)
            ]

            mock_table.query.side_effect = [
                {"Items": posts_page1, "LastEvaluatedKey": {"id": "50"}},
                {"Items": posts_page2},
            ]

            event = make_event("GET", "/posts", query_params={"author": "John Doe"})
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert len(body) == 75
            assert all(post["author"] == "John Doe" for post in body)
            assert mock_table.query.call_count == 2

    def test_get_posts_with_pagination(self):
        """Test retrieving posts with pagination handling."""
        with patch("services.blog_crud.handler.table") as mock_table:
            posts_page1 = [
                {
                    "id": str(i),
                    "author": f"Author {i}",
                    "create_at": 1700000000000,
                    "title": f"Post {i}",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": f"Content {i}"}],
                }
                for i in range(1, 101)
            ]
            posts_page2 = [
                {
                    "id": str(i),
                    "author": f"Author {i}",
                    "create_at": 1700000000000,
                    "title": f"Post {i}",
                    "tags": ["test"],
                    "image": None,
                    "body": [{"type": "para", "value": f"Content {i}"}],
                }
                for i in range(101, 151)
            ]

            mock_table.scan.side_effect = [
                {"Items": posts_page1, "LastEvaluatedKey": {"id": "100"}},
                {"Items": posts_page2},
            ]

            event = make_event("GET", "/posts")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert len(body) == 150
            assert mock_table.scan.call_count == 2

    def test_get_empty_posts(self):
        """Test retrieving posts when database is empty."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.scan.return_value = {"Items": []}

            event = make_event("GET", "/posts")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body == []


class TestGetPostById:
    """Tests for GET /posts/{id} endpoint."""

    def test_get_post_by_id_success(self):
        """Test successfully retrieving a post by ID."""
        with patch("services.blog_crud.handler.table") as mock_table:
            post = {
                "id": "abc-123",
                "author": "John Doe",
                "create_at": 1700000000000,
                "title": "My Post",
                "tags": ["test"],
                "image": "https://example.com/image.jpg",
                "body": [{"type": "para", "value": "Hello World"}],
            }
            mock_table.get_item.return_value = {"Item": post}

            event = make_event("GET", "/posts/abc-123")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body["id"] == "abc-123"
            assert body["title"] == "My Post"
            assert body["author"] == "John Doe"
            mock_table.get_item.assert_called_once_with(Key={"id": "abc-123"})

    def test_get_post_not_found(self):
        """Test retrieving a post that doesn't exist."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.get_item.return_value = {}

            event = make_event("GET", "/posts/nonexistent")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 404
            body = json.loads(result["body"])
            assert body["message"] == "Post not found"


class TestUpdatePost:
    """Tests for PUT /posts/{id} endpoint."""

    def test_update_post_success(self):
        """Test successfully updating a post."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.update_item.return_value = {}

            event = make_event(
                "PUT",
                "/posts/abc-123",
                {
                    "author": "John Doe",
                    "title": "Updated Title",
                    "tags": ["updated", "test"],
                    "image": "https://example.com/new-image.jpg",
                    "body": [{"type": "para", "value": "Updated Content"}],
                },
            )
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body["message"] == "Post updated"
            mock_table.update_item.assert_called_once()
            call_args = mock_table.update_item.call_args
            assert call_args.kwargs["Key"] == {"id": "abc-123"}
            assert ":a" in call_args.kwargs["ExpressionAttributeValues"]
            assert (
                call_args.kwargs["ExpressionAttributeValues"][":t"] == "Updated Title"
            )

    def test_update_post_partial_data(self):
        """Test updating a post with minimal data."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.update_item.return_value = {}

            event = make_event(
                "PUT",
                "/posts/xyz-789",
                {
                    "author": "Jane Doe",
                    "title": "New Title",
                    "tags": ["updated"],
                    "image": None,
                    "body": [{"type": "para", "value": "New content"}],
                },
            )
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            mock_table.update_item.assert_called_once()


class TestDeletePost:
    """Tests for DELETE /posts/{id} endpoint."""

    def test_delete_post_success(self):
        """Test successfully deleting a post."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.delete_item.return_value = {}

            event = make_event("DELETE", "/posts/abc-123")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body["message"] == "Post deleted"
            mock_table.delete_item.assert_called_once_with(Key={"id": "abc-123"})


class TestErrorHandling:
    """Tests for error cases and invalid routes."""

    def test_invalid_route(self):
        """Test request to non-existent endpoint."""
        with patch("services.blog_crud.handler.table"):
            event = make_event("GET", "/invalid/route")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 404
            body = json.loads(result["body"])
            assert body["message"] == "Route not found"

    def test_invalid_method(self):
        """Test invalid HTTP method."""
        with patch("services.blog_crud.handler.table"):
            event = make_event("PATCH", "/posts/abc-123")
            result = handler.lambda_handler(event, None)

            assert result["statusCode"] == 404
            body = json.loads(result["body"])
            assert body["message"] == "Route not found"

    def test_response_headers(self):
        """Test that responses have correct Content-Type header."""
        with patch("services.blog_crud.handler.table") as mock_table:
            mock_table.scan.return_value = {"Items": []}
            event = make_event("GET", "/posts")
            result = handler.lambda_handler(event, None)

            assert result["headers"]["Content-Type"] == "application/json"
            assert "body" in result
            assert isinstance(result["body"], str)
