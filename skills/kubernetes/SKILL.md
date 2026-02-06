---
name: kubernetes
description: Kubernetes and kubectl mastery for deployments, services, pods, debugging, and cluster management. Use when user asks to "deploy to k8s", "create deployment", "debug pod", "kubectl commands", "scale service", "check pod logs", "create ingress", or any Kubernetes tasks.
---

# Kubernetes

Essential kubectl commands and Kubernetes patterns.

## Context & Namespace

```bash
# View contexts
kubectl config get-contexts
kubectl config current-context

# Switch context
kubectl config use-context production

# Set default namespace
kubectl config set-context --current --namespace=my-app

# Use namespace in command
kubectl get pods -n kube-system
kubectl get pods --all-namespaces  # or -A
```

## Pods

```bash
# List pods
kubectl get pods
kubectl get pods -o wide              # More details
kubectl get pods -w                    # Watch mode
kubectl get pods --show-labels
kubectl get pods -l app=web            # By label

# Pod details
kubectl describe pod my-pod
kubectl get pod my-pod -o yaml

# Logs
kubectl logs my-pod
kubectl logs my-pod -f                 # Follow
kubectl logs my-pod --tail=100
kubectl logs my-pod -c my-container    # Specific container
kubectl logs my-pod --previous         # Previous crash

# Exec into pod
kubectl exec -it my-pod -- /bin/sh
kubectl exec -it my-pod -c my-container -- bash

# Port forward
kubectl port-forward my-pod 8080:80
kubectl port-forward svc/my-service 8080:80

# Copy files
kubectl cp my-pod:/app/file.txt ./file.txt
kubectl cp ./file.txt my-pod:/app/

# Delete
kubectl delete pod my-pod
kubectl delete pod my-pod --grace-period=0 --force
```

## Deployments

```bash
# Create deployment
kubectl create deployment web --image=nginx:latest --replicas=3

# List
kubectl get deployments
kubectl get deploy

# Scale
kubectl scale deployment web --replicas=5

# Update image
kubectl set image deployment/web nginx=nginx:1.25

# Rollout status
kubectl rollout status deployment/web

# Rollback
kubectl rollout undo deployment/web
kubectl rollout undo deployment/web --to-revision=2

# History
kubectl rollout history deployment/web

# Restart (rolling)
kubectl rollout restart deployment/web
```

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.25
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          env:
            - name: NODE_ENV
              value: "production"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
```

## Services

```yaml
# ClusterIP (internal)
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080

---
# LoadBalancer (external)
apiVersion: v1
kind: Service
metadata:
  name: web-public
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080

---
# NodePort
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

```bash
# Quick expose
kubectl expose deployment web --port=80 --target-port=8080
kubectl expose deployment web --type=LoadBalancer --port=80

# List services
kubectl get svc
kubectl describe svc web
```

## ConfigMaps & Secrets

```bash
# ConfigMap
kubectl create configmap app-config --from-literal=key=value
kubectl create configmap app-config --from-file=config.yaml

# Secret
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# View
kubectl get configmap app-config -o yaml
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 -d
```

## Apply & Delete

```bash
# Apply manifest
kubectl apply -f deployment.yaml
kubectl apply -f ./k8s/              # All files in directory
kubectl apply -f https://example.com/manifest.yaml

# Delete
kubectl delete -f deployment.yaml
kubectl delete deployment web
kubectl delete all -l app=web        # By label

# Dry run
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server
```

## Debugging Quick Reference

```bash
# Pod not starting?
kubectl describe pod my-pod          # Check Events section
kubectl get events --sort-by='.lastTimestamp'

# CrashLoopBackOff?
kubectl logs my-pod --previous       # Logs from crashed container

# Can't connect to service?
kubectl get endpoints my-service     # Check if endpoints exist
kubectl run debug --rm -it --image=busybox -- wget -qO- http://my-service

# Resource issues?
kubectl top pods
kubectl top nodes
kubectl describe node <node-name>    # Check Allocatable vs Allocated
```

## Reference

For debugging patterns: `references/debugging.md`
For YAML templates: `references/manifests.md`
