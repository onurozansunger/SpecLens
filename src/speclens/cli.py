from __future__ import annotations

import argparse
import json
import platform

from .common import ROOT, write_json


def main():
    parser = argparse.ArgumentParser(description="SpecLens local document baseline")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    commands.add_parser("fetch")
    commands.add_parser("extract")
    embed = commands.add_parser("embed")
    embed.add_argument("--device", choices=["cpu", "mps"], default="mps")
    embed.add_argument("--offline", action="store_true")
    search = commands.add_parser("search")
    search.add_argument("query")
    methods = ["bm25", "dense", "hybrid", "hybrid_expanded"]
    search.add_argument("--method", choices=methods, default="hybrid_expanded")
    search.add_argument("--document", action="append")
    search.add_argument("--limit", type=int, default=6)
    answer = commands.add_parser("answer")
    answer.add_argument("question")
    answer.add_argument("--document", action="append", required=True)
    answer.add_argument("--method", choices=methods, default="hybrid_expanded")
    answer.add_argument("--per-document", type=int, default=8)
    answer.add_argument("--output")
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=8010)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("kind", choices=["retrieval", "generation", "quality"])
    evaluate.add_argument("--method", choices=methods, default="hybrid_expanded")
    evaluate.add_argument("--limit", type=int, default=30)
    evaluate.add_argument("--per-document", type=int, default=8)
    evaluate.add_argument("--output")
    evaluate.add_argument("--tasks", default="data/evaluation/development.jsonl")
    evaluate.add_argument("--corpus-root", default=str(ROOT))
    evaluate.add_argument("--prompt-version", choices=["v1", "v2", "v3"], default="v3")
    evaluate.add_argument("--freeze")
    evaluate.add_argument("--replay")
    commands.add_parser("check-data")
    compare = commands.add_parser("compare-vin")
    compare.add_argument("--document", action="append", required=True)
    compare.add_argument("--target", required=True, help="Numeric target voltage")
    compare.add_argument("--unit", choices=["V", "mV", "kV"], default="V")
    compare.add_argument("--method", choices=methods, default="hybrid_expanded")
    compare.add_argument("--output")
    args = parser.parse_args()
    if args.command == "doctor":
        import torch

        result = {
            "python": platform.python_version(),
            "architecture": platform.machine(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "mps_built": torch.backends.mps.is_built(),
            "mps_available": torch.backends.mps.is_available(),
        }
        if result["mps_available"]:
            a = torch.arange(16, dtype=torch.float32, device="mps").reshape(4, 4)
            result["mps_matmul_sum"] = float((a @ a.T).sum().item())
            torch.mps.synchronize()
        write_json(ROOT / "reports/torch_doctor.json", result)
    elif args.command == "fetch":
        from .corpus import fetch_corpus

        result = fetch_corpus()
    elif args.command == "extract":
        from .corpus import extract_corpus

        result = extract_corpus()
    elif args.command == "embed":
        from .retrieval import build_embeddings

        result = build_embeddings(device=args.device, offline=args.offline)
    elif args.command == "search":
        from .retrieval import Retriever

        result = Retriever().search(args.query, args.method, args.limit, args.document)
    elif args.command == "answer":
        from pathlib import Path

        from .pipeline import Pipeline

        result = Pipeline().answer(args.question, args.document, args.method, args.per_document)
        if args.output:
            write_json(Path(args.output), result)
    elif args.command == "serve":
        import uvicorn

        uvicorn.run("speclens.api:app", host="127.0.0.1", port=args.port, workers=1)
        return
    elif args.command == "evaluate":
        from pathlib import Path

        from .evaluation import evaluate_generation, evaluate_retrieval

        output = Path(args.output) if args.output else None
        if args.kind == "quality":
            from .benchmark import evaluate_quality

            if output is None:
                parser.error("Quality evaluation requires --output to preserve run history")
            result = evaluate_quality(
                Path(args.tasks),
                output,
                Path(args.corpus_root),
                args.prompt_version,
                Path(args.freeze) if args.freeze else None,
                Path(args.replay).resolve() if args.replay else None,
            )
        elif args.kind == "retrieval":
            result = evaluate_retrieval(methods=methods, output=output)
        else:
            result = evaluate_generation(args.method, args.limit, output, args.per_document)
    elif args.command == "check-data":
        from .dataset import check_pilot

        result = check_pilot()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["valid"]:
            raise SystemExit(1)
        return
    elif args.command == "compare-vin":
        from decimal import Decimal
        from pathlib import Path

        from .numeric import compare_vin_findings
        from .pipeline import Pipeline

        target = Decimal(args.target)
        if not target.is_finite():
            parser.error("Target must be finite")
        result = Pipeline().answer(
            "What is the recommended VIN input voltage range? Include VIN in the exact quote.",
            args.document,
            args.method,
        )
        result["comparison"] = compare_vin_findings(result, target, args.unit)
        if args.output:
            write_json(Path(args.output), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
