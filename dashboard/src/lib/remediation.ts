# remediation.ts - Knowledge Base
# Contains 17 RemediationGuide entries covering:
# Network: open MySQL port, SSH hardening, RDP filtering, outdated kernel
# Web App: SQL injection, XSS, exposed .env files
# Code Security: vulnerable deps (lodash, jsonwebtoken), exposed secrets (AWS, Slack),
#               weak password hashing (MD5), insecure deserialization, debug mode
# TLS: weak ciphers, certificate expiry
# Monitoring: port scan detection, unencrypted auth
# 
# Each guide includes: explanation, why_it_matters, fix_steps,
# code_vulnerable, code_fixed, prevention, tools_to_verify,
# estimated_time, skill_level, references
