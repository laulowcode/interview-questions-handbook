# How do you design API versioning to avoid breaking old clients when updating?

### Why is Versioning Necessary?

You need to version your API whenever you make a **breaking change**. A breaking change is any modification that will cause an existing client application to fail.

- **Examples of Breaking Changes:**

  - Changing a JSON field name (e.g., `"name"` to `"fullName"`).
  - Removing an endpoint or a field from a response.
  - Changing the data type of a field (e.g., an `integer` ID to a `string` UUID).
  - Adding a new _required_ field to a request body.

- **Non-Breaking Changes** (usually don't require a new version):

  - Adding a new, _optional_ field to a response.
  - Adding a completely new endpoint.
  - Adding new optional query parameters.

By versioning, you create a contract with your users: `v1` will _always_ work the way it does now, giving them time to migrate to `v2` at their own pace.

---

### Common Versioning Strategies

Here are the three main strategies, with URL Path Versioning being the most popular due to its clarity.

#### 1\. URL Path Versioning (Most Common) ✅

You embed the version number directly into the URL path. It's explicit and easy for developers to understand and use.

- **Example:**

  - `https://api.example.com/v1/products/123`
  - `https://api.example.com/v2/products/123`

- **Pros:**

  - **Extremely clear:** The version is visible in the URL.
  - **Simple to route:** Easy to implement in web frameworks like Flask, FastAPI, or Django.
  - **Browser-friendly:** Easy for developers to test different versions directly in their browser.

- **Cons:**

  - Technically violates the REST principle that a URI should point to a unique resource, not a version of it. However, its practicality often outweighs this theoretical concern.

#### 2\. Query Parameter Versioning

You specify the version as a query parameter in the URL.

- **Example:** `https://api.example.com/products/123?version=1`

- **Pros:**

  - Keeps the base URL clean.
  - Can be easier to default to the "latest" version if the parameter is omitted.

- **Cons:**

  - Less obvious than path versioning.
  - Can clutter URLs that already have many query parameters.

#### 3\. Custom Header Versioning

You use a custom HTTP header to indicate the desired API version. This is often considered the "purest" RESTful approach.

- **Example:**

  - `Accept: application/vnd.example.api.v1+json`
  - Or a simpler custom header: `X-API-Version: 2`

- **Pros:**

  - **Clean URLs:** The URL is not "polluted" with version information at all.
  - Keeps the focus on the resource itself.

- **Cons:**

  - **Less accessible:** You can't test it by simply typing a URL into a browser.
  - Requires clients to be able to set custom headers, which is slightly more complex than just changing a URL.

---

### Python Implementation Example (Using FastAPI)

Organizing your code is key. A great way to do this is by separating the code for each version into its own module or directory.

#### Project Structure

Your project might look like this, with separate folders for `v1` and `v2`:

```
my_project/
├── main.py
└── api/
    ├── __init__.py
    ├── v1/
    │   ├── __init__.py
    │   └── routes.py
    └── v2/
        ├── __init__.py
        └── routes.py
```

#### Code Implementation

**1. Version 1 Logic (`api/v1/routes.py`)**

This version returns a simple user object.

```python
# api/v1/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    # Old response format
    return {"user_id": user_id, "name": "Alex"}
```

**2. Version 2 Logic (`api/v2/routes.py`)**

We introduce a breaking change: `name` becomes `full_name` and we add an `email`.

```python
# api/v2/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    # New, changed response format
    return {"user_id": user_id, "full_name": "Alexandra", "email": "alex@example.com"}
```

**3. Main Application (`main.py`)**

In your main app file, you import and mount each version's router with a versioned prefix. This tells FastAPI to direct requests starting with `/v1` to the `v1` router, and so on.

```python
# main.py
from fastapi import FastAPI
from api.v1 import routes as v1_routes
from api.v2 import routes as v2_routes

app = FastAPI()

# Mount the v1 API router under the /v1 prefix
app.include_router(v1_routes.router, prefix="/v1", tags=["v1"])

# Mount the v2 API router under the /v2 prefix
app.include_router(v2_routes.router, prefix="/v2", tags=["v2"])

@app.get("/")
async def root():
    return {"message": "API is running. Try /v1/users/1 or /v2/users/1"}
```

Now, a request to `GET /v1/users/1` is handled by the `v1` code, while a request to `GET /v2/users/1` is handled by the `v2` code. Old clients using `v1` are completely unaffected by the changes in `v2`.
