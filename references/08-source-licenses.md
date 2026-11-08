# 源仓库、许可与取用边界

> 归档目录：`sources/`（由 `scripts/fetch_sources.py` 生成，清单见 `sources/SOURCES.md`）
> 星数为 2026-11-06~08 从 GitHub API 拉的实测值，**会变化，别拿它当质量指标**。
> **归档状态：16/17 已本地落盘（31 MB）**；`awesome-short-drama-skills` 因本机代理对大 zip 反复传输中断未拉下，它是索引型仓库，本包只取它的分组结论，不影响工作流执行。补下命令见下。

## 1. 17 个源仓库

| 仓库 | ★(约) | 许可 | 本包取用了什么 | 阶段 |
|---|---|---|---|---|
| [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | 560 | MIT | 情绪契约单元链、三档结构、15 秒四拍、前三集节拍卡、付费墙换算、四账、机检三级语义 | S1/S3/S4/S5 |
| [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 3857 | MIT | 入口判定、创作者契约、故事引擎、机制循环与换代、单集契约七字段、拉片拆解维度、制作形态卡 | S0/S1/S2/S3/S4/S5 |
| [0xsline/short-drama](https://github.com/0xsline/short-drama) | 1581 | MIT | 四段波形 15/30/35/20、卡点密度与五类套路、爽点矩阵、13 题材 | S3/S4 |
| [mengxiujie/ManjuForge](https://github.com/mengxiujie/ManjuForge) | 30 | MIT-0 | 七个记忆文件、故事圣经、伏笔引擎、身份不变量/状态变量、22 项一致性检查 | S1/S5 |
| [UnderleveledBuilder/awesome-story-skills](https://github.com/UnderleveledBuilder/awesome-story-skills) | 8 | CC0-1.0 | 819 个项目按 12 类叙事方法分类，选型索引 | 索引 |
| [UnderleveledBuilder/awesome-short-drama-skills](https://github.com/UnderleveledBuilder/awesome-short-drama-skills) | 1893 | CC0-1.0 | 83 个短剧 skill 分组与两轮盲评实测 | 索引 |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | 1992 | MIT | 通用编剧理论 / Truby / 剧集圣经（本包只作背景，未直接采纳其结构） | 参考 |
| [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | 1462 | MIT | 全格式大纲与场景拆解（背景参考） | 参考 |
| [VanGong1999/screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) | 501 | MIT | IP 评估 + 情节点拆解（背景参考） | 参考 |
| [e06084/claude-screenwriting](https://github.com/e06084/claude-screenwriting) | 10 | MIT | Vogler/McKee/救猫咪落成故事 wiki、15-beat 健康度诊断（背景参考） | 参考 |
| [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) | 54 | **NOASSERTION** | 救猫咪 15/6 拍压缩、**31 部爆款统计（4 大套路 / 3 种开场占比）**、情绪欠条三型、10 类故事型 | S2/S4 |
| [zhlmi/narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) | 131 | **NOASSERTION** | 框架推断卡（谁的故事 / 谁在动谁在变 / 框架未定不往下写） | S1 |
| [ciel-oliver/analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel) | 19 | **NOASSERTION** | 爆款逆向：六维拆书、双时间线、三维节奏（背景参考） | 参考 |
| [bohetang5959/Novel2Manga](https://github.com/bohetang5959/Novel2Manga) | 1 | **NOASSERTION** | 改编阅读纪律、分阶段交付、伏笔表、集数不预设 | S0/S3/S5 |
| [wocha-xiaoli/video-shot-analysis-feishu](https://github.com/wocha-xiaoli/video-shot-analysis-feishu) | 46 | MIT | 拉片结果写入飞书多维表格的字段设计 | S0 |
| [sharon-laicc/viral-video-decomposer](https://github.com/sharon-laicc/viral-video-decomposer) | 12 | MIT | 镜头级拉片 + 爆款机制 + 生产蓝图（背景参考） | S0 |
| [bkingfilm/lapian-notes](https://github.com/bkingfilm/lapian-notes) | 750 | MIT | 逐帧 → 剧情泳道 → 情绪曲线的拉片方法（背景参考） | S0 |

许可为归档时的判断；标 NOASSERTION 的表示仓库未给出明确 LICENSE 或本包未逐一复核，**一律按「只归纳结论、不复制原文」处理**。商用前请逐个复核 LICENSE。

## 2. 取用边界（说真话）

- **本包所有 `references/` 是重编与归纳**，不是原文摘录；MIT / MIT-0 / CC0 部分可自由改造，NOASSERTION 部分只保留公开统计数字与方法思想。
- **没有做端到端写作实测**：本包验证的是框架机检规则自测与源仓库可读性，没有用真实项目跑完 60 集正文再盲评。别把「规则齐全」当成「写出来的剧本好看」。
- **那份 awesome 清单的盲评有局限**：单模型、每 skill 3 次，且产出稿夹带编号与自检表，下游出片前要清理。它的结论适合选型，不适合当质量证明。
- **星数与框架质量倒挂**：最系统的救猫咪+爆款统计只有 54★，漫剧七记忆文件 30★；1992★ 那套是通用编剧理论，直接拿来写红果会「太文艺、钩子不够猛」。
- **分支坑**：`short-drama-factory` 默认分支是 `master` 不是 `main`，`blob/main/...` 会 404；本包 `fetch_sources.py` 已处理。

## 3. 自动回流升级（写入需人工确认）

```text
1. python scripts/fetch_sources.py --force
   → 重拉 17 仓库，刷新 sources/SOURCES.md（时间/分支/文件数/许可）
2. 比对上游 CHANGELOG 与新增 references，列出方法变更点
3. 更新本包 references/ 01~08 → 更新本表 → 跑 validate_framework.py --selftest
4. 写 CHANGELOG.md：版本号 / 变更点 / 影响的 Gate 与 F 规则 / 来源版本
5. 向用户展示 diff，获确认后才落盘；不自动覆盖 output/ 里的项目文件
```

升级触发条件建议：上游档位参数变化（时长/字数/集数）、机检编号扩容、新增爆款统计样本、许可状态变化。

## 4. 已知缺口

| 缺口 | 现状 | 补法 |
|---|---|---|
| 没有真实项目回测 | 只有 `examples/` 合规样例与反例注入自测 | 拿一个已完结项目倒填，看 Gate 是否能复现其结构 |
| 红果热榜数据未接 | S0 明确写「无对标、纯原创」，不编数据 | 接 `OnlyShot` 阶段 0 的市场情报扫描或飞书 Base 拉片库 |
| 拉片未自动化 | 只给字段与工具链接 | 接 `viral-video-analyzer` / `lapian-notes` 导出 |
| 合规送审未覆盖 | 本包不含广电 16 号令红线全文 | 正文层用 `short-drama-factory` 的 `screenplay-compliance-rules.md` |
