from __future__ import annotations

import importlib.util
import sys
from datetime import timedelta
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "reconcile-72h.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("reconcile_72h_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_prompt(module, text: str, classification: str = "META"):
    dt = module.WINDOW_START + timedelta(hours=1)
    prompt = module.Prompt(
        timestamp=dt.isoformat(timespec="seconds"),
        dt=dt,
        workspace="workspace-root",
        session_id="session",
        text=text,
        normalized_text=module.normalize_text(text),
        text_hash=module.prompt_hash(module.normalize_text(text)),
    )
    prompt.classification = classification
    prompt.summary = module.summarize(prompt.text)
    return prompt


def make_commit(module, hours_after: int, message: str):
    dt = module.WINDOW_START + timedelta(hours=hours_after)
    return module.Commit(
        hash=f"deadbeef{hours_after}",
        timestamp=dt.isoformat(timespec="seconds"),
        dt=dt,
        message=message,
        workspace="orchestration-start-here",
        message_lower=message.lower(),
    )


def test_noise_patterns_filter_exact_steering_tokens():
    module = load_module()

    assert module.is_noise("proceed")
    assert module.is_noise("continue")
    assert module.is_noise("yes")
    assert module.is_noise("❯ next")
    assert module.is_noise("[Image attachment]")


def test_steering_requires_stronger_signal_than_word_yes():
    module = load_module()

    assert module.is_steering("proceed with all, logic dictates order")
    assert module.is_steering("close--orchestration-event--intake")
    assert not module.is_steering("yes and we need to all build out all directories")

    prompt = make_prompt(module, "yes and we need to all build out all directories", "META")
    assert module.classify(prompt) == "BUILD"


def test_redact_text_masks_grouped_app_passwords():
    module = load_module()
    fake_app_password = "nvyr rosr " + "yeoz lwrw"  # allow-secret

    redacted = module.redact_text(
        f"gmail app name and password: job-search\n{fake_app_password}"  # allow-secret
    )

    assert fake_app_password not in redacted
    assert "[REDACTED_APP_PASSWORD]" in redacted


def test_deduplicate_prompts_collapses_repetitions():
    module = load_module()

    first = make_prompt(module, "Provide an overview of all that was")
    second = make_prompt(module, "Provide   an overview of all that was")
    third = make_prompt(module, "Provide an overview of all that was")

    deduped, duplicate_count = module.deduplicate_prompts([first, second, third])

    assert duplicate_count == 2
    assert len(deduped) == 1
    assert deduped[0].repetitions == 3


def test_match_outcomes_marks_absorbed_conceptual_intake():
    module = load_module()

    prompt = make_prompt(
        module,
        "Provide an overview of all that was and all that is and all that needs to be based on this entire session's context.",
        "RESEARCH",
    )
    commits = [
        make_commit(module, 2, "docs: persist session close audit plan"),
        make_commit(module, 3, "feat: operator prompts compilation"),
    ]

    module.match_outcomes([prompt], commits)

    assert prompt.outcome == "ABSORBED"
    assert "commits landed within 8h" in prompt.evidence


def test_match_outcomes_marks_specific_untraced_build_as_unresolved():
    module = load_module()

    prompt = make_prompt(
        module,
        "Route USPS junk email into the right folder and check the last two weeks for similar clutter.",
        "BUILD",
    )
    commits = [make_commit(module, 10, "docs: unrelated constitution update")]

    module.match_outcomes([prompt], commits)

    assert prompt.outcome == "UNRESOLVED"
