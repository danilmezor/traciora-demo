import uuid

import pytest

from seeder import __main__ as runner
from seeder import ids


def test_ids_are_pinned_to_their_inputs():
    """Every machine and every later build gives a person the same ids; another configuration gives others."""
    assert ids.uuid("person", "7", "en") == uuid.UUID("79e43e38-368d-5654-89e6-c7548e43c344")
    assert ids.number("person", "7", "en") == 1985565238
    assert ids.number("person", "7", "ru") == 383039130
    assert all(0 < ids.number("call", n, "en") < 2 ** 31 for n in range(1000))


def test_a_missing_step_is_absent_and_a_broken_one_raises(tmp_path, monkeypatch):
    (tmp_path / "seedstep_broken.py").write_text("import seedstep_nowhere\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(runner, "STEPS", {"gone": "seeder.nowhere.people", "broken": "seedstep_broken", "erp": "seeder.erp"})
    assert runner.find("gone") is None
    assert runner.find("erp").step
    with pytest.raises(ModuleNotFoundError, match="seedstep_nowhere"):
        runner.find("broken")
