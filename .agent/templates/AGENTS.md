# {{name}}

<!-- aviisr-agent-workflow:v1 -->
## Agent execution standard
- The primary reasoning agent owns architecture, planning, shared contracts, ambiguous bugs,
  security/privacy, monetization, persistence, and final integration. Use a short plan only
  when the work has dependencies or meaningful risk.
- Delegate bounded boilerplate, focused unit tests, lint fixes and behavior-preserving local
  refactors to `workhorse`; use `flow-checker` for independent scenario/edge-case review.
  Spawn only when the saved work exceeds the handoff overhead. Do trivial/dependent work
  directly. Prefer one worker; at most three at once, each owning disjoint files.
- Codex workers use gpt-6-luna; Claude workers use haiku. Primary: gpt-6.1-sol / opus.
  Workers do not delegate. Escalate ambiguous requirements, shared-contract changes,
  security/payments/save migrations, or two unsuccessful attempts to the primary.
  If a configured model is unavailable, report it and use an available model explicitly;
  do not silently claim cheap routing. Runtime/user settings can override project defaults.
- Each assignment includes goal, exact write scope, relevant context paths, invariants,
  acceptance checks, and stop conditions. Use fresh worker context where supported, not
  the full chat. Worker returns changed files, checks/results, uncertainties and next step
  in at most 250 words; keep long logs in artifacts. Never edit another worker's files.
- Read `.agent/context.md` and the affected app's local AGENTS.md; then search with rg and
  read only relevant code and current decisions. Do not preload archives, assets, generated
  files, vendor SDKs, entire logs or whole repository listings. Persist important decisions
  in existing decision/handoff documents; do not duplicate them into every prompt.
- Run deterministic tools before asking a model to diagnose formatting or test failures.
  Verify changed behavior with focused tests; broaden only for shared changes or failures.
  Configuration/docs-only work runs `python3 tools/agent_workflow.py check`; this does not
  prove app compilation or gameplay. Existing release/runtime test requirements remain.
- For user flows map states, transitions, cancellation, offline/denied permissions and
  recovery. Use executable checks and metrics for behavior, screenshots for layout, and
  human review for game feel. Preserve identifiers, schemas and product constraints.
- Before finalizing, inspect the combined diff and evidence. Distinguish passed, failed,
  skipped and not-run checks. Record a concise handoff and any real usage measurements;
  never invent token savings or equate lower model price with fewer tokens.
- Future apps: run `python3 tools/agent_workflow.py scaffold PATH --kind KIND --name NAME`.
  This registers the app and creates local context with inherited rules. New independent
  repositories: use `bootstrap TARGET --kind KIND --name NAME` from this toolkit.
  GitHub accounts do not automatically propagate these files to new repositories.
<!-- /aviisr-agent-workflow:v1 -->
