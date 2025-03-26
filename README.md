# JSON Data API

A simple REST API that serves data from a JSON file.

## Setup


1. Build the container:
```bash
podman build -t json-api .
```

2. Run the container:
```bash
podman run -d -p 8000:8000 --name json-api json-api
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Welcome message
- `GET /items`: Get all items
- `GET /items/{item_id}`: Get a specific item by ID
- `GET /items/category/{category}`: Get items by category
- `GET /items/search/`: Search items with filters
  - Query parameters:
    - `min_price`: Minimum price filter
    - `max_price`: Maximum price filter
    - `category`: Category filter

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Container Management

To stop the container:
```bash
podman stop json-api
```

To remove the container:
```bash
podman rm json-api
```

To view container logs:
```bash
podman logs json-api
``` 