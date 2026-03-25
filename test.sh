#!/usr/bin/env bash
BASE=http://localhost:4200

echo "=== 1. Регистрация ==="
curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@test.com","password":"pass123"}' | jq

echo "=== 2. Логин ==="
curl -s -c cookies.txt -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}' | jq

echo "=== 3. Whoami ==="
curl -s -b cookies.txt $BASE/auth/whoami | jq

echo "=== 4. Доступ без токена ==="
curl -s $BASE/users/ | jq

echo "=== 5. Доступ с токеном ==="
curl -s -b cookies.txt $BASE/users/ | jq

echo "=== 6. Refresh ==="
curl -s -c cookies.txt -b cookies.txt -X POST $BASE/auth/refresh | jq

echo "=== 7. Whoami после refresh ==="
curl -s -b cookies.txt $BASE/auth/whoami | jq

echo "=== 8. Logout ==="
curl -s -b cookies.txt -X POST $BASE/auth/logout | jq

echo "=== 9. Whoami после logout ==="
curl -s -b cookies.txt $BASE/auth/whoami | jq

echo "=== 10. Второй пользователь с тем же паролем ==="
curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@test.com","password":"pass123"}' | jq

echo "=== Проверьте хеши в БД: ==="
echo "docker exec -it wp_labs_db psql -U student -d wp_labs -c \"SELECT username, password_hash, salt FROM users;\""

echo "=== 11. Logout-all ==="
curl -s -c cookies.txt -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}' | jq
curl -s -b cookies.txt -X POST $BASE/auth/logout-all | jq
curl -s -b cookies.txt $BASE/auth/whoami | jq
