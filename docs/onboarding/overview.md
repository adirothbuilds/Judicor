# Judicor Project Overview

This brief is for new contributors to get productive quickly. It maps the codebase, key data models, environment variables, and shows how to run a local end-to-end flow with the control plane and HTTP client.

## High-Level Architecture

- CLI (Typer) -> Judicor client (factory-selected) -> AI reasoners + session/identity stores.
- Control plane (FastAPI) exposes incident/timeline endpoints secured by API key.
- Storage is local (files under `~/.judicor`) for incidents, timelines, summaries, sessions, identity.
- AI reasoners: dummy (static) and Gemini, selected per role.

### Core Modules

- `judicor.cli.app`: Typer commands (`init`, `list`, `attach`, `ask`, `status`, `resolve`, `trigger`, `context`). Client type via `JUDICOR_CLIENT_TYPE` (`dummy` default, `http` supported).
- `judicor.client.factory`: Chooses client implementation (dummy/local or HTTP/control-plane).
- `judicor.client.implementations.dummy`: Uses local persistent stores; role-aware reasoners (Analyzer on trigger, Investigator+Summarizer on ask, Resolver on resolve), logs timeline/history/summary, enforces state machine.
- `judicor.client.implementations.http`: Talks to control-plane API (`JUDICOR_API_URL`, `JUDICOR_API_KEY`), mirrors JudicorClient interface.
- `judicor.control_plane.app`: FastAPI app with API-key auth; endpoints for create/list/get incidents, append timeline, resolve, health; uses same local stores.
- `judicor.control_plane.run`: Entrypoint for running the control plane (`poetry run judicor-plane`).
- `judicor.ai.roles`: `AgentRole` enum (Analyzer, Investigator, Summarizer, Resolver).
- `judicor.ai.factory`: Creates role-aware reasoners based on provider env (`JUDICOR_AI_PROVIDER` dummy/gemini).
- `judicor.ai.implementations.dummy|gemini`: Reasoner implementations (Gemini uses `GOOGLE_API_KEY`).
- `judicor.ai.policy`: Confidence/validation policy.
- `judicor.domain`: Models (`Incident`, `IncidentState`), results, messages, state machine (`transition_incident_state`).
- `judicor.session`: Persistent stores for incidents, timeline, history/summary, session; `utils` centralizes secure writes and datetime parsing.
- `judicor.identity`: CLI init flow and storage under `~/.judicor/identity.json`.

### Key Data Models

- `Incident`: `id`, `title`, `state` (`IncidentState`), timestamps; `status` property mirrors state value.
- `IncidentState`: `created`, `active`, `investigating`, `resolved`, `archived` with legal transitions in `domain/state.py`.
- `Results`: `Result`, `AttachResult`, `AskResult`, `TriggerResult`, `StatusResult` (confidence/reasoning included for Ask).
- Timeline/History: stored per-incident JSON files under `~/.judicor/incidents/<id>/` for events, history entries, and rolling summary.

### Environment Variables

- Client selection: `JUDICOR_CLIENT_TYPE` (`dummy`, `http`).
- AI provider: `JUDICOR_AI_PROVIDER` (`dummy`, `gemini`).
- Gemini auth: `GOOGLE_API_KEY`.
- Control plane: `JUDICOR_API_URL` (default `http://localhost:8000`), `JUDICOR_API_KEY` (shared key).

### Running the Control Plane

In one terminal:

```bash
export JUDICOR_API_KEY=k
poetry run judicor-plane  # runs uvicorn on :8000
```

### Using the HTTP Client via CLI (second terminal)

```bash
export JUDICOR_API_KEY=k
export JUDICOR_API_URL=http://localhost:8000
export JUDICOR_CLIENT_TYPE=http

# optional: Gemini
# export GOOGLE_API_KEY=your_key
# export JUDICOR_AI_PROVIDER=gemini

poetry run judicor trigger
poetry run judicor list
poetry run judicor attach 1
poetry run judicor ask "What is the status?"
poetry run judicor resolve
poetry run judicor context
```

### Using the Dummy Client (local-only)

Unset `JUDICOR_CLIENT_TYPE` or set to `dummy` to use local stores and dummy/Gemini reasoners without the control plane.

### Testing

- `make test` runs pytest with coverage.
- `make lint` runs flake8.
- `make run-control` or `poetry run judicor-plane` to start the control plane manually for ad-hoc integration.

### File Locations

- Runtime data: `~/.judicor/identity.json`, `~/.judicor/session.json`, `~/.judicor/incidents/<id>/incident.json`, `timeline.json`, `history.json`, `summary.json`.

### Notes

- Control-plane AI calls are stubbed in the HTTP client ask path (timeline-only) and can be extended later to call server-side AI.
- API key auth is intentionally simple (shared key) to keep accountability; extend to per-identity keys if needed.
