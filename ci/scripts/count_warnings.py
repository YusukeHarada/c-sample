#!/usr/bin/env python3
"""ビルドログからコンパイラ警告を数え、ベースラインと比較するスクリプト（ドラフト）。

使い方:
    python count_warnings.py build.log --baseline ci/warning_baseline.txt
    python count_warnings.py build.log --baseline ci/warning_baseline.txt --update   # ベースライン更新

判定:
    警告数 > ベースライン → 終了コード 1（ジョブ失敗）
    警告数 < ベースライン → 成功。ベースラインを下げるよう促すメッセージを出す
    警告数 = ベースライン → 成功

注意:
    - 同じ警告が複数回出力されても 1 件として数える（重複除去）
    - 警告の書式はコンパイラごとに異なるため、--pattern で正規表現を追加・変更する
      例) Tasking: 'W\\d{3}:'  /  GCC・Clang: 'warning:'  /  Green Hills: 'warning #\\d+'
    - 標準出力のみに出力する（PowerShell 5.1 で stderr が誤って失敗扱いになるのを避けるため）
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_PATTERNS = [
    r"\bwarning\b\s*[:#]",   # GCC / Clang / Green Hills 系
    r"\bW\d{3,4}\b\s*:",     # Tasking 系（例: ctc W505: ...）
]


def read_text(path: Path) -> str:
    """文字コードが混在していても落ちないように読む（Shift_JIS のログを想定）。"""
    for enc in ("utf-8", "cp932"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def collect_warnings(log_text: str, patterns: list[str], excludes: list[str]) -> list[str]:
    regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
    ex_regexes = [re.compile(p, re.IGNORECASE) for p in excludes]
    seen: dict[str, None] = {}
    for line in log_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(r.search(line) for r in regexes) and not any(r.search(line) for r in ex_regexes):
            seen.setdefault(line, None)   # 出現順を保ったまま重複除去
    return list(seen)


def read_baseline(path: Path) -> int | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return int(text) if text.isdigit() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=Path, help="ビルドログ")
    ap.add_argument("--baseline", type=Path, required=True, help="許容する警告数を書いたファイル")
    ap.add_argument("--pattern", action="append", help="警告行とみなす正規表現（複数指定可。指定時は既定値を置き換え）")
    ap.add_argument("--exclude", action="append", default=[], help="除外する行の正規表現（例: サードパーティのパス）")
    ap.add_argument("--json", type=Path, help="集計結果の出力先（summarize.py で使用）")
    ap.add_argument("--list", type=Path, help="警告の一覧の出力先")
    ap.add_argument("--update", action="store_true", help="現在の警告数でベースラインを上書きする")
    args = ap.parse_args()

    if not args.log.exists():
        print(f"[ERROR] ログが見つかりません: {args.log}")
        return 2

    warnings = collect_warnings(read_text(args.log), args.pattern or DEFAULT_PATTERNS, args.exclude)
    count = len(warnings)
    baseline = read_baseline(args.baseline)

    if args.list:
        args.list.write_text("\n".join(warnings) + ("\n" if warnings else ""), encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"warnings": count, "baseline": baseline}, ensure_ascii=False), encoding="utf-8")

    print(f"警告数: {count}（ベースライン: {baseline if baseline is not None else '未設定'}）")
    for w in warnings[:20]:
        print(f"  {w}")
    if count > 20:
        print(f"  ...ほか {count - 20} 件（一覧は {args.list or '--list 指定時に出力'}）")

    if args.update:
        args.baseline.write_text(f"{count}\n", encoding="utf-8")
        print(f"[INFO] ベースラインを {count} に更新しました。")
        return 0
    if baseline is None:
        print("[WARN] ベースラインが未設定のため判定をスキップしました。--update で作成してください。")
        return 0
    if count > baseline:
        print(f"[NG] 警告が {count - baseline} 件増えています。新しい警告を修正してください。")
        return 1
    if count < baseline:
        print(f"[OK] 警告が {baseline - count} 件減りました。ci/warning_baseline.txt を {count} に更新してください。")
    else:
        print("[OK] 警告数は増えていません。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
