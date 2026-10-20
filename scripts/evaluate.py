"""Execute the Sprint 4 golden dataset against Groq and Gemini.

Examples:
    python scripts/evaluate.py
    python scripts/evaluate.py --resume results/sprint4/<run_id>/partial.json
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from src.evaluation.pipeline import run_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="Roda o golden dataset da Sprint 4 em Groq e Gemini.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/eval/golden_dataset.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/sprint4")
    parser.add_argument("--resume", type=Path, help="Retoma a partir do partial.json de uma execução.")
    parser.add_argument("--rejudge", action="store_true", help="Recalcula as notas guardadas sem repetir chamadas aos modelos avaliados; exige --resume.")
    parser.add_argument("--score-existing", action="store_true", help="Não repete chamadas que falharam; com --resume, também aplica auditorias determinísticas às respostas completas.")
    args = parser.parse_args()

    missing = [name for name in ("GROQ_API_KEY", "GOOGLE_API_KEY") if not os.getenv(name)]
    if missing:
        parser.error("Credenciais ausentes no ambiente/.env: " + ", ".join(missing))
    if args.rejudge and not args.resume:
        parser.error("--rejudge requer --resume com o partial.json de uma execução.")
    try:
        run_dir = run_evaluation(args.dataset.resolve(), args.output_dir.resolve(), args.resume.resolve() if args.resume else None, rejudge=args.rejudge, score_existing=args.score_existing)
    except Exception as exc:
        print(f"Falha na avaliação: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Resultados salvos em: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
