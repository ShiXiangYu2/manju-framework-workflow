# 源仓库归档清单

> 由 `scripts/fetch_sources.py` 自动生成，最后更新：2026-11-08 19:25:03
> 本目录仅作**方法论参考归档**，交付物为上层重编的 references/ 与 templates/。

| 仓库 | 分支 | 许可 | 状态 | 文件数 | 用途 |
|---|---|---|---|---|---|
| [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | master | MIT | 已归档 | 33 | 主引擎：情绪契约单元链 / 三档结构 / 15秒四拍 / 机检 |
| [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | main | MIT | 已归档 | 597 | 台词质量：12 skill、阶段确认、盲评最优 |
| [0xsline/short-drama](https://github.com/0xsline/short-drama) | main | MIT | 已归档 | 12 | 爽感节奏曲线 / 四层反派 / 五类钩子 / 13题材 |
| [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) | main | NOASSERTION | 已归档 | 3 | 救猫咪节拍 + 31部爆款统计（仅归纳结论，不复制原文） |
| [mengxiujie/ManjuForge](https://github.com/mengxiujie/ManjuForge) | main | MIT-0 | 已归档 | 86 | 漫剧连载：七个记忆文件 + 22项一致性检查 |
| [bohetang5959/Novel2Manga](https://github.com/bohetang5959/Novel2Manga) | main | NOASSERTION | 已归档 | 4 | 小说→漫剧总纲→分集大纲，伏笔生命周期表 |
| [UnderleveledBuilder/awesome-story-skills](https://github.com/UnderleveledBuilder/awesome-story-skills) | main | CC0-1.0 | 已归档 | 50 | 索引：819个项目按12类叙事方法分类 |
| [UnderleveledBuilder/awesome-short-drama-skills](https://github.com/UnderleveledBuilder/awesome-short-drama-skills) | main | CC0-1.0 | 未下载 | - | 索引：83个短剧skill + 两轮盲评实测 |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | main | MIT | 已归档 | 91 | 通用编剧理论 / Truby / 剧集圣经 |
| [e06084/claude-screenwriting](https://github.com/e06084/claude-screenwriting) | main | MIT | 已归档 | 51 | Vogler/McKee/救猫咪 15-beat 落成故事wiki |
| [zhlmi/narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) | main | NOASSERTION | 已归档 | 30 | 框架推断卡：谁的故事 / 谁在动谁在变 |
| [ciel-oliver/analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel) | main | NOASSERTION | 已归档 | 29 | 爆款逆向：六维拆书 + 双时间线 + 三维节奏 |
| [VanGong1999/screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) | main | MIT | 已归档 | 186 | IP评估 + 情节点拆解 + 大纲 |
| [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | main | MIT | 已归档 | 4 | 全格式编剧：大纲与场景拆解 |
| [wocha-xiaoli/video-shot-analysis-feishu](https://github.com/wocha-xiaoli/video-shot-analysis-feishu) | main | MIT | 已归档 | 7 | 拉片输入：逐镜分析落飞书多维表格字段 |
| [sharon-laicc/viral-video-decomposer](https://github.com/sharon-laicc/viral-video-decomposer) | main | MIT | 已归档 | 40 | 拉片输入：镜头级拆解 + 爆款机制 + 生产蓝图 |
| [bkingfilm/lapian-notes](https://github.com/bkingfilm/lapian-notes) | main | MIT | 已归档 | 97 | 拉片输入：逐帧→剧情泳道→情绪曲线 |

## 许可边界

- **MIT / MIT-0 / CC0-1.0**：可复用结构与方法。
- **NOASSERTION（无明确许可）**：仅归纳其公开统计结论与设计思想，禁止整段复制原文或代码。
- 归档仓库的权利归原作者所有；商用前请逐个复核 LICENSE。

## 自动回流更新

```bash
python scripts/fetch_sources.py            # 补齐缺失仓库
python scripts/fetch_sources.py --only <关键字> --workers 1   # 单独补下某个失败仓库
python scripts/fetch_sources.py --manifest-only                # 断网时按本地现状刷新本清单
python scripts/fetch_sources.py --force   # 全部重拉（升级前先跑这个）
```

升级流程：重拉 → 读 CHANGELOG/新文件 → 更新 references/ → 跑机检 → 写本包 CHANGELOG.md。
**所有写入需人工确认后执行。**
