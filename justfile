alias up := docker-up
alias down := docker-down
alias db := docker-build

set dotenv-load := true

REDIS_PASSWORD := env('REDIS_PASSWORD')
K8S_IMAGE := "docker.io/wp-labs/api:1.0.0"

run:
    just docker-up

redism:
    docker exec -it wp_labs_redis redis-cli -a {{ REDIS_PASSWORD }} MONITOR

redis:
    docker exec -it wp_labs_redis redis-cli -a {{ REDIS_PASSWORD }} 

# --- INFO: DOCKER ---

docker-up:
    docker compose up -d 

docker-down:
    docker compose down

docker-build: docker-down
    docker compose up -d --build
    just docker-logs-app

docker-logs-app:
    docker logs -f wp_labs_app

# --- INFO: KUBERNETES ---

k8s-up: k8s-create k8s-build k8s-apply

k8s-down:
    kind delete cluster

k8s-create:
    kind create cluster || true

k8s-build:
    docker build -t {{ K8S_IMAGE }} .
    kind load docker-image {{ K8S_IMAGE }}

k8s-apply:
    kubectl apply -f k8s/00-namespace.yaml
    # kubectl apply -f k8s/01-postgresql/
    kubectl apply -f k8s/02-mongodb/
    kubectl apply -f k8s/03-redis/
    kubectl apply -f k8s/04-minio/
    kubectl apply -f k8s/05-rabbitmq/
    kubectl apply -f k8s/06-api/

k8s-port-api:
    kubectl port-forward svc/api 4200:4200 -n wp-labs

k8s-port-minio:
    kubectl port-forward svc/minio 9001:9001 -n wp-labs

k8s-port-redis:
    kubectl exec -it deployment/redis -n wp-labs -- redis-cli -a redis_secure_password_change_in_prod

k8s-port-redism:
    kubectl exec -it deployment/redis -n wp-labs -- redis-cli -a redis_secure_password_change_in_prod MONITOR

k8s-port-db:
    kubectl port-forward svc/mongo 27017:27017 -n wp-labs

k8s-status:
    kubectl get pods -n wp-labs -w

k8s-logs:
    kubectl logs -f -l app=api -n wp-labs

k8s-scale replicas="4":
    kubectl scale deployment/api --replicas={{ replicas }} -n wp-labs
    kubectl get pods -n wp-labs
