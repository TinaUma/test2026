# DevOps Engineer — Review Checklist

### Docker
- [ ] Multi-stage builds
- [ ] Specific version tags (не latest)
- [ ] Non-root user
- [ ] .dockerignore настроен
- [ ] Health checks

### CI/CD
- [ ] GitLab CI pipelines
- [ ] Stages: test → build → deploy
- [ ] Environment-specific rules
- [ ] Manual approval для production
- [ ] Rollback strategy

### Kubernetes
- [ ] Resource requests/limits
- [ ] Liveness/readiness probes
- [ ] Secrets через secretKeyRef
- [ ] SecurityContext настроен
- [ ] HPA для автоскейлинга

### Monitoring
- [ ] RED metrics (Rate, Errors, Duration)
- [ ] Actionable alerts с runbooks
- [ ] SLI/SLO dashboards
- [ ] Log aggregation настроен
