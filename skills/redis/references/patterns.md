# Redis Advanced Patterns

## Caching Strategies

### Cache-Aside (Lazy Loading)

```python
def get_user(user_id):
    # 1. Check cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # 2. Cache miss - query DB
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)

    # 3. Populate cache
    redis.setex(f"user:{user_id}", 300, json.dumps(user))  # 5 min TTL
    return user
```

### Write-Through

```python
def update_user(user_id, data):
    # 1. Update DB
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)

    # 2. Update cache
    redis.setex(f"user:{user_id}", 300, json.dumps(data))
```

### Cache Invalidation

```python
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)
    redis.delete(f"user:{user_id}")  # Invalidate instead of update
```

## Rate Limiting

### Fixed Window

```python
def is_rate_limited(user_id, limit=100, window=60):
    key = f"ratelimit:{user_id}:{int(time.time()) // window}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, window)
    return count > limit
```

### Sliding Window (Sorted Set)

```python
def is_rate_limited(user_id, limit=100, window=60):
    key = f"ratelimit:{user_id}"
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()
    return count > limit
```

### Token Bucket

```python
def acquire_token(user_id, rate=10, capacity=20):
    key = f"bucket:{user_id}"
    now = time.time()

    # Lua script for atomicity
    script = """
    local tokens = tonumber(redis.call('HGET', KEYS[1], 'tokens') or ARGV[3])
    local last = tonumber(redis.call('HGET', KEYS[1], 'last') or ARGV[1])
    local elapsed = ARGV[1] - last
    tokens = math.min(tonumber(ARGV[3]), tokens + elapsed * tonumber(ARGV[2]))
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last', ARGV[1])
        redis.call('EXPIRE', KEYS[1], ARGV[4])
        return 1
    end
    return 0
    """
    return redis.eval(script, 1, key, now, rate, capacity, capacity * 2)
```

## Pub/Sub Patterns

### Event Broadcasting

```python
# Publisher
redis.publish("events:user", json.dumps({
    "type": "user_created",
    "user_id": 123,
    "timestamp": time.time()
}))

# Subscriber
pubsub = redis.pubsub()
pubsub.subscribe("events:user")

for message in pubsub.listen():
    if message["type"] == "message":
        event = json.loads(message["data"])
        handle_event(event)
```

### Pattern Subscription

```python
pubsub.psubscribe("events:*")  # All event channels

for message in pubsub.listen():
    if message["type"] == "pmessage":
        channel = message["channel"]  # e.g., "events:user"
        data = json.loads(message["data"])
```

## Lua Scripts

```bash
# Atomic compare-and-set
EVAL "
  local current = redis.call('GET', KEYS[1])
  if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1
  end
  return 0
" 1 mykey "old_value" "new_value"

# Atomic increment with cap
EVAL "
  local current = tonumber(redis.call('GET', KEYS[1]) or 0)
  if current < tonumber(ARGV[1]) then
    return redis.call('INCR', KEYS[1])
  end
  return -1
" 1 counter 100
```

## Streams (Event Log)

```bash
# Add to stream
XADD events * type "order" user_id "123" amount "99.99"

# Read from beginning
XRANGE events - + COUNT 10

# Read new entries (consumer)
XREAD COUNT 10 BLOCK 5000 STREAMS events $

# Consumer groups
XGROUP CREATE events mygroup $ MKSTREAM
XREADGROUP GROUP mygroup consumer1 COUNT 10 BLOCK 5000 STREAMS events >

# Acknowledge processed
XACK events mygroup <message-id>
```

## Monitoring

```bash
# Real-time command monitor
redis-cli monitor

# Memory analysis
redis-cli --bigkeys
redis-cli --memkeys

# Slow log
CONFIG SET slowlog-log-slower-than 10000  # 10ms
SLOWLOG GET 10

# Info sections
INFO memory
INFO stats
INFO clients
INFO replication
```
