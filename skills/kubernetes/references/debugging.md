# Kubernetes Debugging Guide

## Pod Troubleshooting Flowchart

### Pod Pending

```bash
# Check events
kubectl describe pod <pod> | grep -A 10 Events

# Common causes:
# - Insufficient resources → kubectl describe node | grep -A 5 Allocated
# - No matching node (nodeSelector/affinity) → check pod spec
# - PVC not bound → kubectl get pvc
# - Image pull issues → check imagePullSecrets
```

### Pod CrashLoopBackOff

```bash
# Check previous logs
kubectl logs <pod> --previous

# Check exit code
kubectl describe pod <pod> | grep "Exit Code"
# Exit 0 = normal exit (check readiness/liveness probes)
# Exit 1 = app error
# Exit 137 = OOMKilled (increase memory limit)
# Exit 139 = Segfault

# Check OOM
kubectl describe pod <pod> | grep OOMKilled
```

### Pod ImagePullBackOff

```bash
# Check image name/tag
kubectl describe pod <pod> | grep Image

# Verify registry access
kubectl get secret -n <namespace>
kubectl create secret docker-registry regcred \
  --docker-server=registry.io \
  --docker-username=user \
  --docker-password=pass
```

## Network Debugging

```bash
# DNS resolution
kubectl run debug --rm -it --image=busybox -- nslookup my-service

# HTTP connectivity
kubectl run debug --rm -it --image=curlimages/curl -- \
  curl -v http://my-service:8080/health

# Check service endpoints
kubectl get endpoints my-service
# Empty endpoints = selector doesn't match pod labels

# Check network policy
kubectl get networkpolicy -n <namespace>

# Port-forward for local testing
kubectl port-forward svc/my-service 8080:80
```

## Resource Debugging

```bash
# Node resources
kubectl top nodes
kubectl describe node <node> | grep -A 10 "Allocated resources"

# Pod resources
kubectl top pods
kubectl top pods --containers  # Per container

# Events (cluster-wide)
kubectl get events --sort-by='.lastTimestamp' -A
kubectl get events --field-selector type=Warning
```

## Debug Container

```bash
# Ephemeral debug container (K8s 1.23+)
kubectl debug -it <pod> --image=busybox --target=<container>

# Debug node
kubectl debug node/<node> -it --image=ubuntu

# Copy pod for debugging (with different command)
kubectl debug <pod> -it --copy-to=debug-pod --container=app -- sh
```

## Common Checks

```bash
# Is my app healthy?
kubectl get pods -l app=web
kubectl logs -l app=web --tail=10

# Why can't pods talk to each other?
kubectl get svc
kubectl get endpoints
kubectl get networkpolicy

# Why is my deployment not updating?
kubectl rollout status deployment/web
kubectl describe deployment web

# What's using all the resources?
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu
```
