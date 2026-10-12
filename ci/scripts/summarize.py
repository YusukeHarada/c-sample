#!/usr/bin/env python3
"""各ジョブの指標を 1 行にまとめ、推移 CSV に追記するスクリプト（ドラフト）。

使い方（CI の夜間スケジュールで実行）:
    python summarize.py --metrics-dir metrics --complexity complexity.csv \
        --cppcheck cppcheck.xml --history metrics_history.csv --fetch-previous

推移の残し方:
    GitLab CE には指標を蓄積する機能（Metrics Reports）がないため、
    前回の nightly_summary ジョブの成果物（metrics_history.csv）を API で取得し（GitLab の場合）、
    今回の 1 行を追記して再び成果物として保存する。
    取得に失敗した場合は新規に CSV を作成する（推移はそこから再スタート）。
    GitHub Actions では、ワークフロー側で前回の成果物を gh run download で取得して
    --history に渡す（--fetch-previous は使わない）。

前回分の取得に使う環境変数（GitLab が自動で設定）:
    CI_API_V4_URL, CI_PROJECT_ID, CI_DEFAULT_BRANCH, CI_JOB_TOKEN, CI_JOB_NAME
    社内 CA の証明書で検証に失敗する場合は REQUESTS_CA_BUNDLE 相当として
    SSL_CERT_FILE に CA ファイルを指定する。
"""
import argparse
import csv
import io
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def complexity_stats(path: Path, ccn_limit: int) -> dict:
    """lizard の --csv 出力を集計する（列: NLOC, CCN, token, PARAM, length, location, ...）。"""
    ccns = []
    nloc_total = 0
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2 or not row[0].strip().isdigit():
            continue   # ヘッダ行や空行を飛ばす
        nloc_total += int(row[0])
        ccns.append(int(row[1]))
    if not ccns:
        return {}
    return {
        "functions": len(ccns),
        "nloc": nloc_total,
        "ccn_max": max(ccns),
        "ccn_avg": round(sum(ccns) / len(ccns), 2),
        "ccn_over": sum(1 for c in ccns if c > ccn_limit),
    }


def cppcheck_stats(path: Path) -> dict:
    """cppcheck の XML（--xml-version=2）を重大度別・MISRA に分けて数える。"""
    if not path.exists():
        return {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    stats = {"cppcheck_total": 0, "cppcheck_error": 0, "cppcheck_warning": 0, "misra": 0}
    for err in root.iter("error"):
        err_id = err.get("id", "")
        if err_id in ("missingInclude", "missingIncludeSystem", "checkersReport", "toomanyconfigs"):
            continue   # 解析環境の情報で、コードの指摘ではないもの
        stats["cppcheck_total"] += 1
        if err_id.startswith("misra"):
            stats["misra"] += 1
        sev = err.get("severity", "")
        if sev == "error":
            stats["cppcheck_error"] += 1
        elif sev == "warning":
            stats["cppcheck_warning"] += 1
    return stats


def fetch_previous_history(job_name: str) -> str | None:
    api = os.environ.get("CI_API_V4_URL")
    project = os.environ.get("CI_PROJECT_ID")
    ref = os.environ.get("CI_DEFAULT_BRANCH", "main")
    token = os.environ.get("CI_JOB_TOKEN")
    if not (api and project and token):
        print("[INFO] GitLab の環境変数がないため、前回分の取得をスキップします。")
        return None
    url = (f"{api}/projects/{project}/jobs/artifacts/{urllib.parse.quote(ref, safe='')}"
           f"/raw/metrics_history.csv?job={urllib.parse.quote(job_name)}")
    req = urllib.request.Request(url, headers={"JOB-TOKEN": token})
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE"))
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as res:
            return res.read().decode("utf-8-sig")
    except Exception as e:   # 初回・期限切れ・権限不足など
        print(f"[INFO] 前回の推移 CSV を取得できませんでした（新規作成します）: {e}")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metrics-dir", type=Path, default=Path("metrics"))
    ap.add_argument("--complexity", type=Path, default=Path("complexity.csv"))
    ap.add_argument("--cppcheck", type=Path, default=Path("cppcheck.xml"))
    ap.add_argument("--ccn-limit", type=int, default=15)
    ap.add_argument("--history", type=Path, default=Path("metrics_history.csv"))
    ap.add_argument("--fetch-previous", action="store_true", help="前回の成果物を API で取得して追記する")
    args = ap.parse_args()

    row = {
        "date": datetime.now(JST).strftime("%Y-%m-%d %H:%M"),
        # GitLab CI / GitHub Actions のどちらでも識別子を残す
        "commit": os.environ.get("CI_COMMIT_SHORT_SHA") or os.environ.get("GITHUB_SHA", "")[:8],
        "pipeline": os.environ.get("CI_PIPELINE_ID") or os.environ.get("GITHUB_RUN_NUMBER", ""),
    }
    warnings = load_json(args.metrics_dir / "warnings.json")
    if warnings:
        row["compiler_warnings"] = warnings.get("warnings")
    for region, v in load_json(args.metrics_dir / "memory.json").items():
        row[f"{region}_used"] = v.get("used")
        row[f"{region}_pct"] = v.get("percent")
    row.update(complexity_stats(args.complexity, args.ccn_limit))
    row.update(cppcheck_stats(args.cppcheck))

    history: list[dict] = []
    if args.fetch_previous:
        prev = fetch_previous_history(os.environ.get("CI_JOB_NAME", "nightly_summary"))
        if prev:
            history = list(csv.DictReader(io.StringIO(prev)))
    elif args.history.exists():
        history = list(csv.DictReader(args.history.open(encoding="utf-8-sig")))
    history.append({k: ("" if v is None else v) for k, v in row.items()})

    # 指標が増減しても列がずれないよう、全行の列を合わせる（出現順を保持）
    fields: list[str] = []
    for r in history:
        for k in r:
            if k not in fields:
                fields.append(k)
    with args.history.open("w", newline="", encoding="utf-8-sig") as f:   # Excel で開けるよう BOM 付き
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(history)

    print(f"推移 CSV を更新しました: {args.history}（{len(history)} 行）")
    for k, v in row.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
