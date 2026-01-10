from judicor.ai.roles import AgentRole
from judicor.session import history_store


def test_append_and_load_history(temp_history_store):
    history_store.append_entry(1, AgentRole.INVESTIGATOR, "content")
    entries = history_store.load_history(1)
    assert len(entries) == 1
    assert entries[0].role is AgentRole.INVESTIGATOR


def test_summary_roundtrip(temp_history_store):
    history_store.set_summary(1, "summary text")
    assert history_store.load_summary(1) == "summary text"
