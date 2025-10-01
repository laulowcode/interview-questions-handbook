
# Redis Caching: Common Patterns and Best Practices

**Redis, an in-memory data structure store, is exceptionally popular for caching due to its speed and versatility. Caching is a crucial technique for improving application performance by storing frequently accessed data in a location that is faster to access than the original source (like a database or an external API).**

**This guide covers the most common Redis caching patterns, including API result caching, database query caching, and strategies for cache invalidation.**

## 1. Cache-Aside Pattern (Lazy Loading)

**This is the most common caching strategy. The application logic is responsible for managing the cache.**

**How it works:**

1. **When your application needs data, it first checks the Redis cache.**
2. **Cache Hit:** If the data is found in the cache, it's returned directly to the client. This is fast.
3. **Cache Miss:** If the data is not in the cache, the application retrieves it from the primary data source (e.g., a database or an external API).
4. **The application then stores this newly retrieved data in the Redis cache before returning it to the client. Subsequent requests for the same data will result in a cache hit.**

### A. API Result Caching

**Use Case:** You have an endpoint that calls a slow third-party API or performs a computationally expensive task. Caching the final result can dramatically reduce latency for repeated requests.

**Pattern:**

* **A client requests data from an API endpoint.**
* **The application generates a unique cache key based on the request parameters (e.g., URL path, query params).**
* **It checks Redis for this key.**
* **On a cache miss, it performs the expensive operation (e.g., calls the external API), caches the result with a Time-to-Live (TTL), and then returns it.**

**Python Example (using a Flask decorator):**

**Here is a simple way to implement API result caching using a Python decorator. The decorator handles the cache-checking logic automatically.**

```
import redis
import json
import time
from functools import wraps
from flask import Flask, request, jsonify

# Assume redis_client is a configured Redis connection instance
# Assume app is a configured Flask app instance

def cache_api_result(ttl_seconds):
    """
    A decorator to cache the result of a Flask view function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create a unique cache key from the request path and args
            cache_key = f"api:{request.path}?{request.query_string.decode('utf-8')}"
          
            # 1. Try to get the result from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                print(f"CACHE HIT for key: {cache_key}")
                return jsonify(json.loads(cached_result))

            # 2. If it's a cache miss, call the original function
            print(f"CACHE MISS for key: {cache_key}")
            result = f(*args, **kwargs)
          
            # 3. Store the result in Redis with a TTL
            redis_client.setex(cache_key, ttl_seconds, result.get_data(as_text=True))
          
            return result
        return decorated_function
    return decorator

@app.route('/weather')
@cache_api_result(ttl_seconds=30) # Cache the result for 30 seconds
def get_weather():
    """
    Simulates a slow API call to a weather service.
    """
    city = request.args.get('city', 'Hanoi')
    print(f"Fetching weather for {city} from a 'slow' external service...")
    time.sleep(2)  # Simulate network latency
  
    weather_data = { "city": city, "temperature_celsius": 30 }
    return jsonify(weather_data)

```

### B. Database Query Caching

**Use Case:** You have database queries that are executed frequently but whose results don't change often. Examples include fetching user profiles, product catalogs, or application configuration.

**Pattern:**

* **The application needs to fetch data from the database.**
* **It creates a unique cache key representing the query (e.g., **`<span class="selected">user:123</span>`, `<span class="selected">products:all</span>`).
* **It checks Redis for this key.**
* **On a cache miss, it executes the query against the database, caches the result (often serialized as JSON), and returns it.**

## 2. Cache Invalidation

**Keeping cached data consistent with the source data is a critical challenge. Stale data in the cache can lead to incorrect application behavior. Here are the common strategies for cache invalidation.**

### A. Time-to-Live (TTL) Caching

**This is the simplest invalidation strategy. When you store an item in the cache, you set an expiration time. Redis will automatically evict the key after the specified duration.**

* **Pros:** Simple to implement. Protects against serving extremely stale data. It's a good default strategy.
* **Cons:** The data can be stale for the duration of the TTL. For applications requiring strong consistency, this might not be suitable.

### B. Manual Invalidation (on Data Change)

**When using the Cache-Aside pattern, the application logic must explicitly invalidate the cache whenever the source data is modified (created, updated, or deleted).**

**How it works:**

1. **The application receives a request to write/update/delete data (e.g., update a user's profile).**
2. **It first updates the data in the primary database.**
3. **After a successful database operation, it sends a **`<span class="selected">DEL</span>` command to Redis to remove the corresponding cache key.
4. **The next time the data is requested, it will be a cache miss, and the application will fetch the fresh data from the database and repopulate the cache.**

* **Pros:** Ensures that stale data is removed from the cache as soon as it changes, leading to better consistency than TTL alone.
* **Cons:** Requires more application logic to track and delete cache keys. There's a small chance of a race condition if another process reads from the database just before the cache is invalidated.

### C. Write-Through Caching

**In this pattern, the application writes data to the cache and the database at the same time. The cache is always up-to-date.**

**How it works:**

1. **The application receives a request to write/update data.**
2. **It first writes the data to the Redis cache.**
3. **Then, it immediately writes the same data to the primary database.**
4. **The write operation is only considered complete after data is successfully written to both stores.**

* **Pros:** Provides strong consistency between the cache and the database. Data in the cache is never stale.
* **Cons:** Introduces write latency, as every write operation has to go to two systems. It can be more complex to implement correctly, especially handling failures where the cache write succeeds but the database write fails. This pattern is less common for read-heavy applications where Cache-Aside is sufficient.

**The accompanying **`<span class="selected">caching_examples.py</span>` file provides a practical implementation of these concepts using Python, Flask, and the `<span class="selected">redis-py</span>` library.
