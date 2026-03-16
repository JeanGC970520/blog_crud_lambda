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
awslocal dynamodb list-tables | grep post > /dev/null
if [[ $? -eq 0 ]]; then
    echo "DynamoDB table 'post' exists."
else
    echo "Error: DynamoDB table 'post' does not exist."
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
    --payload '{
    "httpMethod":"POST",
    "path":"/posts",
    "body":"{\"title\":\"Mi primer post\",\"content\":\"Hola mundo\"}"
    }' \
    response.json

cat response.json | jq .id > /dev/null
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

cat response2.json | jq .id > /dev/null
if [[ $? -eq 0 ]]; then
    echo "API Gateway is working correctly."
else
    echo "Error: API Gateway is not working correctly."
    exit 1
fi

awslocal dynamodb scan --table-name post | jq .Items > /dev/null
if [[ $? -eq 0 ]]; then
    echo "DynamoDB 'post' table is working correctly."
else
    echo "Error: DynamoDB 'post' table is not working correctly."
    exit 1
fi

echo "All tests for Blog app passed successfully."

echo "Delete dummy data from DynamoDB table 'post'..."
awslocal dynamodb scan --table-name post --query "Items[].id.S" \
    --output text | xargs -I {} awslocal dynamodb delete-item \
    --table-name post \
    --key '{"id": {"S": "{}"}}'

echo "Dummy data deleted successfully from DynamoDB table 'post'."
