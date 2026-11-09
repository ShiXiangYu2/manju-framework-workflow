# 先看我 · 漫剧剧本框架创建工作流

你拿到的是一个**和 AI 一起搭故事骨架**的工具包。

它帮你把一部 60 集（或 40 / 80 / 100 集）的漫剧，在动笔前想清楚：观众每集在等什么、这个「等」分几段结清、每集结算什么又欠下什么、伏笔怎么不穿帮。最后给你六张必交表 + 一份交接单；想再细一点，可以加一张可选的单集情绪曲线表。

**它不写台词，也不写剧本正文**——正文由交接单指向下游工具去写。

---

## 三步开始（新手推荐，不用装任何东西）

1. **解压**到任意文件夹。
2. 打开 **`START-HERE.md`**，复制里面「第一步」那段**填 5 个空**的开场提示词。
3. 发给你的 AI 助手（WorkBuddy / Claude / Cursor / 其他能读本地文件的 Agent 都行），并补一句：

   > 请先读本目录的 `SKILL.md`，按 S0 带我走。**不要一次跑完七个阶段**，每阶段给我 2 个候选让我挑。

之后你只做两件事：**说想法、挑一个**。表格、结构、自检由 AI 写。填不出来的空写「不知道 / 你帮我定」即可。

> 如果你的 AI 助手读不到本地文件：把 `SKILL.md` 和 `START-HERE.md` 的内容直接粘进对话也行。

---

## 三种用法

| 方式 | 适合谁 | 怎么做 |
|---|---|---|
| 零安装（推荐） | 小白、偶尔用一次 | 按上面三步，什么都不装 |
| 装成 Agent Skill | 经常用、想在任意对话里直接调用 | 把整个文件夹复制到 `~/.workbuddy/skills/manju-framework-workflow/`（Windows 是 `%USERPROFILE%\.workbuddy\skills\`）；Claude Code 用 `~/.claude/skills/` |
| 只用表格 | 想自己填、不打算用 AI | 把 `templates/` 里三份 `.tsv` 直接粘进飞书多维表格，列名已对齐 `examples/`；第三份 `06` 是可选的 |

---

## 可选：命令行（新手可完全跳过）

需要 **Python 3.8+**，只用标准库，**不用 pip install**。

```bash
python scripts/validate_framework.py --selftest       # 确认规则可用，应显示「自测通过」

mkdir output && cp templates/0[0-5]* output/         # 六个必交模板
# 可选：cp templates/06-emotion-curve.tsv output/  （单集情绪曲线，不建也照常交付）
# 按 S0 → S6 在 output/ 里填内容
python scripts/validate_framework.py --dir output    # 交付前机检，报告写 output/framework-check.txt
```

`templates/` 是空模板，**别直接改**；`output/` 才是你自己的项目文件。
`06-emotion-curve.tsv` 是 v1.1.0 的可选表（每集四个情节点的作用/强度、主波、10 秒内转折），不建它时机检完全跳过相关规则，旧项目不用回填。
`make_examples.py` 会重建模板与样例，正常情况下不用跑。

---

## 目录一览

```text
00-READ-ME-FIRST.md   本文件
START-HERE.md         小白上手卡：开场提示词 + 示范对话 + 术语小词典
NOTICE.md             许可与来源声明（外发前请一起保留）
SKILL.md              Agent 主入口：七阶段 S0–S6 + 门禁 G0–G6
README.md / CHANGELOG.md  人读说明 / 版本记录
references/ 01–08     八份方法文件，AI 每阶段只按需挂载一份
templates/  7 份      6 份必交 + 1 份可选（含 3 份可粘飞书的 TSV）
examples/   8 份      60 集合规样例 + 60 行情绪曲线 + 机检报告
scripts/    4 个      validate_framework（机检）/ fetch_sources（拉源仓库）
                      / make_examples（重建样例）/ make_distribution（重新打包）
sources/SOURCES.md    17 个上游仓库的链接、分支、许可清单（**仅清单，不含源码**）
```

---

## 四条提醒

1. **`examples/` 是格式演示**，内容故意机械重复，只看列名和填法，**别当范文抄**。
2. **S4 排节拍先看前 3 集样板**，认可了再批量铺满，否则改起来比重做还贵。
3. **共创约定**：每阶段 AI 给 2 个候选 + 人话摘要，你说「行」才落盘；机检报 FAIL 让 AI 改，你只确认剧情逻辑。
4. **上游源码未随包附带**：出于许可原因（部分上游仓库无明确许可证），本包只给链接清单。需要自己研究时运行 `python scripts/fetch_sources.py --workers 5`，脚本只从 GitHub 只读下载公开仓库，**不上传本机任何数据**。

---

版本 **v1.1.0** · 打包日期 2026-11-09 · 变更见 `CHANGELOG.md` · 许可见 `NOTICE.md`
