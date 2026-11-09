#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""漫剧框架机检 F01–F20（规则见 references/07-gates-and-machine-check.md）

用法：
    python scripts/validate_framework.py --dir output
    python scripts/validate_framework.py --dir examples --json
    python scripts/validate_framework.py --selftest

三级语义：FAIL 必须修 / WARN 人工复核 / NOTE 不要求修改。
检查报告写到 --dir/framework-check.txt（--selftest 不写文件）。

方法冲突说明：付费墙分两类——
  · 商业首墙（免费转付费，8–12 集）来自 0xsline/short-drama；
  · 结构墙（挂单元接缝 ±1 集）来自 short-drama-factory。
两者在 60 集三单元时必然不重合，故 F10 只约束结构墙，F11 单独看商业首墙。

v1.1.0：F19/F20 为可选规则——仅当 output/06-emotion-curve.tsv 存在时生效，
且只报 WARN。六个必交文件、G0–G6、F01–F18 的行为一律不变。
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = ["00-intake-card.md", "01-framework-brief.md", "02-unit-chain.tsv",
         "03-beat-table.tsv", "04-ledger.md", "05-handoff.md"]

REQUIRED_FIELDS = ["情绪契约", "流派", "终止条件", "档位", "总集数", "单集时长",
                   "播放面", "套路", "开场", "故事型", "赛道", "画风"]

# 档位: (时长秒区间, 字数带, 合法总集数, 单元集数范围, 卡点最小间隔, 首墙集区间)
EXPECT = {
    "标准档": ((90, 120), (480, 850), {60, 80, 100}, (12, 30), 5, (8, 12)),
    "长档": ((150, 195), (820, 1400), {30, 40, 50}, (6, 15), 3, (4, 6)),
    "漫剧档": ((60, 90), (330, 620), {60, 80, 100}, (12, 30), 5, (8, 12)),
}
SEG_RATIO = {"起势": 15, "攀升": 30, "风暴": 35, "决战": 20}
BEAT_REQUIRED = ["进入状态", "当前压力与钩子", "当集目标", "反对力量", "因果升级",
                 "局势转折", "当集结算", "新债", "出去状态", "钩子类型"]
BEAT_CORE = ["进入状态", "当集结算", "新债", "出去状态", "钩子类型"]
PLACEHOLDERS = ["【填写】", "TODO", "TBD"]

# 可选：单集情绪曲线（v1.1.0）。文件不存在时完全跳过，不进 FILES / F01。
EMOTION_FILE = "06-emotion-curve.tsv"
EMO_TONES = ("甜", "虐", "爽", "紧张")
EMO_CURVES = {"升→降→升", "降→升→悬", "平→炸→钩"}
EMO_ACTS = {"蓄力", "推高", "砸低", "转折"}
EMO_PEAK_ACTS = {"推高", "转折"}


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def rows_tsv(text):
    return list(csv.DictReader(io.StringIO(text.strip("\ufeff")), delimiter="\t"))


def fields_of(md):
    out = {}
    for m in re.finditer(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*[：:]\s*(.+?)\s*$", md, re.M):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def first_int(v):
    m = re.search(r"\d+", str(v or ""))
    return int(m.group()) if m else None


def num_range(v, unit):
    m = re.search(r"(\d+)\s*[–—\-~～至]\s*(\d+)\s*" + unit, str(v or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def clean(s):
    return re.sub(r"[^\w\u4e00-\u9fff]", "", str(s or ""))


def bigrams(s):
    s = clean(s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def tsv_block(md, heading):
    m = re.search(r"##\s*" + heading + r"[^\n]*\n.*?```tsv\s*\n(.*?)```", md, re.S)
    return rows_tsv(m.group(1)) if m else None


def check(directory):
    """返回 (issues, stats)；issue = (code, level, message)。"""
    issues = []

    def add(code, level, msg):
        issues.append((code, level, msg))

    paths = {n: os.path.join(directory, n) for n in FILES}
    missing = [n for n, p in paths.items() if not os.path.isfile(p)]
    if missing:
        add("F01", "FAIL", "缺少交付文件：" + "、".join(missing))
        return issues, {"files": len(FILES) - len(missing)}

    brief = read(paths["01-framework-brief.md"])
    f = fields_of(brief)
    units = rows_tsv(read(paths["02-unit-chain.tsv"]))
    beats = rows_tsv(read(paths["03-beat-table.tsv"]))
    ledger = read(paths["04-ledger.md"])

    # F02 必填字段
    absent = [k for k in REQUIRED_FIELDS if not f.get(k) or any(p in f[k] for p in PLACEHOLDERS)]
    if absent:
        add("F02", "FAIL", "简报缺少或仍是占位符的字段：" + "、".join(absent))
    # 简报里所有字段值的占位符（F18 会再全量扫一遍，这里只做字段级）

    # F03 契约
    contract = f.get("情绪契约", "")
    if not (8 <= len(contract) <= 60) or re.search(r"第\s*\d+\s*集|EP\s*\d+|\bE\d+\b", contract, re.I):
        add("F03", "FAIL", "情绪契约须是一句 8–60 字、不含集号的话；当前：%r" % contract)

    # F04 流派
    if f.get("流派") not in ("情绪流", "剧情流"):
        add("F04", "FAIL", "流派须为「情绪流」或「剧情流」；当前：%r" % f.get("流派"))

    # F05 档位
    fmt = f.get("档位", "")
    total = first_int(f.get("总集数"))
    spec = EXPECT.get(fmt)
    if not spec:
        add("F05", "FAIL", "档位须为标准档/长档/漫剧档；当前：%r" % fmt)
        spec = EXPECT["标准档"]
    if total not in spec[2]:
        add("F05", "FAIL", "档位 %s 的总集数应为 %s；当前：%s" % (fmt, sorted(spec[2]), total))
    dur = num_range(f.get("单集时长"), "秒")
    wc = num_range(f.get("单集字数带"), "字")
    if not dur or abs(dur[0] - spec[0][0]) > 10 or abs(dur[1] - spec[0][1]) > 10:
        add("F05", "FAIL", "单集时长应为 %d–%d 秒；当前：%r" % (spec[0][0], spec[0][1], f.get("单集时长")))
    if not wc or abs(wc[0] - spec[1][0]) > 60 or abs(wc[1] - spec[1][1]) > 60:
        add("F05", "FAIL", "单集字数带应为 %d–%d 字；当前：%r" % (spec[1][0], spec[1][1], f.get("单集字数带")))

    # F06–F09 单元链
    if not (2 <= len(units) <= 4):
        add("F06", "FAIL", "单元数须为 2–4；当前：%d" % len(units))
    parsed_units = []
    for u in units:
        a, b = first_int(u.get("起集")), first_int(u.get("止集"))
        parsed_units.append((a, b, u))
        if a is None or b is None or b < a:
            add("F07", "FAIL", "单元 %s 起止集无效" % u.get("单元ID"))
            continue
        size = b - a + 1
        lo, hi = spec[3]
        if not (lo <= size <= hi):
            add("F07", "FAIL", "单元 %s 共 %d 集，超出 %d–%d 集硬帽" % (u.get("单元ID"), size, lo, hi))
    if total and parsed_units and all(a is not None and b is not None for a, b, _ in parsed_units):
        ordered = sorted(parsed_units, key=lambda x: x[0])
        cursor = 1
        for a, b, u in ordered:
            if a != cursor:
                add("F08", "FAIL", "单元 %s 起集应为 %d 覆盖有缺口/重叠；实际 %d" % (u.get("单元ID"), cursor, a))
                break
            cursor = b + 1
        if cursor != total + 1:
            add("F08", "FAIL", "单元链末集应为 %d；实际 %d" % (total, cursor - 1))
    for i, (a, b, u) in enumerate(sorted(parsed_units, key=lambda x: (x[0] or 0))):
        if i < len(units) - 1 and not clean(u.get("换矛说明")):
            add("F09", "FAIL", "单元 %s 缺「换矛说明」（三缝合一）" % u.get("单元ID"))
        if not clean(u.get("循环终止条件")):
            add("F09", "FAIL", "单元 %s 缺可核对的机制循环终止条件" % u.get("单元ID"))

    # F10–F12 两类付费墙
    ends = [b for _, b, _ in parsed_units if b is not None]
    struct_walls, biz_walls = set(), set()
    for _, _, u in parsed_units:
        for w in re.findall(r"\d+", u.get("结构墙集号") or ""):
            struct_walls.add(int(w))
        for w in re.findall(r"\d+", u.get("商业首墙集号") or ""):
            biz_walls.add(int(w))
    for w in sorted(struct_walls):
        if not any(abs(w - e) <= 1 for e in ends):
            add("F10", "FAIL", "结构墙 EP%d 未落在任何单元接缝 ±1 集（接缝：%s）" % (w, ends))
    beat_flags = {first_int(r.get("集号")) for r in beats if clean(r.get("付费墙")).upper() == "Y"}
    all_walls = struct_walls | biz_walls
    if beat_flags != all_walls:
        add("F10", "FAIL", "节拍表付费墙标记 %s 与单元链声明 %s 不一致" %
            (sorted(x for x in beat_flags if x is not None), sorted(all_walls)))
    if all_walls:
        first_wall = min(all_walls)
        lo, hi = spec[5]
        if not (lo <= first_wall <= hi):
            add("F11", "WARN", "商业首墙 EP%d 不在建议区间 %d–%d 集（可人工复核后保留）" % (first_wall, lo, hi))
        sw = sorted(all_walls)
        for x, y in zip(sw, sw[1:]):
            if y - x < spec[4]:
                add("F12", "FAIL", "卡点 EP%d 与 EP%d 间隔 %d 集，小于 %d 集下限" % (x, y, y - x, spec[4]))
    else:
        add("F12", "FAIL", "未声明任何付费墙")

    # F13–F16 节拍表
    nums = [first_int(r.get("集号")) for r in beats]
    if total and (len(beats) != total or nums != list(range(1, total + 1))):
        add("F13", "FAIL", "节拍表须为 %d 行且集号 1..%d 连续；当前 %d 行" % (total, total, len(beats)))
    for r in beats:
        ep = r.get("集号")
        empty = [k for k in BEAT_CORE if not clean(r.get(k))]
        if empty:
            add("F14", "FAIL", "EP%s 缺字段：%s" % (ep, "、".join(empty)))
        if not clean(r.get("当集结算")) or not clean(r.get("新债")):
            add("F14", "FAIL", "EP%s 必须「先结算、再欠新债」" % ep)
        if len(clean(r.get("当前压力与钩子"))) < 2:
            add("F14", "FAIL", "EP%s 钩子不能只靠故弄玄虚" % ep)
    for prev, cur in zip(beats, beats[1:]):
        if not (bigrams(prev.get("出去状态")) & bigrams(cur.get("进入状态"))):
            add("F15", "WARN", "EP%s → EP%s 出去/进入状态看不出承接" % (prev.get("集号"), cur.get("集号")))
    if beats:
        for seg, target in SEG_RATIO.items():
            cnt = sum(1 for r in beats if clean(r.get("段位")) == seg)
            pct = cnt * 100.0 / len(beats)
            if abs(pct - target) > 5:
                add("F16", "WARN", "四段波形「%s」占比 %.1f%%，偏离 %d%% 超过 5 个百分点" % (seg, pct, target))

    # F17 台账
    for h in ("伏笔账", "人物账", "道具账", "规则账"):
        if not re.search(r"##\s*" + h, ledger):
            add("F17", "FAIL", "台账缺「## %s」" % h)
    fo = tsv_block(ledger, "伏笔账")
    if not fo:
        add("F17", "FAIL", "伏笔账缺 ```tsv 数据表")
    else:
        for r in fo:
            a, b = first_int(r.get("首现集")), first_int(r.get("拟收集团"))
            if not clean(r.get("setup_id")) or a is None or b is None or not clean(r.get("状态")):
                add("F17", "FAIL", "伏笔 %s 缺 setup_id / 首现集 / 拟收集团 / 状态" % r.get("setup_id"))
            elif b - a < 2:
                add("F17", "FAIL", "伏笔 %s 埋设 EP%d 到回收 EP%d 不足 2 集" % (r.get("setup_id"), a, b))
    for h in ("人物账", "道具账", "规则账"):
        blk = tsv_block(ledger, h)
        if not blk or not any(clean(x.get("状态变量") or x.get("状态机") or x.get("内容")) for x in blk):
            add("F17", "FAIL", "%s 为空表" % h)

    # F18 占位符
    for n in FILES:
        if not n.endswith(".md"):
            continue
        t = read(paths[n])
        for p in PLACEHOLDERS:
            if p in t:
                add("F18", "FAIL", "%s 残留占位符 %s" % (n, p))
                break

    # F19/F20 可选：单集情绪曲线。文件不存在时完全跳过，旧项目不受影响。
    emo_rows = []
    emo_path = os.path.join(directory, EMOTION_FILE)
    if os.path.isfile(emo_path):
        emo_rows = rows_tsv(read(emo_path))
        emo_nums = [first_int(r.get("集号")) for r in emo_rows]
        if total and (len(emo_rows) != total or emo_nums != list(range(1, total + 1))):
            add("F20", "WARN", "情绪曲线表须 %d 行且集号 1..%d 连续；当前 %d 行" %
                (total, total, len(emo_rows)))
        for r in emo_rows:
            ep = r.get("集号")
            tone = clean(r.get("情绪主调"))
            curve = (r.get("情绪走势") or "").strip()
            acts = [x.strip() for x in (r.get("作用序列") or "").split("/") if x.strip()]
            raw = [x.strip() for x in (r.get("强度序列") or "").split("/") if x.strip()]
            peak = first_int(r.get("主波序号"))
            try:
                levels = [int(x) for x in raw]
            except ValueError:
                levels = []

            bad19 = []
            if not any(t in tone for t in EMO_TONES):
                bad19.append("情绪主调")
            if curve not in EMO_CURVES:
                bad19.append("情绪走势")
            if len(acts) != 4 or any(a not in EMO_ACTS for a in acts):
                bad19.append("作用序列须4项")
            if len(levels) != 4 or any(not 1 <= x <= 10 for x in levels):
                bad19.append("强度序列须4个1–10")
            if peak is None or not 1 <= peak <= 4:
                bad19.append("主波序号须1–4")
            else:
                if len(acts) == 4 and acts[peak - 1] not in EMO_PEAK_ACTS:
                    bad19.append("主波落在蓄力/砸低位")
                if len(levels) == 4 and (levels[peak - 1] != max(levels) or levels[peak - 1] < 8):
                    bad19.append("主波非全集最高或强度<8")
            if bad19:
                add("F19", "WARN", "EP%s 情绪曲线不合口径：%s" % (ep, "、".join(bad19)))

            gap = first_int(r.get("主波后转折秒"))
            bad20 = []
            if gap is None or not 1 <= gap <= 10:
                bad20.append("主波后转折须在10秒内")
            if acts and "蓄力" not in acts:
                bad20.append("缺蓄力段")
            if acts and not ({"转折", "砸低"} & set(acts)):
                bad20.append("缺回落/转折段")
            if bad20:
                add("F20", "WARN", "EP%s 情绪曲线起伏不合口径：%s" % (ep, "、".join(bad20)))

    stats = {"dir": directory, "files": len(FILES), "units": len(units),
             "episodes": len(beats), "emotion": len(emo_rows),
             "fail": sum(1 for x in issues if x[1] == "FAIL"),
             "warn": sum(1 for x in issues if x[1] == "WARN")}
    return issues, stats


def render(issues, stats):
    # 只写目录名：报告会随包外发，写绝对路径会泄露本机用户名与工作区路径
    d = os.path.normpath(stats.get("dir", ""))
    lines = ["# 框架机检报告", "",
             "目录：%s" % os.path.basename(d),
             "文件 %s / 单元 %s / 分集 %s / 情绪曲线 %s（0=未启用）" %
             (stats.get("files"), stats.get("units"), stats.get("episodes"), stats.get("emotion", 0)),
             "FAIL %d ｜ WARN %d" % (stats["fail"], stats["warn"]), ""]
    if not issues:
        lines.append("全部通过：F01–F20 零 FAIL、零 WARN（F19/F20 仅在 06 表存在时检查）。")
    else:
        lines.append("| 编号 | 级别 | 说明 |")
        lines.append("|---|---|---|")
        for code, level, msg in issues:
            lines.append("| %s | %s | %s |" % (code, level, msg.replace("|", "/")))
    lines += ["", "> FAIL 必须修；WARN 人工复核并在交接单写结论。",
              "> 框架机检通过 ≠ 正文能看，下游仍须跑 E1–E26 / S1–S8。"]
    return "\n".join(lines) + "\n"


def selftest():
    """正例（examples）+ 反例注入，验证规则确实会咬人。"""
    ex = os.path.join(BASE, "examples")
    issues, stats = check(ex)
    fails = [i for i in issues if i[1] == "FAIL"]
    warns = [i for i in issues if i[1] == "WARN"]
    print("[正例] examples/ → FAIL %d / WARN %d" % (len(fails), len(warns)))
    for i in issues:
        print("   %s %s %s" % i)
    if fails or warns:
        print("!! 正例未全绿，请先修正 examples/")
        return 1

    cases = [
        ("F03", "01-framework-brief.md", lambda t: t.replace(
            "- **情绪契约**：等那笔被冒领的账被当着所有人算清",
            "- **情绪契约**：第 8 集男主在宴会上亮出印章打脸")),
        ("F13", "03-beat-table.tsv", lambda t: "\n".join(
            l for l in t.splitlines() if not l.startswith("30\t")) + "\n"),
        ("F10", "02-unit-chain.tsv", lambda t: t.replace("\t20\t10\t起势", "\t25\t10\t起势")),
        ("F18", "05-handoff.md", lambda t: t.replace("# 下游交接单", "# 下游交接单\n\n【填写】")),
        ("F19", EMOTION_FILE, lambda t: t.replace("4/9/6/3", "4/5/9/3", 1)),
        ("F20", EMOTION_FILE, lambda t: t.replace("\t2\t6\t前3秒", "\t2\t18\t前3秒", 1)),
    ]
    optional = [n for n in (EMOTION_FILE,) if os.path.isfile(os.path.join(ex, n))]
    cases = [c for c in cases if c[1] in FILES or c[1] in optional]
    ok = True
    for code, fname, mutate in cases:
        with tempfile.TemporaryDirectory() as td:
            for n in FILES + optional:
                shutil.copy(os.path.join(ex, n), os.path.join(td, n))
            p = os.path.join(td, fname)
            original = read(p)  # 必须先读：open(...,"w") 会立即截断文件
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(mutate(original))
            iss, _ = check(td)
            hit = [i[0] for i in iss]
            good = code in hit
            ok &= good
            print("[反例] 期望 %s → %s（命中：%s）" % (code, "OK" if good else "未命中", ",".join(sorted(set(hit))) or "无"))
    print("\n== 自测%s ==" % ("通过" if ok else "失败"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="output", help="项目产出目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--selftest", action="store_true", help="规则自测（正例+反例注入）")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    d = args.dir if os.path.isabs(args.dir) else os.path.join(os.getcwd(), args.dir)
    issues, stats = check(d)
    report = render(issues, stats)
    if args.json:
        print(json.dumps({"stats": stats,
                          "issues": [{"code": c, "level": l, "msg": m} for c, l, m in issues]},
                         ensure_ascii=False, indent=2))
    else:
        print(report)
    if os.path.isdir(d):
        with open(os.path.join(d, "framework-check.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
    return 1 if stats["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
