curl -s http://127.0.0.1:4200/ | jq
curl -s -X POST http://127.0.0.1:4200/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "os": "linux",
    "totaltime": 42
  }' | jq
curl -s http://127.0.0.1:4200/users/ | jq
curl -s http://127.0.0.1:4200/users/1 | jq
curl -s http://127.0.0.1:4200/users/999 | jq
curl -s -X PATCH http://127.0.0.1:4200/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "john.updated@example.com"}' | jq
curl -s -X DELETE http://127.0.0.1:4200/users/1 -w "\nHTTP Status: %{http_code}\n"
curl -s -X GET "http://127.0.0.1:4200/users/?page=1&limit=10" | jq

# docker exec -it wp_labs_db psql -U student -d wp_labs
