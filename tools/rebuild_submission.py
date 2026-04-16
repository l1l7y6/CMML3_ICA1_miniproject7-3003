from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the submission-ready figures, tables, and Word documents."
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Optional path to the raw 'oxydata dap cells.xlsx' spreadsheet. If omitted, the committed CSV is reused.",
    )
    return parser.parse_args()


def run_step(script_name: str, extra_args: list[str] | None = None) -> None:
    command = [sys.executable, str(TOOLS_DIR / script_name)]
    if extra_args:
        command.extend(extra_args)
    print("running", " ".join(command))
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> None:
    args = parse_args()

    if args.source is not None:
        run_step("prepare_selected_dap_data.py", ["--source", str(args.source)])
    elif os.environ.get("CMML3_ICA1_SOURCE_XLSX"):
        run_step("prepare_selected_dap_data.py")

    run_step("generate_ica1_results.py")
    run_step("build_word_docs.py")
    print("submission rebuild complete")


if __name__ == "__main__":
    main()
