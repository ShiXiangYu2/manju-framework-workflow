#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""源仓库下载器 / 自动回流更新工具

用途：把「漫剧剧本框架创建工作流」引用的 GitHub 仓库浅下载到 sources/，
并生成 sources/SOURCES.md 归档清单（含分支、文件数、许可、链接、下载时间）。

用法：
    python scripts/fetch_sources.py                  # 下载缺失的仓库
    python scripts/fetch_sources.py --force         # 全部重新下载
    python scripts/fetch_sources.py --only <关键字>  # 只更新匹配关键字的仓库
    python scripts/fetch_sources.py --list          # 只列清单不下载

说明：GitHub 匿名 API 有 60 次/小时限流，且部分网络环境下 raw.githubusercontent.com
被代理拦截；本脚本改走 codeload.github.com 的 zip 接口，不依赖 API 与 git。
"""
import argparse
import concurrent.futures
import datetime
import io
import os
import shutil
import sys
import urllib.request
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(BASE, "sources")

# (repo, default_branch, license, role)
REPOS = [
    ("lixiaoxiao9888-create/short-drama-factory", "master", "MIT", "主引擎：情绪契约单元链 / 三档结构 / 15秒四拍 / 机检"),
    ("zenstory-ai/drama-skills", "main", "MIT", "台词质量：12 skill、阶段确认、盲评最优"),
    ("0xsline/short-drama", "main", "MIT", "爽感节奏曲线 / 四层反派 / 五类钩子 / 13题材"),
    ("catyiqian/qianqianwriting", "main", "NOASSERTION", "救猫咪节拍 + 31部爆款统计（仅归纳结论，不复制原文）"),
    ("mengxiujie/ManjuForge", "main", "MIT-0", "漫剧连载：七个记忆文件 + 22项一致性检查"),
    ("bohetang5959/Novel2Manga", "main", "NOASSERTION", "小说→漫剧总纲→分集大纲，伏笔生命周期表"),
    ("UnderleveledBuilder/awesome-story-skills", "main", "CC0-1.0", "索引：819个项目按12类叙事方法分类"),
    ("UnderleveledBuilder/awesome-short-drama-skills", "main", "CC0-1.0", "索引：83个短剧skill + 两轮盲评实测"),
    ("jtydhr88/screenwriting-skills", "main", "MIT", "通用编剧理论 / Truby / 剧集圣经"),
    ("e06084/claude-screenwriting", "main", "MIT", "Vogler/McKee/救猫咪 15-beat 落成故事wiki"),
    ("zhlmi/narrative-to-screen-reader", "main", "NOASSERTION", "框架推断卡：谁的故事 / 谁在动谁在变"),
    ("ciel-oliver/analyze-hit-novel", "main", "NOASSERTION", "爆款逆向：六维拆书 + 双时间线 + 三维节奏"),
    ("VanGong1999/screen-creative-skills", "main", "MIT", "IP评估 + 情节点拆解 + 大纲"),
    ("Shanyin-ai/shanyin-screenwriting-master", "main", "MIT", "全格式编剧：大纲与场景拆解"),
    ("wocha-xiaoli/video-shot-analysis-feishu", "main", "MIT", "拉片输入：逐镜分析落飞书多维表格字段"),
    ("sharon-laicc/viral-video-decomposer", "main", "MIT", "拉片输入：镜头级拆解 + 爆款机制 + 生产蓝图"),
    ("bkingfilm/lapian-notes", "main", "MIT", "拉片输入：逐帧→剧情泳道→情绪曲线"),
]


def fetch_zip(repo, branch):
    """先试 main/master，再回退另一个分支，返回 (bytes, 实际分支)。

    大仓库经代理下载可能要 30~60s，故单分支重试 3 次、单次超时 180s；
    只有明确的 404 才判定为「分支不存在」并换下一个分支。
    """
    candidates = [branch, "master" if branch == "main" else "main"]
    errors = []
    for br in candidates:
        url = "https://codeload.github.com/%s/zip/refs/heads/%s" % (repo, br)
        for attempt in range(3):
            req = urllib.request.Request(url, headers={"User-Agent": "manju-framework-fetcher"})
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    return resp.read(), br
            except Exception as e:  # noqa: BLE001
                errors.append("%s#%d:%s" % (br, attempt + 1, str(e)[:45]))
                if "404" in str(e):
                    break  # 分支确实不存在，换下一个
    raise RuntimeError("all attempts failed: %s" % " | ".join(errors[-5:]))


def extract_strip_top(data, dest):
    """解压 zip 并剥掉顶层目录，防路径穿越。"""
    tmp = dest + ".tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        top = names[0].split("/")[0] + "/"
        count = 0
        for info in zf.infolist():
            n = info.filename
            if not n.startswith(top) or n.endswith("/"):
                continue
            rel = n[len(top):]
            if ".." in rel.split("/") or rel.startswith("/"):
                continue
            target = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            count += 1
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.rename(tmp, dest)
    return count


def write_manifest(rows):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 源仓库归档清单",
        "",
        "> 由 `scripts/fetch_sources.py` 自动生成，最后更新：%s" % now,
        "> 本目录仅作**方法论参考归档**，交付物为上层重编的 references/ 与 templates/。",
        "",
        "| 仓库 | 分支 | 许可 | 状态 | 文件数 | 用途 |",
        "|---|---|---|---|---|---|",
    ]
    for repo, br, lic, role, status, count in rows:
        lines.append("| [%s](https://github.com/%s) | %s | %s | %s | %s | %s |" %
                     (repo, repo, br, lic, status, count, role))
    lines += [
        "",
        "## 许可边界",
        "",
        "- **MIT / MIT-0 / CC0-1.0**：可复用结构与方法。",
        "- **NOASSERTION（无明确许可）**：仅归纳其公开统计结论与设计思想，禁止整段复制原文或代码。",
        "- 归档仓库的权利归原作者所有；商用前请逐个复核 LICENSE。",
        "",
        "## 自动回流更新",
        "",
        "```bash",
        "python scripts/fetch_sources.py            # 补齐缺失仓库",
        "python scripts/fetch_sources.py --only <关键字> --workers 1   # 单独补下某个失败仓库",
        "python scripts/fetch_sources.py --manifest-only                # 断网时按本地现状刷新本清单",
        "python scripts/fetch_sources.py --force   # 全部重拉（升级前先跑这个）",
        "```",
        "",
        "升级流程：重拉 → 读 CHANGELOG/新文件 → 更新 references/ → 跑机检 → 写本包 CHANGELOG.md。",
        "**所有写入需人工确认后执行。**",
    ]
    with open(os.path.join(SOURCES, "SOURCES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="全部重新下载")
    ap.add_argument("--only", default="", help="只处理仓库名含该关键字的项")
    ap.add_argument("--list", action="store_true", help="只列清单")
    ap.add_argument("--max", type=int, default=0, help="本次最多新增下载 N 个仓库（0=不限）")
    ap.add_argument("--workers", type=int, default=4, help="并行下载数（默认 4；代理慢时调大）")
    ap.add_argument("--manifest-only", action="store_true",
                    help="只按本地现状刷新 SOURCES.md，不联网（网络不稳时用于如实归档）")
    args = ap.parse_args()

    os.makedirs(SOURCES, exist_ok=True)
    if args.list:
        for repo, br, lic, role in REPOS:
            print("%-56s %-8s %-14s %s" % (repo, br, lic, role))
        return 0

    if args.manifest_only:
        rows = []
        for repo, br, lic, role in REPOS:
            d = os.path.join(SOURCES, repo.replace("/", "__"))
            if os.path.isdir(d) and os.listdir(d):
                n = sum(len(fs) for _, _, fs in os.walk(d))
                rows.append((repo, br, lic, role, "已归档", n))
                print("已归档 %-53s %d files" % (repo, n), flush=True)
            else:
                rows.append((repo, br, lic, role, "未下载", "-"))
                print("未下载 %-53s（链接与方法说明仍有效）" % repo, flush=True)
        write_manifest(rows)
        print("\n清单已刷新：sources/SOURCES.md")
        return 0

    rows = [None] * len(REPOS)
    pending = []
    skip = 0
    for idx, (repo, br, lic, role) in enumerate(REPOS):
        if args.only and args.only.lower() not in repo.lower():
            rows[idx] = (repo, br, lic, role, "未选", "-")
            continue
        dest = os.path.join(SOURCES, repo.replace("/", "__"))
        if os.path.isdir(dest) and not args.force and os.listdir(dest):
            n = sum(len(fs) for _, _, fs in os.walk(dest))
            rows[idx] = (repo, br, lic, role, "已存在", n)
            skip += 1
            print("SKIP %-56s %d files" % (repo, n), flush=True)
            continue
        pending.append((idx, (repo, br, lic, role), dest))

    if args.max and len(pending) > args.max:
        for idx, (repo, br, lic, role), _ in pending[args.max:]:
            rows[idx] = (repo, br, lic, role, "本批跳过", "-")
        pending = pending[:args.max]

    def work(entry):
        idx, (repo, br, lic, role), dest = entry
        try:
            data, real_br = fetch_zip(repo, br)
            n = extract_strip_top(data, dest)
            print("OK   %-56s %-7s %5d files %7.1f KB" % (repo, real_br, n, len(data) / 1024), flush=True)
            return idx, (repo, real_br, lic, role, "OK", n), "OK"
        except Exception as e:  # noqa: BLE001
            print("FAIL %-56s %s" % (repo, str(e)[:120]), file=sys.stderr, flush=True)
            return idx, (repo, br, lic, role, "FAIL", "-"), "FAIL"

    ok = fail = 0
    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
            for idx, row, status in ex.map(work, pending):
                rows[idx] = row
                ok += status == "OK"
                fail += status == "FAIL"
    rows = [r for r in rows if r is not None]
    write_manifest(rows)
    print("\n== 新增 %d / 跳过 %d / 失败 %d ==  清单: sources/SOURCES.md" % (ok, skip, fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
