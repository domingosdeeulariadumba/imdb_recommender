import redis
from urllib.parse import urlparse
import os

# Fetch the Redis URL from environment variable
redis_url = os.getenv('REDIS_URL')

if not redis_url:
    print("REDIS_URL is not set.")
    exit()

parsed_url = urlparse(redis_url)
print(f"Connecting to Redis at: {parsed_url.hostname}:{parsed_url.port}")

# Establish connection to Redis
r = redis.StrictRedis(
    host=parsed_url.hostname,
    port=parsed_url.port,
    decode_responses=True
)

# Example: Set and get a test key-value pair
test_key = 'test_key'
test_value = 'test_value'

# Set a key-value pair in Redis
r.set(test_key, test_value)

# Retrieve the value from Redis
retrieved_value = r.get(test_key)
print(f"Retrieved value from Redis: {retrieved_value}")

# Optional: Example of fetching data from Redis and doing something with it
# You can modify this part based on your actual use case.
