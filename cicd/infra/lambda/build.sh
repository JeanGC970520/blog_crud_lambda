awslocal lambda create-function \
    --function-name blog_crud \
    --runtime python3.12 \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/blog-lambda-execution-role \
    --zip-file fileb://$PWD/services/blog_crud/function.zip