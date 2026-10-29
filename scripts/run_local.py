"""Start and stop both local services as one foreground command."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    for port in (8010, 8011):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                raise SystemExit(
                    f"Port {port} is occupied. Stop the previous SpecLens process first."
                )
    runtimes = [ROOT / "environments/llm/.venv/bin/python", ROOT / ".venv/bin/python"]
    if not all(p.exists() for p in runtimes):
        raise SystemExit("Run uv sync --locked in both environments first; see README.")
    (ROOT / "logs").mkdir(exist_ok=True)
    children, logs = [], []
    try:
        commands = [
            ([str(runtimes[0]), str(ROOT / "scripts/llm_worker.py"), "serve"], 8011, "worker"),
            ([str(runtimes[1]), "-m", "speclens.cli", "serve"], 8010, "api"),
        ]
        for command, port, label in commands:
            log = (ROOT / f"logs/{label}.log").open("w")
            logs.append(log)
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                env={**os.environ, "HF_HUB_OFFLINE": "1", "PYTHONPATH": str(ROOT / "src")},
                start_new_session=True,
            )
            children.append(process)
            for attempt in range(30):
                if process.poll() is not None:
                    raise RuntimeError(f"{label} exited. Inspect logs/{label}.log")
                try:
                    response = httpx.get(
                        f"http://127.0.0.1:{port}/health", timeout=2, trust_env=False
                    )
                    response.raise_for_status()
                    break
                except httpx.HTTPError:
                    time.sleep(1)
            else:
                raise RuntimeError(f"{label} did not become ready within 30 seconds")
        print("SpecLens: http://127.0.0.1:8010", flush=True)
        print("Ctrl-C stops both local services. Logs are under logs/.", flush=True)
        while all(p.poll() is None for p in children):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping local services…", flush=True)
    finally:
        for process in reversed(children):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
        for process in children:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
