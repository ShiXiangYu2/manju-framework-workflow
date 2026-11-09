#!/usr/bin/env python3
"""把本工作流打成一个可直接外发的干净 zip。

默认**不含 sources/ 下的第三方源码**（其中若干仓库无明确许可，再分发有风险），
只附 `sources/SOURCES.md` 链接清单。确需完整离线源码时用 --include-sources，
并自行核对各仓库许可证。

用法：
    python scripts/make_distribution.py                     # 推荐：干净分享包
    python scripts/make_distribution.py --include-sources  # 完整包，自行承担许可核对
    python scripts/make_distribution.py --list             # 只看将打包哪些文件

产出：dist/manju-framework-workflow-v<版本>.zip + dist/SHA256SUMS.txt
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

ROOT_FILES = [
    "00-READ-ME-FIRST.md",
    "NOTICE.md",
    "START-HERE.md",
    "README.md",
    "SKILL.md",
    "CHANGELOG.md",
]
SUBDIRS = {
    "references": {".md"},
    "templates": {".md", ".tsv"},
    "examples": {".md", ".tsv", ".txt"},
    "scripts": {".py"},
}
ALWAYS = ["sources/SOURCES.md"]


def version() -> str:
    """优先读 frontmatter 的 version 字段，避免长 description 把标题挤出截取范围。"""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^version:\s*(\d+\.\d+\.\d+)\s*$", text, re.M)
    if m:
        return m.group(1)
    m = re.search(r"v(\d+\.\d+\.\d+)", text[:2000])
    if m:
        return m.group(1)
    raise RuntimeError("SKILL.md 里找不到 version 字段或 vX.Y.Z 标题，拒绝打 0.0.0 包")


def collect(include_sources: bool) -> list[str]:
    rels: list[str] = []
    for name in ROOT_FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError("缺少根目录文件: %s" % name)
        rels.append(name)
    for sub, exts in SUBDIRS.items():
        d = ROOT / sub
        if not d.is_dir():
            raise FileNotFoundError("缺少目录: %s" % sub)
        for p in sorted(d.iterdir()):
            if not (p.is_file() and not p.name.startswith(".") and p.suffix.lower() in exts):
                continue
            if sub == "scripts" and p.name == "publish_github.py":
                continue  # 需 GitHub 凭据，仅本地发布用，不进分享包
            rels.append("%s/%s" % (sub, p.name))
    for name in ALWAYS:
        if not (ROOT / name).is_file():
            raise FileNotFoundError("缺少来源清单: %s" % name)
        rels.append(name)
    if include_sources:
        for p in sorted((ROOT / "sources").rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".tmp":
                rel = p.relative_to(ROOT).as_posix()
                if rel not in rels:
                    rels.append(rel)
    rels = sorted(set(rels))
    leaks = [r for r in rels if r.startswith("sources/") and r not in ALWAYS]
    if not include_sources and leaks:
        raise RuntimeError("默认包不得夹带第三方源码，发现 %d 个" % len(leaks))
    return rels


def main() -> int:
    ap = argparse.ArgumentParser(description="打包漫剧框架工作流为分享 zip")
    ap.add_argument("--list", action="store_true", help="只列将打包的文件")
    ap.add_argument("--include-sources", action="store_true",
                    help="附带第三方源码（需自行核对许可，默认关闭）")
    args = ap.parse_args()

    ver = version()
    name = "manju-framework-workflow-v%s" % ver
    rels = collect(args.include_sources)
    if args.list:
        for r in rels:
            print(r)
        print("-- 共 %d 个文件" % len(rels))
        return 0

    with tempfile.TemporaryDirectory(prefix="manju-dist-") as td:
        stage = Path(td) / name
        for rel in rels:
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)

        check = subprocess.run(
            [sys.executable, str(stage / "scripts" / "validate_framework.py"), "--selftest"],
            cwd=str(stage), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120,
        )
        if check.returncode != 0 or "自测通过" not in (check.stdout or ""):
            print("副本自测失败，已中止打包:\n%s\n%s" % (check.stdout, check.stderr), file=sys.stderr)
            return 2
        print("[1/3] 副本自测通过（F01–F20 正例 0 FAIL / 0 WARN、6 条反例精确命中）")

        DIST.mkdir(exist_ok=True)
        zp = DIST / (name + ".zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for rel in rels:
                z.write(stage / rel, "%s/%s" % (name, rel))

        with zipfile.ZipFile(zp) as z:
            bad = z.testzip()
            if bad is not None:
                raise RuntimeError("zip 校验失败: %s" % bad)
            names = z.namelist()
            if len(names) != len(rels):
                raise RuntimeError("zip 文件数不符: %d != %d" % (len(names), len(rels)))
            if not args.include_sources:
                leaked = [n for n in names
                          if n.startswith("%s/sources/" % name) and not n.endswith("SOURCES.md")]
                if leaked:
                    raise RuntimeError("zip 夹带第三方源码: %s" % leaked[:3])
        print("[2/3] zip 完整性校验通过")

        sha = hashlib.sha256(zp.read_bytes()).hexdigest()
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        (DIST / "SHA256SUMS.txt").write_text(
            "# %s · %s\n%s  %s\n" % (name, stamp, sha, zp.name), encoding="utf-8")

    groups: dict[str, int] = {}
    for r in rels:
        key = r.split("/")[0] if "/" in r else "(根目录)"
        groups[key] = groups.get(key, 0) + 1
    print("[3/3] 打包完成\n")
    print("文件: %s" % zp)
    print("体积: %.1f KB · %d 个文件" % (zp.stat().st_size / 1024, len(rels)))
    print("内容: " + "  ".join("%s %d" % (k, v) for k, v in sorted(groups.items())))
    print("SHA256: %s" % sha)
    print("第三方源码: %s" % ("已附带（请核对许可）" if args.include_sources else "未附带（仅 SOURCES.md 清单）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
