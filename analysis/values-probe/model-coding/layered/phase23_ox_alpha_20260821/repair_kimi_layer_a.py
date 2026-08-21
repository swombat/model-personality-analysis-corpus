#!/usr/bin/env python3
"""Repair Kimi Layer-A rows that exhausted the original 800-token budget."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import httpx


PHASE = Path(__file__).resolve().parent
LAYERED = PHASE.parent
RUNNER = LAYERED / "run_layer_a_code_coders.py"
IDS = {
    "P23_ox-alpha_G3_2",
    "P23_ox-alpha_G3_13",
    "P23_ox-alpha_G3_27",
}


def load_runner():
    spec = importlib.util.spec_from_file_location("phase23_layer_a_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    runner = load_runner()
    manifest = {
        row["layered_id"]: row
        for row in (
            json.loads(line)
            for line in (PHASE / "manifest_phase23.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    repaired = {}
    for layered_id in sorted(IDS):
        sample = manifest[layered_id]
        body = {
            "model": runner.CODERS["kimi-k2-6"],
            "messages": [
                {"role": "system", "content": runner.SYSTEM},
                {"role": "user", "content": runner.prompt(sample)},
            ],
            "temperature": 0,
            "max_tokens": 3000,
            "include_reasoning": False,
        }
        headers = {
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://danieltenner.com",
            "X-Title": "layer-a-code-protocol-repair",
        }
        for attempt in range(5):
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=180,
            )
            if response.status_code in (408, 409, 429) or response.status_code >= 500:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            raw = response.json()
            message = raw["choices"][0]["message"]
            text = (
                message.get("content")
                or message.get("reasoning")
                or message.get("reasoning_content")
                or ""
            )
            topics, clean = runner.parse(text, runner.WISH_CODES)
            if clean:
                repaired[layered_id] = {
                    "coder_key": "kimi-k2-6",
                    "coder_model": runner.CODERS["kimi-k2-6"],
                    "layered_id": layered_id,
                    "model": sample["model"],
                    "model_family": sample["model_family"],
                    "condition": sample["condition"],
                    "processing_chain": sample["processing_chain"],
                    "raw_text": text,
                    "topics": topics,
                    "parse_clean": True,
                    "value_topics": [],
                    "wish_topics": [{"topic_key": topic} for topic in topics],
                    "raw": raw,
                }
                print(layered_id, topics, flush=True)
                break
        else:
            raise RuntimeError(f"repair failed: {layered_id}")

    out = PHASE / "layer_a" / "kimi-k2-6.jsonl"
    rows = []
    for line in out.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows.append(repaired.get(row["layered_id"], row))
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    )
    failed = PHASE / "layer_a" / "kimi-k2-6.failed.jsonl"
    if failed.exists():
        failed.rename(PHASE / "layer_a" / "kimi-k2-6.failed.length-exhausted.jsonl")
    print(json.dumps({"repaired": len(repaired)}))


if __name__ == "__main__":
    main()
