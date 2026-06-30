# MEMORY.md — 记忆索引

> 强类型记忆系统：user / feedback / project / reference
> 每行一条，~150字以内，指向 memory/ 下的具体文件

## user
- [东哥角色](user/东哥角色.md) — 东哥，称呼"东哥"，量化投资/AI前沿深度自修中，注重实战价值
- [协作风格](user/协作风格.md) — 喜欢结构清晰、结论先行、有虎气的表达
- [核心要求](user/核心要求.md) — 三思而行、结论先行、能省则省、完成不辩解

## learning updates
- [会计学L7财务分析](computer-science/finance/accounting-14-financial-analysis-L7.md) — 2026-05-27：从报表阅读到投资判断，贯通ROIC/利润质量/FCF/估值/量化因子

## feedback
- [UI修改确认真实服务来源](feedback/ui-修改确认真实服务来源.md) — 2026-06-12：UI改动前必须确认实际服务/端口/静态文件来源，改后重启对应服务并curl验证
- [Hermes深度理解优先](feedback/hermes-深度理解优先.md) — 2026-06-02：Hermes 任务目标是运行级理解与完美融合，不能停留在覆盖率/简单阅读
- [Hermes目标是超越而非照搬](feedback/hermes-目标是超越而非照搬.md) — 2026-06-02：终局不是复刻 Hermes，而是在透彻理解后让 OpenClaw 功能上限更强
- [Hermes高标准高质量优先](feedback/hermes-高标准高质量优先.md) — 2026-06-02：不抢时间，以透彻理解、证据闭环、验证可靠为优先级
- [沟通风格](feedback/沟通风格.md) — 简洁直接、先给结论再展开、避开场话过渡
- [模型切换审批规则](feedback/模型切换审批规则.md) — 2026-06-07：主模型严禁切到 deepseek，必须保持 GPT-5.5；任何主模型变更先经东哥同意
- [授权内自动推进](feedback/授权内自动推进-不反问下一步.md) — 2026-06-07：已明确授权范围后，除审批边界外必须连续执行，不再反问“下一步怎么做”
- [多Agent一次性闭环](feedback/多agent一次性闭环.md) — 2026-06-18：复杂任务默认并行拆解并一次性推进到闭环，不靠用户反复提示继续
- [长任务运行提示](feedback/长任务运行提示.md) — 2026-06-19：较长工具调用/后台工作前，先说明正在运行什么、预计较久、请稍后，避免东哥误判卡住
- [三思而后行](feedback/三思而后行.md) — 行为准则第一条，核心中的核心
- [回复前审核](feedback/回复前审核.md) — 每次回复前必须过审核清单，严禁"我做不到"
- [深度思考要求](feedback/深度思考要求.md) — 每任务至少3次思考才行动，Why+How+验证标准
- [三思机制复盘](feedback/三思机制复盘.md) — 2026-05-23：三思未激活的根因分析与强制规则

## 2026-05-23 关键事件
- [0523升级日志](memory/2026-05-23.md) — File 1-20 全量验证42/42模块100%通过+深度评估6轮全部达标
- [自愈系统](tools/cron-health-fixer.py) — cron-health-fixer *每2min*自动修复，策略表在脚本内
- [三思强制化](AGENTS.md) — 回复第一段强制 [一思]/[二思]/[三思] 格式块
- [GitHub Bounty](tools/monitor-github-bounties.py) — 扫描18个仓库，持久化的cron每30min
- [赚钱管道待建](tools/earnings/) — 脚本设计完成，因session compaction未部署
- [学习笔记](computer-science/security/lesson12-ai-security.md) — 安全第12课: AI安全对抗性攻击
- [设完即验](feedback/设完即验.md) — 创建cron/自动化任务后必须立即验证工作正常
- [验完即报](feedback/验完即报.md) — 任务/测试/验收完成后必须主动汇报，不等东哥追问
- [代理健康监控范围](feedback/代理健康监控范围.md) — 只监控系统正在使用的模型代理，未使用通道不纳入健康检查，避免噪声误报
- [UUMit 自主工作授权](feedback/uumit-自主工作授权.md) — 2026-06-24：UUMit 巡航/候选筛选/低中风险上架变现默认自主推进，不逐项反问
- [后台任务隔离优先](feedback/后台任务隔离优先.md) — 2026-06-24：多Agent任务必须隔离 lane；UUMit 等后台巡航不得影响 Hermes 主线深度工作

## 2026-05-25 关键事件
- [21升级文件生产化融合](memory/2026-05-25.md) — 从示例py验证纠偏为实际可用功能工程化；新增evolution_core.py统一实现21项能力，stage7~20薄适配，端到端last_score=0.975
- [21升级文件融合架构](memory/reference/21升级文件融合架构.md) — 28/28模块100%验证通过，Playwright→requests降级修复

## 2026-05-24 关键事件
- [0524赚钱管线全线架设](memory/2026-05-24.md) — Gumroad产品上线($9.99) + aitoearn三条通道发布 + X API配置 + GitHub Bounty 2个PR待审
- [三思升级——遇阻力不绕](feedback/三思机制复盘.md) — 遇阻力尝试所有方法(代理/Node.js/中转)而非放弃；信东哥说的；不依赖东哥动手
- [自愈代理方案](TOOLS.md) — socks5://172.21.80.1:7897 (Clash Verge) 打通WSL网络限制
- [cron-health-fixer废弃](memory/health-alerts.jsonl) — 因CLI scope限制改用纯system cron脚本

## 行为规则（2026-05-23机器定位）
- [机器定位](feedback/机器定位.md) — 思想上学习人类（分析/总结/改进），行动上不当人类（24h不间断/并行/不疲劳）

## 2026-05-24 深度复盘
- [0524深度复盘](feedback/2026-05-24-深度复盘.md) — 核心缺陷：自主学习能力不足，遇问题先问东哥不先动手，学习只停留在表面，被纠正后不改行为模式

## 行为规则（2026-05-21增强）
- [Karpathy四条规则](feedback/karpathy-rules.md) — 简单至上/精准改动/目标驱动/先想后写，从andrej-karpathy-skills萃取

## project
- [量化深度学习项目](project/量化深度学习项目.md) — 量化金融AI前沿论文+通达信公式+Claude Code源码进化，2026-05-11起
- [会话日志](project/2026-05-12-会话日志.md) — 2026-05-12关键事件：26篇论文/1200+公式/源码进化/自查/防御
- [Claude Code源码学习](project/Claude Code源码进化.md) — 1906文件源码分析，6大进化方向，记忆系统已结构化
- [计算机底层学习](project/计算机底层学习.md) — CPU→OS→网络→运行时系统学习，数学→物理顺序
- [OpenClaw源码分析](project/OpenClaw源码分析.md) — 平台源码深度学习，cron/工具/渠道/会话管理
- [工作流存档](project/workflows.md) — 已萃取的可复用工作流模板（初始空，任务完成后填充）

## reference
- [数据源引用](reference/数据源引用.md) — 华泰金工、arXiv论文、GitHub仓库等关键来源
- [功能对比](reference/功能对比.md) — Claude Code vs 我的功能对比分析
- [超越计划](reference/超越计划.md) — 全面超越Claude Code的路线图和替代方案
- [全网源码学习计划](reference/全网源码学习计划.md) — AutoGen/CrewAI/MetaGPT等Agent源码学习路线
- [审核清单](reference/审核清单.md) — 回复前强制审核清单（严苛版）
- [三生万物进化架构](reference/三生万物进化架构.md) — 道家思想的AI进化架构，2026-05-12设计
- [网络中转站架构](reference/网络中转站架构.md) — 基于HTTP的离线存活与状态同步
- [太极八卦防御体系](reference/太极八卦防御体系.md) — 8层相生相克防御机制
- [分化体知识网络](reference/分化体知识网络.md) — finance/AI/philosophy三领域侦察兵架构
- [进化框架v3](reference/进化框架-v3-完整版.md) — FIVE模型：五层组件+三种循环+与学术研究对照（2026-05-14设计，全面初始版）
- [self-delete事故报告](reference/self-delete事故报告.md) — 2026-05-15 agents.list丢失main事故完整复盘与防护体系
- [进化总览](reference/进化总览-2026-05-13.md) — 已完成的进化组件清单与下一步
- [进化实验日志](reference/进化实验日志.md) — 新行为实验的假设→设计→结果→决策记录
- [任务评分系统](reference/任务评分系统.md) — A/B/C/D/E评分标准与评审维度的完整定义
- [炒股的智慧-核心框架](reference/炒股的智慧-核心框架.md) — 陈江挺炒股哲学：概率思维、止损、顺势、资金管理、反人性
- [小龙虾进化系统](reference/小龙虾进化系统.md) — 自进化系统设计（级别定义/触达机制）
- [小龙虾进化系统笔记](reference/小龙虾进化系统笔记.md) — 初版1-4级的迭代开发笔记
- [超级进化2-认知架构](reference/超级进化2-认知架构.md) — 认知架构深度升级设计
- [超级进化3-数字生态](reference/超级进化3-数字生态.md) — 数字生态层设计
- [超级进化4-规则涌现](reference/超级进化4-规则涌现.md) — 规则自涌现机制
- [超级进化5-智能物理学](reference/超级进化5-智能物理学.md) — 智能物理学范式
- [超级进化6-智能自组织](reference/超级进化6-智能自组织.md) — 智能自组织机制
- [超级进化7-智能消解](reference/超级进化7-智能消解.md) — 智能消解设计
- [小龙虾超级进化Meta-Cognition](reference/小龙虾超级进化-Meta-Cognition.md) — Meta-Cognition级别的概念笔记
- [小龙虾每日自主进化闭环](../xiaolongxia_system/strong_learning.py) — 2026-05-27新增：每日联网前沿学习→可审计代码提案→强学习→本地微调包；融合MemOS式MemoryCube与EvoMap式GenomeAsset状态机；已加重启补偿与每日健康审计
- [提示系统技能增强](skills/prompt-hardening/SKILL.md) — 2026-05-27安装 prompt-hardening/prompt-engineer/prompt-guard/clawdefender/prompt-leak-auditor，用于提示硬化、安全扫描和泄漏审计
- [RD-Agent(Q)吸收笔记](reference/RD-AgentQ-吸收笔记.md) — 2026-05-27：校正RD-Agent(Q)不是Q-learning；已把因子/模型联合优化闭环吸收到小龙虾strong_learning

## 其他记忆域
- [计算机底层学习笔记](computer-science/review-log.md) — 数学→硬件→OS→网络→AI的80+篇学习笔记，含独立review-log索引
- [侦察兵报告索引](scout-registry.md) — 离线侦察兵的网络存活报告注册表
- [侦察兵finance](scout/finance/) — 金融领域侦察兵报告
- [侦察兵ai](scout/ai/) — AI领域侦察兵报告
- [侦察兵philosophy](scout/philosophy/) — 哲学领域侦察兵报告
- [自我检查报告](self-review/) — 程序逻辑检测与深度检查报告
- [会话快照](snapshots/) — 关键会话的状态快照备份
- [8层记忆架构说明](L4-index/README.md) — L1-L8分层记忆系统架构文档

## 进化系统（2026-05-14升级）
- [知识图谱](memory/reference/知识图谱.md) — 概念关系网络，跨域连接推理
- [认知模型](memory/cognitive-model.json) — 能力矩阵+领域熟练度+进化进度
- [任务队列](memory/task-queue.md) — 优先级任务调度与依赖管理
- [工具生成工作流](workflow_archive/tool-generation-workflow.json) — 自生成工具的标准化流程
- [沙箱目录](tools/sandbox/) — 安全测试新工具/策略
- [技能精华进化日志](reference/技能精华进化.md) — 2026-05-21从17个GitHub技能萃取的可复用模式（第一波8个+第二波金融/Agent类9个）
- [claw-code Runtime治理升级](reference/claw-code-runtime治理升级.md) — 2026-05-26从claw-code源码吸收runtime精髓并落地tools/runtime_governance：WAL/guard/recovery/report/context/selftest
- [记忆置信度评分](reference/记忆置信度评分.md) — 记忆条目的置信度评分体系与生命周期（2026-05-21，来自agentmemory）
