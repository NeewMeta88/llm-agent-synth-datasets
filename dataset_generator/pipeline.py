from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import typer

from dataset_generator import __version__
from dataset_generator.core.ids import IdFactory
from dataset_generator.core.markdown import MarkdownDocument
from dataset_generator.core.models import Evidence, Policy, RunManifest, UseCase
from dataset_generator.core.text_sanitize import sanitize_markdown_text
from dataset_generator.extract.heuristics import _policy_type_for_text
from dataset_generator.extract.case_classifier import detect_case
from dataset_generator.extract.drafts import extract_drafts
from dataset_generator.extract.drafts_to_models import drafts_to_policies, drafts_to_use_cases
from dataset_generator.extract.heuristics import extract_policies, extract_use_cases
from dataset_generator.llm.factory import get_llm_client
from dataset_generator.generate.dataset import generate_examples
from dataset_generator.generate.test_cases import generate_test_cases
from dataset_generator.io.writers import (
    write_dataset,
    write_policies,
    write_run_manifest,
    write_test_cases,
    write_use_cases,
)

CaseType = Literal["support_bot", "operator_quality", "auto"]


@dataclass(frozen=True)
class PipelineConfig:
    input_path: str
    out_dir: str
    seed: int
    case: CaseType
    n_use_cases: int
    n_test_cases_per_uc: int
    n_examples_per_tc: int
    llm_provider: str
    llm_model: str | None
    ollama_base_url: str | None
    llm_temperature: float


def _pad_use_cases(doc: MarkdownDocument, items: list[UseCase], target: int) -> list[UseCase]:
    if len(items) >= target:
        return items

    factory = IdFactory("uc_")
    existing_ids = {uc.id for uc in items}
    factory._seen.update(existing_ids)
    factory._counts.update({eid: 1 for eid in existing_ids})
    padded = list(items)

    non_empty_lines = [
        (idx, line) for idx, line in enumerate(doc.lines, start=1) if line.strip()
    ]
    if not non_empty_lines:
        non_empty_lines = [(1, "")]

    i = 0
    while len(padded) < target:
        line_idx, line = non_empty_lines[i % len(non_empty_lines)]
        quote = doc.quote(line_idx, line_idx)
        name = sanitize_markdown_text(line.strip()) or f"Use Case {len(padded) + 1}"
        uc_id = factory.new(name)
        if uc_id in existing_ids:
            i += 1
            continue
        description = sanitize_markdown_text(quote)
        padded.append(
            UseCase(
                id=uc_id,
                case="",
                name=name,
                description=description,
                evidence=[
                    Evidence(
                        input_file=Path(doc.path).name,
                        line_start=line_idx,
                        line_end=line_idx,
                        quote=quote,
                    )
                ],
            )
        )
        existing_ids.add(uc_id)
        i += 1

    return padded


def _pad_policies(doc: MarkdownDocument, items: list[Policy], target: int) -> list[Policy]:
    if len(items) >= target:
        return items

    factory = IdFactory("pol_")
    existing_ids = {p.id for p in items}
    factory._seen.update(existing_ids)
    factory._counts.update({eid: 1 for eid in existing_ids})
    padded = list(items)

    non_empty_lines = [
        (idx, line) for idx, line in enumerate(doc.lines, start=1) if line.strip()
    ]
    if not non_empty_lines:
        non_empty_lines = [(1, "")]

    i = 0
    while len(padded) < target:
        line_idx, line = non_empty_lines[i % len(non_empty_lines)]
        quote = doc.quote(line_idx, line_idx)
        statement = sanitize_markdown_text(line.strip()) or f"Policy {len(padded) + 1}"
        pol_id = factory.new(statement)
        if pol_id in existing_ids:
            i += 1
            continue
        padded.append(
            Policy(
                id=pol_id,
                case="",
                type=_policy_type_for_text(statement),
                statement=statement,
                evidence=[
                    Evidence(
                        input_file=Path(doc.path).name,
                        line_start=line_idx,
                        line_end=line_idx,
                        quote=quote,
                    )
                ],
            )
        )
        existing_ids.add(pol_id)
        i += 1

    return padded


def run_pipeline(config: PipelineConfig) -> Path:
    doc = MarkdownDocument.read(config.input_path)
    detected_case = detect_case(doc.lines, case_override=config.case)

    target_use_cases = max(config.n_use_cases, 5)
    target_policies = max(config.n_use_cases, 5)

    use_cases: list[UseCase] = []
    policies: list[Policy] = []
    llm_used = False
    llm_provider_used = "none"
    llm_fallback_reason: str | None = None
    llm_client = None
    if config.llm_provider != "none":
        try:
            llm_client = get_llm_client(
                config.llm_provider,
                model=config.llm_model,
                base_url=config.ollama_base_url,
                temperature=config.llm_temperature,
            )
            uc_drafts, pol_drafts = extract_drafts(
                doc, llm_client, detected_case, config.seed, temperature=config.llm_temperature
            )
            if uc_drafts:
                use_cases = drafts_to_use_cases(uc_drafts, doc, detected_case)
            if pol_drafts:
                policies = drafts_to_policies(pol_drafts, doc, detected_case)
            llm_used = True
            llm_provider_used = config.llm_provider
        except Exception as exc:
            typer.echo(
                f"WARNING: LLM unavailable, fallback to heuristics. Reason: {exc}"
            )
            llm_used = False
            llm_provider_used = "none"
            llm_fallback_reason = str(exc)[:200]

    if not use_cases:
        use_cases = extract_use_cases(doc, target_use_cases)
    if not policies:
        policies = extract_policies(doc, target_policies)

    use_cases = _pad_use_cases(doc, use_cases, target_use_cases)
    policies = _pad_policies(doc, policies, target_policies)

    use_cases = [uc.model_copy(update={"case": detected_case}) for uc in use_cases]
    policies = [pol.model_copy(update={"case": detected_case}) for pol in policies]

    test_cases = generate_test_cases(
        use_cases=use_cases,
        policies=policies,
        n_per_uc=config.n_test_cases_per_uc,
        seed=config.seed,
    )
    test_cases = [
        tc.model_copy(update={"case": detected_case}) for tc in test_cases
    ]

    examples = generate_examples(
        case=detected_case,
        test_cases=test_cases,
        use_cases=use_cases,
        policies=policies,
        n_per_tc=config.n_examples_per_tc,
        seed=config.seed,
        input_path=config.input_path,
        llm_client=llm_client if llm_used else None,
        llm_temperature=config.llm_temperature,
    )

    out_dir = Path(config.out_dir)
    write_use_cases(out_dir, use_cases)
    write_policies(out_dir, policies)
    write_test_cases(out_dir, test_cases)
    write_dataset(out_dir, examples)

    llm_info = {
        "provider": llm_provider_used,
        "model": getattr(llm_client, "model", None) if llm_client else None,
        "temperature": config.llm_temperature,
    }

    manifest = RunManifest(
        seed=config.seed,
        timestamp=datetime.now(timezone.utc).isoformat(),
        generator_version=__version__,
        llm=llm_info,
        input_path=config.input_path,
        out_path=str(out_dir),
    )
    write_run_manifest(out_dir, manifest)

    return out_dir
