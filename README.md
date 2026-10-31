# web-additional-task-Sidorov

# How to run:

```bash
python3 server.py
```

Open http://127.0.0.1:8080 in a browser.

## Test

```bash
curl -i http://127.0.0.1:8080/
curl -i "http://127.0.0.1:8080/page?id=5"
curl -i http://127.0.0.1:8080/nope
curl -i -X POST http://127.0.0.1:8080/ -H "Content-Type: application/json" -d '{"name": "Mykyta"}'
```
