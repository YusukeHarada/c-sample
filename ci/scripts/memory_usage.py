#!/usr/bin/env python3
"""ELF ファイルから ROM/RAM 使用量をメモリ領域ごとに集計し、上限と比較するスクリプト（ドラフト）。

使い方:
    python memory_usage.py out/app.elf --config ci/memory_limits.json --csv memory_usage.csv

集計方法（プログラムヘッダ = ロードセグメントを使用）:
    - 各 PT_LOAD セグメントについて
        * 格納先アドレス（LMA = p_paddr）に p_filesz バイト（初期値・コード）を計上 → 主に Flash
        * 実行時アドレス（VMA = p_vaddr）に p_memsz バイトを計上 → 主に RAM
      LMA と VMA が同じ領域なら二重計上しない（コードや定数を Flash 上で直接実行する場合）
    - アドレスがどの領域にも入らないセグメントは "unmapped" として警告する
    - config の regions が空の場合は、セクションのフラグで簡易判定する
        * 書き込み不可かつ ALLOC → ROM
        * 書き込み可かつ PROGBITS（.data 相当）→ ROM と RAM の両方
        * NOBITS（.bss 相当）→ RAM

判定:
    いずれかの領域が limit_percent を超えたら終了コード 1、warn_percent を超えたら警告のみ

注意:
    - Tasking などで LMA がプログラムヘッダに正しく出ない場合は、map ファイルの値と突き合わせて確認すること
    - スタック・ヒープをリンカで確保していない場合、RAM 使用量には含まれない
"""
import argparse
import csv
import json
import sys
from pathlib import Path

try:
    from elftools.elf.elffile import ELFFile
    from elftools.elf.constants import SH_FLAGS
except ImportError:
    print("[ERROR] pyelftools が必要です: pip install pyelftools")
    sys.exit(2)


def parse_int(value) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    for r in cfg.get("regions", []):
        r["start"] = parse_int(r["start"])
        r["size"] = parse_int(r["size"])
    return cfg


def find_region(addr: int, regions: list[dict]) -> str | None:
    for r in regions:
        if r["start"] <= addr < r["start"] + r["size"]:
            return r["name"]
    return None


def usage_by_segments(elf: ELFFile, regions: list[dict]) -> tuple[dict, list[str]]:
    usage = {r["name"]: 0 for r in regions}
    notes = []
    for seg in elf.iter_segments():
        if seg["p_type"] != "PT_LOAD" or seg["p_memsz"] == 0:
            continue
        lma, vma = seg["p_paddr"], seg["p_vaddr"]
        filesz, memsz = seg["p_filesz"], seg["p_memsz"]
        lma_region = find_region(lma, regions) if filesz else None
        vma_region = find_region(vma, regions)

        if filesz and lma_region is None:
            notes.append(f"LMA 0x{lma:08X}（{filesz} bytes）がどの領域にも入りません")
        if vma_region is None:
            notes.append(f"VMA 0x{vma:08X}（{memsz} bytes）がどの領域にも入りません")

        if lma_region == vma_region and lma_region is not None:
            usage[lma_region] += max(filesz, memsz)
            continue
        if lma_region:
            usage[lma_region] += filesz
        if vma_region:
            usage[vma_region] += memsz
    return usage, notes


def usage_by_sections(elf: ELFFile) -> dict:
    rom = ram = 0
    for sec in elf.iter_sections():
        flags = sec["sh_flags"]
        if not flags & SH_FLAGS.SHF_ALLOC or sec["sh_size"] == 0:
            continue
        size = sec["sh_size"]
        if sec["sh_type"] == "SHT_NOBITS":
            ram += size
        elif flags & SH_FLAGS.SHF_WRITE:
            rom += size
            ram += size
        else:
            rom += size
    return {"ROM": rom, "RAM": ram}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("elf", type=Path)
    ap.add_argument("--config", type=Path, required=True, help="メモリ領域と上限の定義（JSON）")
    ap.add_argument("--json", type=Path, help="集計結果の出力先（summarize.py で使用）")
    ap.add_argument("--csv", type=Path, help="領域ごとの使用量の出力先")
    args = ap.parse_args()

    if not args.elf.exists():
        print(f"[ERROR] ELF が見つかりません: {args.elf}")
        return 2

    cfg = load_config(args.config)
    regions = cfg.get("regions", [])
    with args.elf.open("rb") as f:
        elf = ELFFile(f)
        if regions:
            usage, notes = usage_by_segments(elf, regions)
            sizes = {r["name"]: r["size"] for r in regions}
            limits = {r["name"]: r for r in regions}
        else:
            usage, notes = usage_by_sections(elf), []
            sizes = {k: parse_int(cfg.get(f"{k.lower()}_size", 0)) for k in usage}
            limits = {k: cfg.get(k.lower(), {}) for k in usage}

    default_warn = cfg.get("warn_percent", 80)
    default_limit = cfg.get("limit_percent", 95)
    rows, result, ng = [], {}, False

    print(f"{'領域':<12}{'使用量(bytes)':>15}{'容量(bytes)':>15}{'使用率':>9}  判定")
    for name, used in usage.items():
        size = sizes.get(name) or 0
        pct = used * 100.0 / size if size else 0.0
        warn = limits.get(name, {}).get("warn_percent", default_warn)
        limit = limits.get(name, {}).get("limit_percent", default_limit)
        status = "OK"
        if size and pct > limit:
            status, ng = "NG", True
        elif size and pct > warn:
            status = "WARN"
        print(f"{name:<12}{used:>15,}{size:>15,}{pct:>8.1f}%  {status}")
        rows.append({"region": name, "used": used, "size": size, "percent": round(pct, 2), "status": status})
        result[name] = {"used": used, "size": size, "percent": round(pct, 2)}

    for n in notes:
        print(f"[WARN] {n}")

    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["region", "used", "size", "percent", "status"])
            w.writeheader()
            w.writerows(rows)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")

    if ng:
        print("[NG] 上限を超えた領域があります。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
