BASE=http://localhost:4200

curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@test.com","password":"pass123"}' | jq

curl -s -c cookies.txt -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}' | jq

curl -s -b cookies.txt $BASE/auth/whoami | jq

curl -s $BASE/users/ | jq

curl -s -b cookies.txt $BASE/users/ | jq

curl -s -c cookies.txt -b cookies.txt -X POST $BASE/auth/refresh | jq

curl -s -b cookies.txt $BASE/auth/whoami | jq

curl -s -b cookies.txt -X POST $BASE/auth/logout | jq

curl -s -b cookies.txt $BASE/auth/whoami | jq

curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@test.com","password":"pass123"}' | jq

curl -s -c cookies.txt -X POST $BASE/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"pass123"}' | jq
curl -s -b cookies.txt -X POST $BASE/auth/logout-all | jq
curl -s -b cookies.txt $BASE/auth/whoami | jq

# docker exec -it wp_labs_db psql -U student -d wp_labs
