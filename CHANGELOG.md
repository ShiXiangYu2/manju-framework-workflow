# Changelog

本文件记录本包的每次方法回流与规则变更。**升级触发**：上游档位参数变化、机检编号扩容、新增爆款统计样本、许可状态变化、用户反馈的新坑。
升级流程：重拉源仓库 → 比对上游变更 → 更新 references → 跑 `--selftest` → 展示 diff → **人工确认后写入本文件**。

---

## v1.1.0 · 2026-11-09 · 单集情绪曲线 + 对抗功能位

按上一轮评估中用户确认的 **A 方案（最小增量）** 落地。核心原则：**不动六个必交文件、不动 15 列节拍表、不动 G0–G6 与 F01–F18 的行为**，新增内容一律走「可选文件 + 可选 WARN」。

### 来源（非 GitHub，带保密标识）

用户提供的两份 PDF，均带「字符宇宙」页眉，《短剧情绪大纲模板》另有「**内部资料 禁止外传**」：

- 《短剧情绪大纲模板》3 页 —— 情绪主调、情绪走势三型、逐段秒数、4 个核心情节点的「剧情/情绪/作用（蓄力·推高·砸低·转折）」、第 4 点为本集主波且强度最高、钩子三型、单集自检 5 条（前 3 秒入戏 / 主波 ≥8 分 / 主波后 10 秒内转折 / 钩子够痒 / 没有废戏）。
- 《网文短剧里45种大受欢迎的人物性格类型》16 页 —— 英雄 6 / 导师 4 / 核心原型变体 18 / 情感功能 12 / 阴影特殊 5，每型性格要点 + 阐释 + 一个电影小说例证。

**合规裁决**：只重新撰写方法结论，**不摘录原文、不复刻表单、不搬 45 型清单与例证**；原始 PDF 不进 `sources/` 归档、不随分享包分发、不推公开仓库。两者也不进入 `fetch_sources.py` 的自动回流。详见 `references/08` §5、`NOTICE.md` §2。

### 补的两个真空缺

| 缺口 | v1.0.0 | v1.1.0 |
|---|---|---|
| 单集情绪刻度 | 只有**全剧**四段波形 + 15 秒四拍**任务轴**；`03-beat-table.tsv` 15 列里一个情绪字段都没有 | 可选 `06-emotion-curve.tsv`：四情节点作用/强度、情绪走势、主波最高且 ≥8、主波后 10 秒内转折 |
| 对手类型池 | S1 引擎第 3 问、S3 三缝合一都要求「对手会换招 / 换层不换欲」，但没给可选的对手类型；弧光字段也只给定性要求 | `02` §7 五个对抗功能位 + 正负变体弧光对照；`04` §3 给换层用法 |

### 改前 / 改后（文件级）

| 文件 | 改前 | 改后 |
|---|---|---|
| `references/05-beat-and-episode-map.md` | §1–§7，四拍任务轴 | 新增 §7「单集情绪曲线」（把四拍直接当四情节点，不另造时间轴）；原 §7 顺延为 §8 |
| `references/02-emotion-contract.md` | §1–§6 | 新增 §7「对抗功能位与弧光变体」，**红线 1 不变**（仍只填四件套 + 不变量） |
| `references/04-unit-and-structure.md` | §3 三缝合一 | 加「换层时去哪找新对手」交叉引用与升层示例 |
| `templates/`、`examples/` | 2 份 TSV 模板 / 6 份样例 | **既有 15 列节拍表一字未改**；新增可选 `06-emotion-curve.tsv` 模板 + 60 行样例 |
| `scripts/validate_framework.py` | F01–F18、4 条反例 | 新增 F19/F20（**仅当 06 存在时触发、只报 WARN**）；反例增至 6 条；报告显示「情绪曲线 N（0=未启用）」 |
| `references/07` / `SKILL.md` / `README.md` / `00-READ-ME-FIRST.md` | v1.0.0 | 规则表、文件索引、目录、上手说明同步到 v1.1.0 |
| `references/08` / `NOTICE.md` | 只有 17 个 GitHub 源 | 新增 §5 内部资料来源表与取用红线 |
| `scripts/make_examples.py` / `make_distribution.py` | 生成 2 模板 / 6 样例；文案 F01–F18 | 生成 3 模板 / 7 样例；文案 F01–F20、6 条反例 |

### 主动裁决（明确不采纳）

- **整份情绪大纲表单不进框架层**：逐秒剧情 + 逐点观众感受文案 + 完整表单属**正文写作层**，塞进来会破坏「只做框架、不写正文」的边界。只抽 4 条可核对刻度；整表建议交给下游 `short-drama-factory` 当单集执行卡。
- **钩子三型不加**：资料按观众心理分「信息差 / 情绪断点 / 选择悬念」，`05` §5 的钩子六型已覆盖且更可执行，不搞两套标签。
- **45 型清单与例证全不进包**：与红线 1「不写人物小传」冲突；例证 0 条短剧/漫剧案例，是通用原型学，标题「网文短剧里」名不副实；原文还有编号错乱（「18 种」从（四）起）。只取「功能位 / 正负变体」这一方法思想，当选型灵感用。
- **F19/F20 只给 WARN**：情绪强度是人工相对刻度，机检只能查口径自洽（主波是否最高、≥8、10 秒内转折），**不判断好不好看**，给 FAIL 会逼人造假数据。
- **不改已交付项目**：`story-framework-output/` 与三个已交付 zip/Word 一律不动，旧项目不必回填 06。

### 修复（本版顺带修掉的两个真 bug）

- `make_distribution.py` 的版本号原本只扫 SKILL.md 前 400 字符；v1.1.0 的 description 加长后标题被挤出截取范围，实际打出了 `v0.0.0.zip`。改为**优先读 frontmatter 的 `version:` 字段**，回退再扫全文前 2000 字符；两者都取不到直接报错，不再静默打 0.0.0 包。
- `validate_framework.py` 把 `--dir` 的**绝对路径**写进 `framework-check.txt`，随包外发会泄露本机用户名与工作区路径（v1.0.0 起就存在；此前的「路径残留 0」因检查脚本转义写法有误，是假阴性）。改为只写目录名，并换用无转义的字节串重新复核。

### 验证（2026-11-09 实跑）

```
$ python scripts/make_examples.py
生成完成：templates/*.tsv 3 份（含可选 06），examples/ 7 份（节拍表与情绪曲线各 60 行）

$ python scripts/validate_framework.py --selftest
[正例] examples/ → FAIL 0 / WARN 0
[反例] F03 / F13 / F10 / F18 / F19 / F20 各自精确命中
== 自测通过 ==

$ python scripts/validate_framework.py --dir examples
文件 6 / 单元 3 / 分集 60 / 情绪曲线 60 ｜ FAIL 0 ｜ WARN 0

$ 回归：临时目录只放六个必交文件（无 06）
情绪曲线 0（0=未启用）｜ FAIL 0 ｜ WARN 0   ← 行为与 v1.0.0 一致
```

```
$ python scripts/make_distribution.py
[1/3] 副本自测通过（F01–F20 正例 0 FAIL / 0 WARN、6 条反例精确命中）
[2/3] zip 完整性校验通过
[3/3] dist/manju-framework-workflow-v1.1.0.zip · 34 文件 · SHA256 见 dist/SHA256SUMS.txt

$ 解压到临时目录模拟朋友使用
--selftest → 自测通过；--dir examples → FAIL 0 / WARN 0
包内检查：非 ASCII 文件名 0 / PDF 原件 0 / 第三方源码 0 / 凭据脚本 0
          本机绝对路径与用户名 0 / 第三方原文整句 0
```

### 已知缺口（不掩饰）

1. F19/F20 只查口径，**未验证「按这张表写出来的剧本情绪更好」**；没有端到端盲评。
2. 两份内部资料**未获公开授权**，公开引用原文/表单前须取得资料方书面授权。
3. 情绪强度 1–10 是主观相对刻度，不同项目之间不可比。
4. 公开 GitHub 仓库是否同步本版，需用户单独确认后推送。

---

## v1.0.0 · 2026-11-08 · 首版编排

### 来源
下载并归档 **17 个中的 16 个** GitHub 仓库（清单见 `sources/SOURCES.md`，共 31 MB），核心取用：

- `lixiaoxiao9888-create/short-drama-factory` v4.9.1（MIT，**默认分支 master**）：情绪契约单元链、三档结构、15 秒换挡四拍、前三集节拍卡、四账、机检三级语义、懒加载矩阵
- `zenstory-ai/drama-skills`（MIT）：入口判定、创作者契约、故事引擎六问、机制循环与换代三处置、单集契约七字段、拉片拆解维度、制作形态卡
- `0xsline/short-drama`（MIT）：四段波形 15/30/35/20、卡点密度与五类套路、爽点矩阵
- `mengxiujie/ManjuForge` v1.10.1（MIT-0）：七个记忆文件、故事圣经、伏笔引擎、身份/状态变量分离
- `catyiqian/qianqianwriting`（NOASSERTION）：救猫咪 15/6 拍、31 部爆款统计（4 大套路 / 3 种开场）、情绪欠条三型 —— **只归纳结论**
- 其余 12 个见 `references/08-source-licenses.md`
- 未本地归档：`UnderleveledBuilder/awesome-short-drama-skills`（本机代理对大 zip 反复 `IncompleteRead`，多次串行/并行/curl 重试均中断）。它是索引型仓库，链接与分组结论保留在 `08`；补下：`python scripts/fetch_sources.py --only awesome-short-drama-skills --workers 1`

### 新增
- 七阶段工作流 S0–S6 + 硬门禁 G0–G6 + 按需挂载矩阵（每阶段只读 1 份 reference）
- 8 份重编 references、6 份空模板（含 2 份可粘飞书的 TSV）、1 套 60 集漫剧档合规样例
- 框架机检 F01–F18（三级语义 FAIL/WARN/NOTE），`--selftest` 含正例 + 4 条反例注入
- `fetch_sources.py` 源仓库并行下载 / 自动回流更新，自动生成 `sources/SOURCES.md`（含分支、文件数、许可、时间）
- `make_examples.py` 可重建模板与样例

### 主动裁决
- **两类付费墙**：`0xsline` 的商业首墙（8–12 集）与 `short-drama-factory` 的结构墙（挂单元接缝）在 60 集三单元时必然冲突。拆成两列分别校验，商业首墙豁免接缝规则，两类合并查间隔。见 `references/07` §1。
- **不重造下游**：本包止于交接单，正文/台词/分镜交给 `short-drama-factory` + `drama-skills`；框架机检不替代 E1–E26 / S1–S8。
- **许可边界**：NOASSERTION 仓库只取公开统计数字与方法思想，不复制原文；星数标注实测日期不作质量指标。

### 修复
- `fetch_sources.py` 单分支下载超时被误判为 404 → 改为主分支重试 3 次、单次 180s，仅明确 404 才换分支。
- `fetch_sources.py` 串行下载经代理过慢（16 分钟仅完成 2 个大仓库）→ 改为 `ThreadPoolExecutor` 并行，新增 `--workers`。
- `validate_framework.py --selftest` 反例注入时 `open(...,"w")` 先截断再读，导致文件被清空、前三条反例假阳性 → 改为先读后写，四条规则精确命中 F03/F10/F13/F18。

### 验证
```
[正例] examples/ → FAIL 0 / WARN 0
[反例] F03 / F10 / F13 / F18 各自精确命中
== 自测通过 ==
```

### 已知缺口（未解决，不掩饰）
1. 未做端到端写作实测，只有规则自测与样例；不能据此断言「写出来的剧本好看」。
2. 红果热榜数据未接，S0 明确要求写「无对标、纯原创」，禁止编造。
3. 拉片未自动化，只给字段与工具链接。
4. 4 个源仓库无明确许可，商用前需逐个复核。
5. 合规送审（广电 16 号令）由正文层处理，本包不含。

### 分发补充（v1.0.0 同版 · 2026-11-08 晚）
为「打包发给朋友使用」新增，不改变工作流规则与版本号：

- 新增 `START-HERE.md`（小白共创上手卡）、`00-READ-ME-FIRST.md`（朋友三步上手 + 三种用法）、`NOTICE.md`（许可、来源、隐私与网络行为声明）。
- 新增 `scripts/make_distribution.py`：白名单打包；自动从 `SKILL.md` 读版本号；打包前在临时副本跑 `--selftest`；打包后校验 zip 完整性、文件数、并断言**未夹带第三方源码**；输出 `dist/SHA256SUMS.txt`。
- 产出 `dist/manju-framework-workflow-v1.0.0.zip`（85.1 KB / 32 文件，顶层单一文件夹；文件名全 ASCII，避免 Windows 解压乱码）。模拟朋友解压验证：`--selftest` 与 `--dir examples` 均 rc=0。
- **许可裁决**：默认包不含 `sources/` 下第三方源码（5 个 NOASSERTION 仓库再分发有风险，合计 31 MB / 1319 文件），只附 `sources/SOURCES.md` 链接清单；使用者需要源码时运行 `fetch_sources.py` 自行下载。确需完整包用 `--include-sources`，许可自行核对。
- 新增 `scripts/publish_github.py`：用 GitHub Git Data API 一次 commit 上传白名单文件（绕开本机 `git push` 经代理 502 的问题），支持 `--dry-run` / `--private` / `--update`；`make_distribution.py` 已将它排除在分享包外（需 GitHub 凭据，不适合随包给朋友）。
- 发布目标：`ShiXiangYu2/manju-framework-workflow`（公开，默认分支 `main`），内容与分享包一致，**不含第三方源码**。
- 发布通道踩坑（已修）：GitHub Git Data API 拒绝在**完全空仓库**建 blob（409 `Git Repository is empty`）→ 先用 Contents API 放一个真实文件建初始提交；本机代理偶发 POST 400/409 → `GH.call` 加 3 次有限重试。最终历史为 2 个 commit（初始化 + 全量文件）。
- 待办：本包原创部分尚未附 `LICENSE`，若朋友需公开再分发或商用，应先补一份授权文件。
