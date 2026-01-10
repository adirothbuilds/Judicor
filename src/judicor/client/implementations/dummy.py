from typing import Optional, List

from judicor.ai.interface import AIReasoner
from judicor.ai.factory import create_ai_reasoner
from judicor.ai.policy import ReasoningPolicy
from judicor.ai.roles import AgentRole
from judicor.client.interface import JudicorClient
from judicor.session import timeline_store
from judicor.session import incident_store
from judicor.session import history_store
from judicor.session.store import (
    load_session,
    save_attached_incident,
    clear_session,
)
from judicor.domain.models import Incident, IncidentState
from judicor.domain.state import transition_incident_state
from judicor.domain.messages import NO_INCIDENT_ATTACHED
from judicor.domain.results import (
    Result,
    AttachResult,
    AskResult,
    TriggerResult,
    StatusResult,
)


class DummyJudicorClient(JudicorClient):
    """
    Dummy implementation of the JudicorClient interface.
    Used for local testing and development.
    """

    def __init__(
        self,
        reasoner: Optional[AIReasoner] = None,
        policy: Optional[ReasoningPolicy] = None,
    ) -> None:
        self.reasoners = self._init_reasoners(reasoner)
        self.policy = policy or ReasoningPolicy()

        # In-memory incidents store (dummy backend)
        stored = incident_store.list_incidents()
        if stored:
            self.incidents = {inc.id: inc for inc in stored}
        else:
            self.incidents = {}
            self._seed_incidents()

        # Restore session if exists
        self.current_incident: Optional[Incident] = None
        session_info = load_session()
        if session_info is not None:
            attached_id, _ = session_info
            self.current_incident = self.incidents.get(attached_id)

    def list_incidents(self) -> List[Incident]:
        """List all incidents."""
        incidents = incident_store.list_incidents()
        self.incidents = {inc.id: inc for inc in incidents}
        return incidents

    def attach_incident(self, incident_id: int) -> AttachResult:
        """Attach to an active incident session by ID."""
        incident = incident_store.load_incident(incident_id)
        if not incident:
            return AttachResult(success=False, message="Incident not found")

        self.current_incident = incident
        self.incidents[incident_id] = incident
        save_attached_incident(incident_id)
        timeline_store.append_event(
            incident_id, "attached", f"Attached to incident {incident_id}"
        )

        if history_store.load_summary(incident_id) is None:
            history_store.set_summary(
                incident_id, f"Initial context for incident {incident_id}"
            )

        return AttachResult(success=True, incident_id=incident_id)

    def detach_incident(self) -> Result:
        """Detach from the currently attached incident session."""
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        incident_id = self.current_incident.id
        self.current_incident = None
        clear_session()

        timeline_store.append_event(
            incident_id,
            "detached",
            f"Detached from incident {incident_id}",
        )

        return Result(success=True, message="Detached successfully")

    def ask_ai(self, question: str) -> AskResult:
        """Ask a question to the AI assistant about the attached incident."""
        if self.current_incident is None:
            return AskResult(success=False, message=NO_INCIDENT_ATTACHED)

        if self.current_incident.state == IncidentState.ACTIVE:
            try:
                transition_incident_state(
                    self.current_incident, IncidentState.INVESTIGATING
                )
                self._persist_incident(self.current_incident)
                timeline_store.append_event(
                    self.current_incident.id,
                    "state_change",
                    "Incident moved to investigating",
                )
            except ValueError:
                pass

        investigator = self.reasoners[AgentRole.INVESTIGATOR]
        raw_result = investigator.ask(self.current_incident, question)
        timeline_store.append_event(
            self.current_incident.id,
            "ask",
            f"Asked AI: {question}",
        )

        evaluated = self.policy.evaluate(raw_result)
        history_store.append_entry(
            self.current_incident.id,
            AgentRole.INVESTIGATOR,
            evaluated.answer or evaluated.message or "",
        )

        # Run summarizer to keep rolling summary small for future asks
        summarizer = self.reasoners[AgentRole.SUMMARIZER]
        context = history_store.load_summary(self.current_incident.id) or ""
        summary_prompt = (
            f"Update summary with latest answer: {evaluated.answer}\n"
            f"Previous summary: {context}"
        )
        summary_result = summarizer.ask(
            self.current_incident,
            summary_prompt,
        )
        if summary_result.success and summary_result.answer:
            history_store.set_summary(
                self.current_incident.id, summary_result.answer
            )
            timeline_store.append_event(
                self.current_incident.id,
                "summary",
                "Incident summary updated",
            )

        return evaluated

    def status_incident(self) -> StatusResult:
        """Check the status of the current incident session."""
        if self.current_incident is None:
            return StatusResult(
                success=False,
                state="none",
                summary=NO_INCIDENT_ATTACHED,
            )

        return StatusResult(
            success=True,
            state=self.current_incident.status,
            summary=(
                f"{self.current_incident.title} is "
                f"{self.current_incident.status}"
            ),
        )

    def resolve_incident(self) -> Result:
        """Resolve the currently attached incident and close the session."""
        if self.current_incident is None:
            return Result(success=False, message=NO_INCIDENT_ATTACHED)

        incident_id = self.current_incident.id
        try:
            transition_incident_state(
                self.current_incident, IncidentState.RESOLVED
            )
            self._persist_incident(self.current_incident)
            resolver = self.reasoners[AgentRole.RESOLVER]
            context = history_store.load_summary(incident_id) or ""
            resolution_result = resolver.ask(
                self.current_incident,
                (
                    "Provide closure and root cause. "
                    f"Summary: {context}"
                ),
            )
            if resolution_result.success and resolution_result.answer:
                history_store.append_entry(
                    incident_id,
                    AgentRole.RESOLVER,
                    resolution_result.answer,
                )
                history_store.set_summary(
                    incident_id, resolution_result.answer
                )
            timeline_store.append_event(
                incident_id,
                "state_change",
                "Incident resolved",
            )
        except ValueError as exc:
            return Result(success=False, message=str(exc))

        self.current_incident = None
        clear_session()

        return Result(
            success=True,
            message=f"Incident {incident_id} resolved successfully",
        )

    def trigger(self) -> TriggerResult:
        """Trigger creation of a new incident session."""
        incident = incident_store.create_incident(
            title=f"Dummy Incident {len(self.incidents) + 1}",
            initial_state=IncidentState.CREATED,
        )

        self._persist_incident(incident)

        timeline_store.append_event(
            incident.id,
            "created",
            f"Incident {incident.id} initialized in state created",
        )

        try:
            transition_incident_state(incident, IncidentState.ACTIVE)
            self._persist_incident(incident)
            timeline_store.append_event(
                incident.id,
                "state_change",
                "Incident moved to active",
            )
            analyzer = self.reasoners[AgentRole.ANALYZER]
            analysis = analyzer.ask(
                incident,
                f"Analyze newly created incident {incident.title}",
            )
            if analysis.success and analysis.answer:
                history_store.append_entry(
                    incident.id, AgentRole.ANALYZER, analysis.answer
                )
                history_store.set_summary(
                    incident.id, analysis.answer
                )
                timeline_store.append_event(
                    incident.id,
                    "analysis",
                    "Initial analysis generated",
                )
        except ValueError:
            pass

        return TriggerResult(success=True, incident_id=incident.id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _persist_incident(self, incident: Incident) -> None:
        self.incidents[incident.id] = incident
        incident_store.save_incident(incident)

    def _init_reasoners(
        self, provided: Optional[AIReasoner]
    ) -> dict[AgentRole, AIReasoner]:
        mapping: dict[AgentRole, AIReasoner] = {}
        for role in AgentRole:
            if provided is not None:
                mapping[role] = provided
            else:
                mapping[role] = create_ai_reasoner(role)
        return mapping

    def _seed_incidents(self) -> None:
        seeds = [
            (
                "Dummy Incident 1",
                IncidentState.ACTIVE,
            ),
            (
                "Dummy Incident 2",
                IncidentState.RESOLVED,
            ),
        ]

        for title, state in seeds:
            incident = incident_store.create_incident(title, state)
            self.incidents[incident.id] = incident
            timeline_store.append_event(
                incident.id,
                "created",
                (
                    "Incident "
                    f"{incident.id} initialized in state "
                    f"{incident.state.value}"
                ),
            )
