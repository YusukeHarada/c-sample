#!/usr/bin/env python3
"""解析結果を GitHub の注釈（PR の差分上に表示）とジョブサマリに変換するスクリプト。

GitLab の Code Quality / テストレポートに相当する見せ方を、サードパーティの Action を使わずに実現する。

使い方:
    python annotate.py cppcheck cppcheck.xml --fail-on non-misra
    python annotate.py lizard complexity.csv --ccn 10 --length 60 --args 5
    python annotate.py junit out/gtest-report.xml build/artifacts/gcov/junit_tests_report.xml

出力:
    - 標準出力に ::warning / ::error 形式のワークフローコマンド → PR の該当行に注釈が付く
    - 環境変数 GITHUB_STEP_SUMMARY があれば、Markdown の表をジョブサマリに追記する
    （GitHub の仕様で、注釈は 1 ステップあたり種類ごとに最大 10 件まで表示される）
"""
import argparse
import csv
import io
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

IGNORED_CPPCHECK_IDS = {"missingInclude", "missingIncludeSystem", "checkersReport",
                        "toomanyconfigs", "unmatchedSuppression"}


def esc(text: str) -> str:
    """ワークフローコマンドで特別な意味を持つ文字をエスケープする。"""
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def annotate(level: str, file: str, line, title: str, msg: str) -> None:
    loc = f"file={file},line={line}," if file else ""
    print(f"::{level} {loc}title={esc(title)}::{esc(msg)}")


def write_summary(md: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(md + "\n")
    else:
        print(md)


def cmd_cppcheck(args) -> int:
    root = ET.parse(args.xml).getroot()
    rows, counter = [], Counter()
    for err in root.iter("error"):
        err_id = err.get("id", "")
        if err_id in IGNORED_CPPCHECK_IDS:
            continue
        loc = err.find("location")
        file = loc.get("file", "") if loc is not None else ""
        line = loc.get("line", "1") if loc is not None else "1"
        sev = err.get("severity", "")
        is_misra = err_id.startswith("misra")
        category = "MISRA" if is_misra else sev
        counter[category] += 1
        msg = err.get("msg", "")
        if is_misra and "rule-texts" in msg:
            # ルール本文は MISRA 規格書（有償）にあるため、ルール番号だけを示す
            rule = err_id.replace("misra-c2012-", "")
            msg = f"MISRA C:2012 Rule {rule} 違反の可能性（ルール本文は規格書を参照）"
        level = "error" if sev == "error" else ("notice" if is_misra else "warning")
        annotate(level, file, line, f"cppcheck {err_id}", msg)
        rows.append((category, err_id, f"{file}:{line}", msg))

    md = ["### 静的解析（Cppcheck）", ""]
    if rows:
        md += ["| 区分 | ルール | 場所 | 内容 |", "|:--|:--|:--|:--|"]
        md += [f"| {c} | `{i}` | {loc} | {m} |" for c, i, loc, m in rows]
        md += ["", "件数: " + "、".join(f"{k} {v}" for k, v in sorted(counter.items()))]
    else:
        md.append("指摘はありません。")
    write_summary("\n".join(md))

    non_misra = sum(v for k, v in counter.items() if k != "MISRA")
    if args.fail_on == "any" and rows:
        return 1
    if args.fail_on == "non-misra" and non_misra:
        print(f"MISRA 以外の指摘が {non_misra} 件あります。")
        return 1
    return 0


def cmd_lizard(args) -> int:
    text = Path(args.csv).read_text(encoding="utf-8-sig", errors="replace")
    over = []
    total = 0
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 10 or not row[0].strip().isdigit():
            continue
        total += 1
        nloc, ccn, params, length = int(row[0]), int(row[1]), int(row[3]), int(row[4])
        file, func, start = row[6], row[7], row[9]
        reasons = []
        if ccn > args.ccn:
            reasons.append(f"複雑度 {ccn} > {args.ccn}")
        if length > args.length:
            reasons.append(f"行数 {length} > {args.length}")
        if params > args.args:
            reasons.append(f"引数 {params} > {args.args}")
        if reasons:
            annotate("warning", file, start, f"lizard {func}", "、".join(reasons))
            over.append((func, f"{file}:{start}", ccn, nloc, params))

    md = ["### 関数の複雑度（lizard）", "",
          f"対象 {total} 関数のうち、しきい値（複雑度 {args.ccn}・行数 {args.length}・引数 {args.args}）超過は {len(over)} 関数です。"]
    if over:
        md += ["", "| 関数 | 場所 | 複雑度 | 行数 | 引数 |", "|:--|:--|--:|--:|--:|"]
        md += [f"| `{f}` | {l} | {c} | {n} | {p} |" for f, l, c, n, p in over]
    write_summary("\n".join(md))
    return 1 if over else 0


def cmd_junit(args) -> int:
    md = ["### 単体テスト結果", "", "| レポート | テスト数 | 失敗 | エラー | スキップ |", "|:--|--:|--:|--:|--:|"]
    failed_total = 0
    failures = []
    for path in args.xml:
        p = Path(path)
        if not p.exists():
            md.append(f"| {p.name} | - | - | - | （レポートなし） |")
            failed_total += 1
            continue
        root = ET.parse(p).getroot()
        tests = fails = errors = skipped = 0
        for case in root.iter("testcase"):
            tests += 1
            name = f"{case.get('classname', '')}.{case.get('name', '')}"
            if case.find("failure") is not None:
                fails += 1
                failures.append((name, case.find("failure").get("message", "") or case.find("failure").text or ""))
            elif case.find("error") is not None:
                errors += 1
                failures.append((name, case.find("error").get("message", "")))
            elif case.find("skipped") is not None:
                skipped += 1
        failed_total += fails + errors
        md.append(f"| {p.name} | {tests} | {fails} | {errors} | {skipped} |")
    for name, msg in failures:
        annotate("error", "", "", f"テスト失敗 {name}", msg.strip()[:500])
        md.append(f"\n- 失敗: `{name}` {msg.strip()[:200]}")
    write_summary("\n".join(md))
    return 1 if failed_total else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("cppcheck")
    p.add_argument("xml")
    p.add_argument("--fail-on", choices=["none", "non-misra", "any"], default="none")
    p.set_defaults(func=cmd_cppcheck)

    p = sub.add_parser("lizard")
    p.add_argument("csv")
    p.add_argument("--ccn", type=int, default=15)
    p.add_argument("--length", type=int, default=100)
    p.add_argument("--args", type=int, default=6)
    p.set_defaults(func=cmd_lizard)

    p = sub.add_parser("junit")
    p.add_argument("xml", nargs="+")
    p.set_defaults(func=cmd_junit)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
