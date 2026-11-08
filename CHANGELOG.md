# Changelog

本文件记录本包的每次方法回流与规则变更。**升级触发**：上游档位参数变化、机检编号扩容、新增爆款统计样本、许可状态变化、用户反馈的新坑。
升级流程：重拉源仓库 → 比对上游变更 → 更新 references → 跑 `--selftest` → 展示 diff → **人工确认后写入本文件**。

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
