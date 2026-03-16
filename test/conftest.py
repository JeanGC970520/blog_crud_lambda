import os
import sys

# Provide dummy AWS credentials so boto3 doesn't raise NoCredentialsError on import
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

# Make the handler module importable
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "services", "blog_crud")
)
