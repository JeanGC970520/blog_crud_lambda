# BLOGS API

## Objetivo
Crear una API que permita gestionar posts de un blog, operaciones
```
POST    /posts
GET     /posts
GET     /posts/{id}
PUT     /posts/{id}
DELETE  /posts/{id}
```

## Arquitectura
Buscamos una arquitectura __Serverless__
```
Cliente (curl / Postman)
        │
        ▼
API Gateway
        │
        ▼
Lambda
        │
        ▼
DynamoDB (tabla: posts)
```
## Estructura del proyecto
```
blogs_crud/
│
├── services/
│
│   └── blog-api/
│       │
│       ├── handler.py
│       ├── requirements.txt
│       └── function.zip
│
└── infra/
    └── dynamodb/
```

## How to works

### Paso 1 - Crear tabla de DynamoDB
Diseño simple:
```
Table: posts

PK: id
```
Comando: `sh ./infra/dynamodb/build.sh`

### Paso 2 - Crear Lambda
En `./services/blog_api/handler.py` se tiene la lógica para las operaciones CRUD

### Paso 3 - Zip code
Debemos crear el archivo `function.zip` donde tendremos tanto el codigo como las dependencias de nuestra función Lambda

### Paso 4 - Crear Lambda

### Paso 5 - Crear REST API y sus recursos

