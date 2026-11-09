# 漫剧剧本框架创建工作流 v1.1.0

把前面几轮查到的 GitHub 高星剧本工作流**下载、拆解、重编**成一套可执行的「框架创建」Agent Skill。

**它只做上游框架**：爆款拉片 / 原著 / 一句创意 → 情绪契约 → 单元链 → 全剧分集节拍表 → 四账台账 → 交接单。
**它不写正文**：交接单指向 `short-drama-factory`（红果味分集正文）与 `drama-skills`（台词、资产、分镜）。

## 为什么单独做一层

前几轮查到的仓库各有强项，但没有一个覆盖「框架创建」的完整链路：

| 仓库 | 强项 | 缺口 |
|---|---|---|
| `short-drama-factory` | 情绪契约单元链、15 秒四拍、E1–E26 机检 | 直接进正文，框架只在 SKILL.md 里当规则，没有可交付的结构表 |
| `drama-skills` | 创作者契约、故事引擎、机制循环、单集契约、拉片维度 | 12 个 skill 覆盖到成片，框架阶段散在 develop/breakdown 里，无门禁串联 |
| `0xsline/short-drama` | 四段波形、卡点密度、爽点矩阵 | 没有单元链与跨集台账 |
| `ManjuForge` | 七个记忆文件、漫剧角色一致性 | 结构层偏薄 |
| `qianqianwriting` | 救猫咪 + 31 部爆款统计 | 无许可、无工作流 |

本包把它们的**框架层**抽出来，加七个硬门禁、20 条机检规则（F19/F20 为可选）、6 份必交模板 + 1 份可选情绪曲线表，并把下游入口写进交接单。

> **v1.1.0 补的是单集情绪刻度**：v1.0.0 只有「全剧四段波形」和「15 秒四拍任务轴」，没有单集情绪曲线。现在可选 `06-emotion-curve.tsv` 记录四个情节点的作用/强度、主波必须是最高点且 ≥8、主波后 10 秒内转折；不建这张表，一切照旧。

## 快速开始

```bash
cd manju-framework-workflow

# 1. 看随包样例（60 集漫剧档，格式演示，不是写作范本）
python scripts/validate_framework.py --selftest       # 正例 0 FAIL/0 WARN + 6 条反例注入
python scripts/validate_framework.py --dir examples

# 2. 开新项目：先复制六个必交模板；想用情绪曲线再单独复制 06
mkdir output && cp templates/0[0-5]* output/
# 可选：cp templates/06-emotion-curve.tsv output/
# 在 Agent 里依次执行：/框架立项 /定契约 /定套路 /拆单元 /排节拍 /建台账 /框架交付

# 3. 交付前机检
python scripts/validate_framework.py --dir output

# 4. 源仓库自动回流更新（升级前先跑，会刷新 sources/SOURCES.md）
python scripts/fetch_sources.py --force --workers 5
```

三个 TSV 模板只有表头，**可直接粘进飞书多维表格**；列名与 `examples/` 完全一致。`06` 是可选的，不填不影响交付。

## 七阶段

| 阶段 | 指令 | 产出 | 门禁 |
|---|---|---|---|
| S0 情报接入 | `/框架立项` | `00-intake-card.md` | G0 入口/播放面/不可改事实 |
| S1 定契约 | `/定契约` | `01-framework-brief.md` §A | G1 契约单句、流派、终止条件 |
| S2 选套路与赛道 | `/定套路` | 简报 §B | G2 ≥2 个机制不同候选 |
| S3 拆单元定结构 | `/拆单元` | `02-unit-chain.tsv` | G3 单元链覆盖、20–30 集硬帽、三缝合一 |
| S4 排分集节拍 | `/排节拍` | `03-beat-table.tsv`（可选 `06-emotion-curve.tsv`） | G4 每集结算+新债、集间承接、四段配比；可选 F19/F20（WARN） |
| S5 建四账台账 | `/建台账` | `04-ledger.md` | G5 伏笔生命周期、漫剧不变量 |
| S6 机检交接 | `/框架交付` | `05-handoff.md` + 报告 | G6 零 FAIL、无占位符 |

每阶段**只读对应的 1 份 references**，不一次性全量加载——照抄 `short-drama-factory` 的懒加载纪律。

## 一个必须说明的方法冲突

两个源仓库的「付费墙」定义对不上：`0xsline` 要首墙在第 8–12 集（商业转化窗口），`short-drama-factory` 要墙挂单元接缝（60 集三单元时第一道接缝在 EP20）。硬合成一条规则会逼用户造假数据，所以本包**拆成两类**：

- **商业首墙**：填「商业首墙集号」列，8–12 集（长档 4–6），豁免接缝规则，位置偏离只报 WARN；
- **结构墙**：填「结构墙集号」列，必须落在单元止集 ±1 集，违反即 FAIL；
- 两类合并后统一检查相邻间隔 ≥5 集。

## 目录

```text
SKILL.md                     主入口（Agent 读这个）
README.md / CHANGELOG.md     人读说明 / 版本记录
references/01–08/            八份重编知识文件（按阶段挂载）
templates/                   6 份必交空模板 + 1 份可选（含 3 份可粘飞书的 TSV）
examples/                    一套合规样例（60 集漫剧档 + 60 行情绪曲线）
scripts/
  fetch_sources.py           17 个源仓库并行下载 / 自动回流更新
  make_examples.py           重建模板与样例
  validate_framework.py      F01–F20 框架机检 + 自测
sources/                     源仓库归档 + 自动生成的 SOURCES.md
```

## 自测结果（2026-11-09，v1.1.0）

```
[正例] examples/ → FAIL 0 / WARN 0
[反例] F03 契约带集号          → 命中 F03
[反例] F13 删节拍表一行        → 命中 F13
[反例] F10 结构墙移离接缝      → 命中 F10
[反例] F18 残留占位符          → 命中 F18
[反例] F19 主波不是最高点      → 命中 F19
[反例] F20 主波后超 10 秒转折  → 命中 F20
== 自测通过 ==
```

另做了**回归验证**：临时目录只放六个必交文件、不带 `06`，机检输出 `情绪曲线 0（0=未启用）/ FAIL 0 / WARN 0`，行为与 v1.0.0 一致。

历史：v1.0.0 自测时修掉一个真 bug——反例注入 `open(...,"w")` 先截断再读，导致文件被清空、前三条出现假阳性；改成「先读后写」后四条规则各自精确命中。

## 说真话：已知缺口

| 缺口 | 说明 |
|---|---|
| 没做端到端写作实测 | 只验证了框架规则与源仓库可读性，**没有**用真实项目跑完 60 集正文再盲评。规则齐全 ≠ 剧本好看 |
| 热榜数据未接 | S0 要求显式写「无对标、纯原创」，不编造近 30 天榜单 |
| 拉片未自动化 | 只给字段与工具链接，没接 `lapian-notes` / `viral-video-analyzer` 的导出 |
| 许可风险 | 4 个源仓库无明确许可，只归纳结论不复制原文；商用前逐个复核 LICENSE |
| 合规送审未覆盖 | 广电 16 号令红线在正文层由 `short-drama-factory` 处理 |
| 星数会过时 | `references/08` 的星数是 2026-11-06~08 实测，只作定位不作质量指标 |
| 2 份内部资料未获公开授权 | 只归纳方法结论，原 PDF 不随包分发、不推公开仓库；例证 0 条短剧案例，只当选型灵感。见 `references/08` §5 |
| 情绪强度是主观相对刻度 | F19/F20 只查口径自洽（主波是否最高、是否 ≥8、转折是否在 10 秒内），**不判断好不好看**，所以只报 WARN |
| 1 个索引仓库未本地归档 | 17 个中 **16 个已落盘**（31 MB）；`awesome-short-drama-skills` 经本机代理反复传输中断未拉下，链接与分组结论仍在 `08`。补下：`python scripts/fetch_sources.py --only awesome-short-drama-skills --workers 1` |

完整来源、许可与取用边界见 [references/08-source-licenses.md](references/08-source-licenses.md)。

## 自动升级

`fetch_sources.py --force` 重拉 17 个仓库 → 比对上游 CHANGELOG → 更新 references → 跑 `--selftest` → 写 CHANGELOG.md。
**所有写入需人工确认后执行**，不自动覆盖 `output/` 里已填的项目文件。
v1.1.0 起另有 2 份用户提供的内部资料，属一次性人工归纳，**不进入自动回流**（无上游可拉，且授权不允许分发原件），见 `references/08` §5。
