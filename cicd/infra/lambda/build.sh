awslocal lambda create-function \
    --function-name blog_api \
    --runtime python3.12 \
    --handler handler.lambda_handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --zip-file fileb://$PWD/services/blog_api/function.zip