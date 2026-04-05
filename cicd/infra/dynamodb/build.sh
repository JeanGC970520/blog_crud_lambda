awslocal dynamodb create-table \
    --table-name posts \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Verificamos que la tabla se ha creado correctamente
awslocal dynamodb list-tables

# Create GSI (secondary index) for author to optimize queries
awslocal dynamodb update-table \
    --table-name posts \
    --attribute-definitions AttributeName=author,AttributeType=S \
    --global-secondary-index-updates \
    '[{
        "Create": {
            "IndexName": "author-index",
            "KeySchema": [
                {"AttributeName": "author", "KeyType": "HASH"},
                {"AttributeName": "id", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        }
    }]'