# Judicor

Judicor is an AI-driven incident reasoning engine that layers human judgment on top of existing observability stacks.
It is CLI-first, human-in-the-loop, and uses Gemini for structured reasoning while keeping uncertainty explicit.

## Concept

- Session-based incident lifecycle with explicit confidence and memory.
- Event-driven reasoning: think only when triggered by a question, alert, or material change.
- Pluggable integrations for observability, ticketing, and storage without touching the core engine.

## Runtime Model

- **Control Plane (always on):** lightweight API to create/manage sessions and receive triggers.
- **Reasoning Engine (on demand):** ephemeral process that fetches data, reasons with Gemini, updates session state, then terminates.
- Closure flow standardizes summaries and pushes resolved sessions to external systems.

## CLI-First Interface

```bash
judicor trigger ...
judicor status
judicor ask "Why is alert X secondary?"
judicor resolve
```

Chat or web adapters remain thin layers over the CLI.

## Project Layout

- `src/judicor/`: Python package (Poetry) for the core engine, control plane, integrations, and CLI adapters.
- `docs/Judicor–Initial_Design&Concept_Document.md`: full design and flow details.
- `assets/` and `docker/`: branding assets and containerization scaffolding.

## Development

- Requires Python 3.11+ and Poetry.
- Install dependencies: `poetry install`
- Run CLI commands via `poetry run judicor ...`

For reasoning principles, architecture diagrams, and future roadmap, see the initial design document in `docs/`.
