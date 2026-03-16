echo "Initializating AWS infrastructure in LocalStack..."

EXECUTION_DIR=$(pwd)

INFRA_DIR="$EXECUTION_DIR/cicd/infra"

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

echo "Step 1: Building DynamoDB tables..."
if [[ -f "$INFRA_DIR/dynamodb/build.sh" ]]; then
    sh -x "$INFRA_DIR/dynamodb/build.sh"
else
    echo "Error: DynamoDB build script not found at $INFRA_DIR/dynamodb/build.sh"
    exit 1
fi

echo "Step 2: Building Lambda functions..."
if [[ -f "$EXECUTION_DIR/cicd/scripts/zip_function.sh" ]]; then
    sh -x "$EXECUTION_DIR/cicd/scripts/zip_function.sh"
else
    echo "Error: Lambda packaging script not found at $EXECUTION_DIR/cicd/scripts/zip_function.sh"
    exit 1
fi

if [[ -f "$INFRA_DIR/lambda/create_exec_role.sh" ]]; then
    sh -x "$INFRA_DIR/lambda/create_exec_role.sh"
else
    echo "Error: Lambda execution role script not found at $INFRA_DIR/lambda/create_exec_role.sh"
    exit 1
fi

if [[ -f "$INFRA_DIR/lambda/build.sh" ]]; then
    sh -x "$INFRA_DIR/lambda/build.sh"
else
    echo "Error: Lambda build script not found at $INFRA_DIR/lambda/build.sh"
    exit 1
fi

echo "Step 3: Building API Gateway resources..."
if [[ -f "$INFRA_DIR/api/build.sh" ]]; then
    sh -x "$INFRA_DIR/api/build.sh"
else
    echo "Error: API Gateway build script not found at $INFRA_DIR/api/build.sh"
    exit 1
fi

echo "AWS infrastructure setup completed successfully in LocalStack."