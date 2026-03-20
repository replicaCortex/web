curl -s http://127.0.0.1:4200/ | python -m json.tool
curl -s -X POST http://127.0.0.1:4200/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "os": "linux",
    "totaltime": 42
  }' | python -m json.tool
curl -s -X POST http://127.0.0.1:4200/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "os": "linux",
    "totaltime": 42
  }' | python -m json.tool
curl -s http://127.0.0.1:4200/users/ | python -m json.tool
curl -s http://127.0.0.1:4200/users/1 | python -m json.tool
curl -s http://127.0.0.1:4200/users/999 | python -m json.tool
curl -s -X PATCH http://127.0.0.1:4200/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "john.updated@example.com"}' | python -m json.tool
curl -s -X DELETE http://127.0.0.1:4200/users/1 -w "\nHTTP Status: %{http_code}\n"
curl -s http://127.0.0.1:4200/users/1 | python -m json.tool
