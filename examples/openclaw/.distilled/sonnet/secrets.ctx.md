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


## Key Patterns


**Storing a secret:**
```typescript
// When user provides a token via `openclaw configure`:
const ref = await storeSecret("discord", "bot-token", userInputToken)
// ref = { "$ref": "discord/bot-token" }
// Write ref into config (not the token itself)
await mutateConfigFile(path, c => { c.channels.discord.config.token = ref })
```

**Resolving a secret:**
```typescript
const tokenRef = config.channels.discord.config.token
if (isSecretRef(tokenRef)) {
  const token = await resolveSecretValue(tokenRef)
  // use token for API call
}
```


## SecretRef Surface


Config paths that support SecretRef (managed by `openclaw secrets configure/apply/audit`):

**Model providers:** `models.providers.*.apiKey`, `models.providers.*.headers.*`, `models.providers.*.request.auth.token`

**Skills + memory:** `skills.entries.*.apiKey`, `agents.defaults.memorySearch.remote.apiKey`

**Gateway auth:** `gateway.auth.password`, `gateway.auth.token`, `gateway.remote.token`, `cron.webhookToken`

**Channel tokens (selection):**
- Telegram: `channels.telegram.botToken`, `channels.telegram.accounts.*.botToken`
- Discord: `channels.discord.token`, `channels.discord.accounts.*.token`
- Slack: `channels.slack.botToken`, `channels.slack.signingSecret`, accounts variants
- Matrix: `channels.matrix.accessToken`, `channels.matrix.password`
- Mattermost: `channels.mattermost.botToken`

**Auth profile secrets:** `profiles.*.keyRef` (`type: "api_key"`), `profiles.*.tokenRef` (`type: "token"`)

**Out of scope (unsupported):**
- OAuth credentials (`auth-profiles.oauth.*`)
- Runtime-minted tokens (Discord thread webhook tokens)
- WhatsApp session files (`channels.whatsapp.creds.json`)
- Command secrets (`commands.ownerDisplaySecret`)

**OAuth policy guard:** `auth.profiles.<id>.mode = "oauth"` cannot be combined with SecretRef inputs for that profile — startup fails fast on violation.

```bash
openclaw secrets configure   # interactive: store a secret
openclaw secrets apply       # apply SecretRefs from a plan file
openclaw secrets audit       # show all SecretRef accesses + coverage
```


## Cross-References


- [[modules/config.ctx|config]] — SecretRef values appear throughout config schema
- [[modules/infra.ctx|infra]] — file I/O utilities for secret store
- [[modules/agents.ctx|agents]] — auth-profiles.json managed by secrets module for API key + OAuth storage
