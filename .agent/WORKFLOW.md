# Agent workflow v1 (2026-11-06)

The repo root owns routing; `.agent/context.md` holds project-specific pointers and checks.
Nested app AGENTS files add constraints. User instructions and current product decisions
take priority over generic routing. Old release history is evidence, not a current task.

## Routing and budget discipline
Primary: architecture, dependencies between apps, complex debugging, risky integration.
Workhorse: bounded edits with acceptance criteria. Flow-checker: independent no-edit
review when the flow warrants it, not a mandatory second model on every small edit.
One worker by default, three maximum, no recursive delegation. Assign each file one owner.
After two unsuccessful fixes, collect symptom, hypotheses, evidence and next discriminating
test for the primary. A role prompt is guidance, not a security sandbox or token hard limit.

Codex project defaults select Sol with medium effort and Luna workers with low effort;
the flow checker uses medium effort. Claude settings select Opus and each worker declares
Haiku explicitly. Keep architecture in the primary session. Model availability, project
trust, client version, explicit invocation and managed settings affect the effective model.
Start a new trusted session after installing. Inspect agent/session model information before
claiming routing is active; if unavailable, explain the fallback. No credentials are added.

Cheap models reduce per-token cost, not necessarily tokens. Control fanout, unnecessary
reads, repeated logs and speculative repair loops. Keep stable instructions compact and
task data separate. Preserve tool/provider prompt caching; do not pad prompts for cache hits.
For representative tasks record model, input/output/cached tokens when exposed, wall time,
retries and verified outcome. Compare equivalent tasks including primary and workers.
No percentage saving is promised before measurement. Avoid timed CEO/polling agents.

## Task contract and handoff
Assignment: goal; allowed paths; context pointers; interfaces/IDs that must not change;
checks and expected result; dependencies; stop conditions. Keep it short and explicit.
Result: files changed; test commands and outcomes; unresolved risks; next owner/action.
Use existing ADR/handoff locations identified in context. Do not add a competing history.

## Future apps and enforcement
`python3 tools/agent_workflow.py scaffold apps/example --kind web --name Example`
creates local guidance and a registry entry. Fill the generated context and replace its
UNCONFIGURED marker before CI can pass. Kinds: unity, web, dotnet, static, other.
`python3 tools/agent_workflow.py bootstrap /path/to/new-repo --kind unity --name Example`
copies the same self-contained toolkit into an empty target (refuses collisions).
Run from a checkout of any standardized repository. This does not create a GitHub repo.
Each independent repo must receive this bootstrap or be created from a standardized copy;
there is no GitHub account-level inheritance. Nested manifests are checked against the
registry, excluding vendor/build directories. For a new custom stack without a recognized
manifest, register it explicitly through scaffold. Static pages inherit their site's context.

CI runs the standard-library-only structural checker and its regression tests, without AI
API calls, secrets or Unity licenses. It checks routing/config consistency, local contexts,
required files and app registration. It cannot guarantee agent obedience, model access,
app correctness or enforce branch protection. Keep existing application CI intact.

## Release and product checks (when relevant)
Review SDK data collection and privacy declarations, permission-denial behavior, real
purchase/restore flows in test environments, store copy matching the shipped version,
safe areas/RTL/screen sizes, clean-install flows and crash recovery. Verify current store
requirements from official docs at release time. Automated metrics complement device
testing and human judgment. Respect each app's ad pacing and release/approval rules.

## Research incorporated
- OpenAI, custom instructions and discovery: https://developers.openai.com/codex/guides/agents-md
- OpenAI, local model routing and custom TOML agents: https://developers.openai.com/codex/subagents
- OpenAI, configuration schema: https://developers.openai.com/codex/config-schema.json
- Anthropic, custom Markdown agents and model selection: https://code.claude.com/docs/en/sub-agents
- Anthropic, context/model/fanout cost management: https://code.claude.com/docs/en/costs
- Apple release requirements: https://developer.apple.com/app-store/review/guidelines/
- Supplied Yagel Oshri post: durable plans/contracts, bounded roles, measurable QA and
  human game-feel review. Its five-day timeline and unmeasured savings are not guarantees.
