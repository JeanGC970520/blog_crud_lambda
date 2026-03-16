
# This script creates a new REST API in LocalStack's API Gateway using the AWS CLI.
# It assigns the resulting API ID to the variable API_ID.
# - The API is named "blog-api" with a description "API REST para el blog".
# - The output is set to text format and only the 'id' field is queried.
API_ID=$(awslocal apigateway create-rest-api \
    --name blog-api \
    --description "API REST para el blog" \
    --output text \
    --query 'id')

# This script configures AWS API Gateway resources and methods using LocalStack.
# It performs the following actions:
#
# 1. Creates a "/posts" resource under the API root.
# 2. Adds POST and GET methods to the "/posts" resource, integrating both with a Lambda function using AWS_PROXY.
# 3. Creates a "/posts/{id}" resource under "/posts" for individual post operations.
# 4. Adds GET, PUT, and DELETE methods to the "/posts/{id}" resource, each integrated with the same Lambda function using AWS_PROXY.
#
# All resources and methods are created using the awslocal CLI, which interacts with LocalStack's emulated AWS services.
# The script assumes that the environment variable $API_ID is set to the target API Gateway REST API ID.
# The Lambda function ARN used for integration is "arn:aws:lambda:us-east-1:000000000000:function:blog_crud".

# Create the "/posts" resource
awslocal apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[0].id') \
    --path-part posts

awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[1].id') \
    --http-method POST \
    --authorization-type NONE

awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[1].id') \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:blog_crud/invocations"

awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[1].id') \
    --http-method GET \
    --authorization-type NONE

awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[1].id') \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method GET \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:blog_crud/invocations"

# Create the "/posts/{id}" resource
awslocal apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[1].id') \
    --path-part '{id}'

awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method GET \
    --authorization-type NONE 

awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method GET \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:blog_crud/invocations"

awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method PUT \
    --authorization-type NONE

awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method PUT \
    --type AWS_PROXY \
    --integration-http-method PUT \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:blog_crud/invocations"

awslocal apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method DELETE \
    --authorization-type NONE

awslocal apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $(awslocal apigateway get-resources --rest-api-id $API_ID --output text --query 'items[2].id') \
    --http-method DELETE \
    --type AWS_PROXY \
    --integration-http-method DELETE \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:blog_crud/invocations"

# Finally, we deploy the API to a stage named "dev" to make it accessible for testing and use.
awslocal apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name dev