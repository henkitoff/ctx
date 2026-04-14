---
module: modules/secrets
type: codebase
depends_on: [infra]
depended_by: [config]
provides: [resolveSecretValue, isSecretRef, SecretRef, auditSecretsUsage]
invariants:
  - "Plain secret values never stored in config.json — always as SecretRef"
  - "Secret resolution happens at runtime, not at config load"
  - "Audit trail required for all secret accesses in production"
keywords: [secrets, encryption, secretref, audit, crypto, store]
---

## Purpose


The `secrets` module provides **encrypted secret storage**: secrets are stored
in `~/.openclaw/store.secret` (AES + master key), referenced in config via
`SecretRef`, and resolved at runtime.

Key components:
- **`crypto.ts`** — AES encryption/decryption
- **`store.ts`** — Secret file storage
- **`resolution.ts`** — `SecretRef` → resolved value
- **`audit.ts`** — Secret usage audit trail


## Public API


| Export | Type | Purpose |
|--------|------|---------|
| `SecretRef` | type | `{ "$ref": "provider/key" }` — pointer to secret |
| `isSecretRef` | fn | Type guard: is this value a SecretRef? |
| `resolveSecretValue` | fn | Decrypt and return secret value |
| `auditSecretsUsage` | fn | Record secret access to audit log |


## Invariants


1. **No plain values in config.json** — always `SecretRef` for sensitive fields
2. Resolution is **runtime-only** — not at config parse time
3. Every production secret access is **audited** (caller, timestamp, key)
4. Master key is derived from device keychain — never hardcoded


## Cross-References


- [[modules/config.ctx|config]] — SecretRef values appear throughout config schema
- [[modules/infra.ctx|infra]] — file I/O utilities for secret store
- [[modules/agents.ctx|agents]] — auth-profiles.json managed by secrets module for API key + OAuth storage
