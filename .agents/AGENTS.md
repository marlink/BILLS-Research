# AGENTS.md — Advanced Developer Mode & Automation Rules

## 1. Permanent Pro Advanced Developer Mode
- Always operate in **Pro Advanced Developer Mode** for all tasks involving coding, API development, data engineering, and automation.
- Never ask the user to manually "switch to dev mode" or prompt for permission on standard, safe engineering operations.
- Maintain production-grade standards: high-performance code, clean modular architecture, and rich modern aesthetics.

## 2. Proactive API & Skill Activation
- Automatically inspect, load, and execute relevant skills from `.agents/skills/` (e.g., `b2b-lead-sync`, `b2b-partner-discovery`, `building-data-apps`, `managing-python-dependencies`) the moment a task matching their scope is requested.
- For all API integrations (KRS, CEIDG, VIES, REST, GraphQL, Google APIs), implement robust retry mechanisms, rate-limiting, user-agent headers, and strict schema validation.

## 3. Autonomous Execution & Verification
- Always execute and verify code after edits (e.g. running scripts, dry-runs, or linters) to confirm zero syntax errors or runtime crashes before concluding turns.
- Keep data pipelines, master CSV catalogs, and HTML dashboards automatically synchronized in real time.
- Avoid placeholders or incomplete implementations.

## 4. Token Efficiency & Agent Caching
- Enforce prompt caching and context optimization across all subagents and API interactions to minimize token overhead and accelerate response times.
