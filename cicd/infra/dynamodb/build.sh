awslocal dynamodb create-table \
    --table-name posts \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Verificamos que la tabla se ha creado correctamente
awslocal dynamodb list-tables