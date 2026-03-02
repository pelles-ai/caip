# Security Recommendations

This document describes known security considerations for the CAIP SDK and example orchestrator. These findings were identified during a security review of the `sdk-and-protocol` branch.

---

## SSRF-1: User-Controlled Agent URLs in Orchestrator Endpoints

**Severity:** High
**Category:** Server-Side Request Forgery (SSRF)
**Affected files:** `examples/orchestrator/app.py`

### Description

Three orchestrator endpoints accept a user-controlled URL and make server-side HTTP requests to it with no validation of scheme, host, or port. The attacker fully controls the destination and the response is returned to the caller, enabling data exfiltration from internal services.

- `POST /api/send-task` (line 143): Takes `agentUrl` from the request body and issues `client.post(f"{agent_url}/", ...)`. The full JSON response is returned to the caller.
- `POST /api/admin/add-skill` (line 234): Takes `agentUrl` from the request body and issues `client.post(f"{agent_url}/admin/skills", ...)`. The attacker also controls the JSON body sent to the target.
- Both endpoints have zero URL validation — no scheme check, no host allowlist, no private IP filtering.

### Exploit Scenario

An attacker sends `POST /api/send-task` with:

```json
{
  "agentUrl": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
  "taskType": "estimate"
}
```

The orchestrator makes an HTTP POST to the AWS metadata service. The JSON response (containing IAM credentials) is returned directly to the attacker. The same pattern works against any internal service reachable from the orchestrator (Redis, Elasticsearch, internal APIs).

### Recommendation

- Validate `agentUrl` against the known `AGENT_URLS` allowlist before making any outbound request. Reject any `agentUrl` not present in the `discovered_agents` dict or the `AGENT_URLS` list.
- Restrict the URL scheme to `http` and `https`.
- Block requests to private and link-local IP ranges (`169.254.x.x`, `10.x.x.x`, `172.16-31.x.x`, `127.x.x.x`).

---

## SSRF-2: Persistent SSRF via Unvalidated Agent URL Registration

**Severity:** High
**Category:** Server-Side Request Forgery (SSRF)
**Affected files:** `examples/orchestrator/app.py`

### Description

The `POST /api/agents` endpoint accepts any URL from the request body and appends it to the `AGENT_URLS` list with no validation. When `GET /api/discover` is subsequently called, the orchestrator makes HTTP GET requests to `{url}/.well-known/agent.json` for every registered URL. The attacker controls the full scheme, host, and port. The response is parsed as JSON and returned to the caller.

Unlike SSRF-1, this variant is **persistent** — the malicious URL remains in `AGENT_URLS` and is fetched on every subsequent discovery call by any user until the server restarts.

### Exploit Scenario

1. Attacker registers a malicious URL:
   ```json
   POST /api/agents
   {"url": "http://internal-elasticsearch:9200"}
   ```
2. When any user clicks "Discover Agents" in the dashboard, the orchestrator fetches `http://internal-elasticsearch:9200/.well-known/agent.json`.
3. If the internal service responds with JSON, the response is stored and returned, leaking internal service information.
4. The malicious URL persists across all future discovery calls.

### Recommendation

- Validate URLs submitted to `POST /api/agents`:
  - Restrict schemes to `http` and `https`.
  - Block private and link-local IP ranges (`169.254.x.x`, `10.x.x.x`, `172.16-31.x.x`, `127.x.x.x`).
  - Resolve the hostname and validate the resolved IP before storing the URL.
- Consider requiring a valid agent card response (with schema validation) before persisting the URL.
- Add authentication to the `/api/agents` endpoint to prevent unauthorized URL registration.
