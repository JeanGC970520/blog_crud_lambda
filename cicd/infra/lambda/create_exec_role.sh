
SCRIPT_DIR=$(dirname "$0")

# Crea la política de IAM con los permisos necesarios para que la función Lambda 
# pueda acceder al servicio DynamoDB y escribir en CloudWatch Logs
awslocal iam create-policy \
    --policy-name blog-lambda-policy \
    --policy-document file://$SCRIPT_DIR/lambda-policy.json

# Crea el rol de ejecución para la función Lambda y adjunta una trust policy
# que permita a  Lambda asumir el rol
awslocal iam create-role \
    --role-name blog-lambda-execution-role \
    --assume-role-policy-document file://$SCRIPT_DIR/trust-policy.json

# Adjunta la política de permisos al rol de ejecución
awslocal iam attach-role-policy \
    --role-name blog-lambda-execution-role \
    --policy-arn arn:aws:iam::000000000000:policy/blog-lambda-policy
