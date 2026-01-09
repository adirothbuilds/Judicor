import typer

from judicor.identity import init_flow


def test_generate_fingerprint_stable():
    fp1 = init_flow._generate_fingerprint("host", "user")
    fp2 = init_flow._generate_fingerprint("host", "user")
    assert fp1 == fp2
    assert len(fp1) == 12


def test_run_init_saves_identity(monkeypatch):
    prompts = iter(["Alice", "alice@example.com", "Acme"])
    monkeypatch.setattr(typer, "prompt", lambda *a, **k: next(prompts))
    monkeypatch.setattr(typer, "echo", lambda *a, **k: None)
    monkeypatch.setattr(init_flow, "load_identity", lambda: None)
    monkeypatch.setattr(init_flow.socket, "gethostname", lambda: "host")
    monkeypatch.setattr(init_flow.getpass, "getuser", lambda: "user")

    captured = {}

    def _save(identity):
        captured["identity"] = identity

    monkeypatch.setattr(init_flow, "save_identity", _save)

    init_flow.run_init()

    identity = captured["identity"]
    assert identity.name == "Alice"
    assert identity.email == "alice@example.com"
    assert identity.org == "Acme"
    assert identity.hostname == "host"
    assert identity.os_user == "user"
    assert identity.fingerprint == init_flow._generate_fingerprint(
        "host", "user"
    )
