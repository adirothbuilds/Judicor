from judicor.session import timeline_store


def test_append_and_load_timeline(temp_timeline_store):
    timeline_store.append_event(1, "created", "Incident created")
    timeline_store.append_event(1, "state_change", "Moved to active")

    events = timeline_store.load_timeline(1)
    assert len(events) == 2
    assert events[0].event_type == "created"
    assert events[1].message == "Moved to active"


def test_load_invalid_file_returns_empty(temp_timeline_store):
    path = temp_timeline_store.BASE_DIR / "1" / "timeline.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not-json")

    events = timeline_store.load_timeline(1)
    assert events == []


def test_append_creates_directories_and_sets_timestamp(temp_timeline_store):
    timeline_store.append_event(42, "note", "Created via test")

    events = timeline_store.load_timeline(42)
    assert len(events) == 1
    assert events[0].event_type == "note"
    assert events[0].timestamp.tzinfo is not None
