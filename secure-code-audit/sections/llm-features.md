# LLM / AI features (chatbots, RAG, agents, AI dashboards)

Classic SAST misses these; review manually wherever the app calls a model (OWASP Top 10 for LLM Applications, 2025 edition: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM10 Unbounded Consumption):
- **Prompt injection**: retrieved documents, user uploads, and third-party content fed to a model are DATA, not instructions — never let them override the system prompt's authority (delimit clearly, instruct the model to treat them as untrusted, strip/flag instruction-like content in RAG chunks).
- **Tool-call authorization**: every tool an LLM can invoke re-checks authn/authz server-side with the END USER's identity — the model must not be able to reach rows/actions the user can't. No raw-SQL or shell tools without strict scoping/allow-listing. Treat tool args like any untrusted input.
- **RAG tenancy**: retrieval queries are scoped by tenant/org id at the store level (filter in the vector/DB query, not post-hoc in the prompt); one tenant's documents must never surface in another's context.
- **Output handling**: model output rendered as text/sanitized markdown — never `dangerouslySetInnerHTML`/`v-html` on it, never `eval`, never auto-clicking links it generates (XSS/markdown-image exfiltration).
- **Secrets & PII**: no credentials or hidden business logic in system prompts (assume prompts leak); don't log full prompts/completions containing user PII; API keys server-side only, never shipped to the client.
- **Denial-of-wallet**: rate-limit + max-token-cap every model endpoint per user/org; cap agent loop iterations; meter and alert on spend.
