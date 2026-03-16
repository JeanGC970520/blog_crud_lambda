echo "Iniciando testing de la infraestructura AWS en LocalStack..."
EXECUTION_DIR=$(pwd)
if [[ -z "$EXECUTION_DIR" ]]; then
    echo "Error: EXECUTION_DIR variable is not set."
    exit 1
fi

if curl http://localhost:4566/health &> /dev/null; then
    echo "LocalStack is running."
else
    echo "Error: LocalStack is not running. Please start LocalStack and try again."
    exit 1
fi

echo "Testing DynamoDB table creation..."
awslocal dynamodb list-tables | grep posts > /dev/null
if [[ $? -eq 0 ]]; then
    echo "DynamoDB table 'posts' exists."
else
    echo "Error: DynamoDB table 'posts' does not exist."
    exit 1
fi

echo "Testing Lambda function existence..."
awslocal lambda list-functions | grep blog_crud > /dev/null
if [[ $? -eq 0 ]]; then
    echo "Lambda function 'blog_crud' exists."
else
    echo "Error: Lambda function 'blog_crud' does not exist."
    exit 1
fi

echo "Testing API Gateway resources..."
awslocal apigateway get-rest-apis | grep blog-api > /dev/null
if [[ $? -eq 0 ]]; then
    echo "API Gateway 'blog-api' exists."
else
    echo "Error: API Gateway 'blog-api' does not exist."
    exit 1
fi

echo "All tests passed successfully. AWS infrastructure is set up correctly in LocalStack."

echo "Test Blog app"
awslocal lambda invoke \
    --function-name blog_crud \
    --cli-binary-format raw-in-base64-out \
    --payload '{
    "httpMethod":"POST",
    "path":"/posts",
    "body":"{\"title\":\"Mi primer post\",\"content\":\"Hola mundo\"}"
    }' \
    response.json

cat response.json
if [[ $? -eq 0 ]]; then
    echo "Blog Service is working correctly."
else
    echo "Error: Blog Service is not working correctly."
    exit 1
fi

API_ID=$(awslocal apigateway get-rest-apis --query "items[?name=='blog-api'].id" --output text)
curl -X POST http://$API_ID.execute-api.localhost.localstack.cloud:4566/dev/posts \
    -H "Content-Type: application/json" \
    -d '{"title":"Mi segundo post","content":"Hola de nuevo"}' > response2.json

cat response2.json
if [[ $? -eq 0 ]]; then
    echo "API Gateway is working correctly."
else
    echo "Error: API Gateway is not working correctly."
    exit 1
fi

awslocal dynamodb scan --table-name posts | jq .Items
if [[ $? -eq 0 ]]; then
    echo "DynamoDB 'posts' table is working correctly."
else
    echo "Error: DynamoDB 'posts' table is not working correctly."
    exit 1
fi

echo "All tests for Blog app passed successfully."

echo "Delete dummy data from DynamoDB table 'posts'..."
awslocal dynamodb scan --table-name posts --query "Items[].id.S" \
    --output text | xargs -I {} awslocal dynamodb delete-item \
    --table-name posts \
    --key '{"id": {"S": "{}"}}'

echo "Dummy data deleted successfully from DynamoDB table 'posts'."
