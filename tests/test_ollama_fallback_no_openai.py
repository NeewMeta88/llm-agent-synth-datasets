import json
import sys
import types
from pathlib import Path

from dataset_generator.pipeline import PipelineConfig, run_pipeline
from dataset_generator.validate.validator import validate_out_dir


def test_ollama_fallback_when_openai_missing(tmp_path: Path, monkeypatch) -> None:
    dummy_openai = types.ModuleType("openai")
    if "openai" in sys.modules:
        monkeypatch.delitem(sys.modules, "openai", raising=False)
    monkeypatch.setitem(sys.modules, "openai", dummy_openai)

    input_path = Path("examples") / "example_input_raw_support_faq_and_tickets.md"
    out_dir = tmp_path / "out" / "support"

    config = PipelineConfig(
        input_path=str(input_path),
        out_dir=str(out_dir),
        seed=9,
        case="auto",
        n_use_cases=5,
        n_test_cases_per_uc=3,
        n_examples_per_tc=1,
        llm_provider="ollama",
        llm_model=None,
        ollama_base_url=None,
        llm_temperature=0.2,
    )
    run_pipeline(config)

    ok, errors, _ = validate_out_dir(out_dir)
    assert ok, errors

    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    llm = manifest.get("llm", {})
    assert llm.get("provider") == "none"
