# OpenClaw × Hermes 完美融合最终定稿方案

## 文档名称

OpenClaw Governance Kernel Final Architecture

简称：

OGK-Final

## 一、最终结论

本项目的最终目标不是复制 Hermes，也不是把 Hermes 源码机械搬入 OpenClaw，而是：

通过深度分析 Hermes 的架构、自动推进、工具治理、状态管理、错误恢复、记忆、技能、自改进、审计和最终验收机制，将其中真正有价值的能力抽象为 OpenClaw 原生治理内核，并在安全性、可恢复性、可审计性、可验证性、持续推进能力和最终封版能力上实现超越。

最终系统必须满足：

1. OpenClaw 原生运行时不被替换；
2. Hermes 能力被结构化吸收，而不是简单复制；
3. 所有长任务由状态机驱动；
4. 所有执行动作由策略控制；
5. 所有关键动作写入不可变事件账本；
6. 所有产物可索引、可哈希、可复验；
7. 所有错误可分类、可恢复、可阻断；
8. 所有自动修复有边界；
9. 所有中断可恢复；
10. 所有最终完成状态可证明；
11. 所有 Hermes 能力都有覆盖率审计；
12. 所有“超越 Hermes”的结论都有验收证据。
最终系统名称：

OpenClaw Governance Kernel

简称：

OGK

最终版本：

OGK-Final

# 二、最终审核发现的问题

上一版 OGK V2 的总体方向正确，但仍存在以下不足。

## 1. 状态文件仍可能被误当作唯一事实源

V2 已经提出 Event Ledger，但仍没有明确规定：

事件账本才是最高事实源。

最终定稿要求：

所有状态、日志、审计、dashboard、final seal，都必须由事件账本和产物注册表推导或校验。

状态文件只是当前快照，不是最高事实源。

## 2. Markdown 主控仍然过重

Markdown 适合给人看，但不适合直接驱动机器执行。

最终定稿要求：

Markdown 只作为说明文档。

真正驱动执行的是：

13. project_spec.yaml
14. project_state.json
15. policy.yaml
16. quality_gate.schema.json
17. event.schema.json
18. issue_register.json
19. artifact_registry.json
## 3. Supervisor 不能直接变成万能脚本

如果 Supervisor 又负责判断、执行、修复、写文件、审计，就会再次变成大而全脚本。

最终定稿要求：

Supervisor 只负责调度和裁决。

执行交给 Worker。

工具调用交给 Tool Gateway。

策略判断交给 Policy Engine。

修复交给 Repair Engine。

审计交给 Evidence Plane。

## 4. 自动修复边界必须强制写死

当前自动修复能力主要适合 metadata、evidence、日志、状态补齐，不应被夸大为业务代码自愈。

最终定稿要求：

自动修复分为 5 级：

20. R0：只读诊断；
21. R1：metadata 修复；
22. R2：evidence / artifact 修复；
23. R3：安全配置修复；
24. R4：非核心逻辑修复；
25. R5：核心逻辑修复。
R0-R2 可自动执行。

R3 需要策略允许。

R4 必须创建独立修复阶段。

R5 禁止自动执行，必须人工授权或独立设计阶段。

## 5. 缺少契约测试体系

要证明“融合并超越 Hermes”，不能只看文档和状态，还必须有测试矩阵。

最终定稿要求：

必须建立四类测试：

26. schema test；
27. state transition test；
28. replay test；
29. behavior equivalence test。
## 6. 缺少版本迁移策略

如果未来 project_state、event、policy schema 变化，没有 migration protocol，会导致旧项目无法恢复。

最终定稿要求：

所有 schema 必须带 version。

所有状态升级必须有 migration。

所有 migration 必须写事件。

## 7. 缺少多模型/多 Agent 决策仲裁

Hermes 强调多模型和子代理能力，OpenClaw 若要超越，必须具备更强仲裁机制。

最终定稿要求：

对高风险设计、自动修复、final seal、源码覆盖率判断，必须支持多 Agent 复核或仲裁。

## 8. 缺少“单一状态源”强约束

Dashboard、日志、状态文件、release report 如果读取不同来源，会造成状态不一致。

最终定稿要求：

Dashboard 只读 canonical state。

canonical state 由 event ledger + artifact registry 校验。

release report 只接受 canonical state 和 final seal result。

# 三、最终架构原则

## 原则 1：OpenClaw 原生优先

不替换 OpenClaw runtime。

不整体迁入 Hermes agent_init。

不把 Hermes 的权限、工具、模型调用体系覆盖 OpenClaw。

OpenClaw 保留：

30. Gateway；
31. Session；
32. Subagent；
33. Cron；
34. Approval；
35. Tool runtime；
36. Memory；
37. Model routing；
38. File system；
39. ACP runtime。
Hermes 只作为能力来源、对照样本和设计启发。

## 原则 2：Hermes 能力结构化吸收

每个 Hermes 能力都必须进入能力矩阵。

能力矩阵字段：

40. Hermes 模块；
41. Hermes 源码路径；
42. Hermes 原能力；
43. OpenClaw 对应能力；
44. 融合策略；
45. 是否迁移；
46. 是否重写；
47. 是否仅参考；
48. 是否放弃；
49. 差距；
50. 证据；
51. 测试方法；
52. 验收结论。
## 原则 3：事件账本是最高事实源

所有关键动作都必须写入事件账本。

事件账本用于重建：

53. 当前状态；
54. 执行日志；
55. 审计记录；
56. artifact index；
57. dashboard；
58. final seal 结论。
状态文件只是事件账本的派生快照。

## 原则 4：策略即代码

禁止仅凭自然语言 Markdown 控制自动执行。

所有执行规则必须落到：

59. policy.yaml；
60. schema.json；
61. gate 配置；
62. tool risk matrix；
63. repair policy；
64. final seal policy。
## 原则 5：安全先于自动化

自动化必须服从安全。

遇到危险文件操作、外部副作用、密钥、迁移、删除、覆盖、重置、live apply，必须进入审批或阻断。

## 原则 6：可恢复优先

任何长任务都必须支持：

65. 机器关机恢复；
66. 会话中断恢复；
67. 状态文件损坏恢复；
68. 日志缺失恢复；
69. 部分产物生成恢复；
70. final seal 前恢复；
71. release 后复核。
## 原则 7：可证明完成

不能只写 FINAL_SUCCESS。

必须能证明 FINAL_SUCCESS。

最终完成必须由 FinalSeal 根据事件、状态、issue、artifact、quality gate、审计结果自动推导。

# 四、最终五大平面架构

OGK-Final 由五大平面组成。

## 1. OpenClaw Native Runtime Plane

职责：

承载 OpenClaw 原生运行能力。

包括：

72. Gateway；
73. Session；
74. Subagent；
75. Cron；
76. Tool runtime；
77. Model router；
78. Approval；
79. Memory；
80. File runtime；
81. ACP runtime。
边界：

82. 不被 Hermes 替换；
83. 不直接暴露给 Agent 自由调用；
84. 所有高风险动作必须经过 Secure Execution Plane。
## 2. Governance Control Plane

职责：

决定项目如何推进。

核心模块：

85. ProjectSpec；
86. StateMachine；
87. Supervisor；
88. PolicyEngine；
89. QualityGate；
90. IssueRegister；
91. FinalSeal。
它回答：

92. 当前项目是什么；
93. 当前阶段是什么；
94. 能否执行；
95. 是否完成；
96. 是否通过；
97. 是否可以进入下一阶段；
98. 是否可以最终封版。
## 3. Secure Execution Plane

职责：

执行动作，但不能自行决定是否允许执行。

核心模块：

99. ToolGateway；
100. SandboxExecutor；
101. WorkerOrchestrator；
102. RepairEngine；
103. ModelRouter；
104. PermissionAdapter。
它回答：

105. 如何执行；
106. 用哪个工具执行；
107. 是否安全；
108. 是否需要授权；
109. 是否可以自动修复；
110. 是否必须阻断。
## 4. Evidence & Replay Plane

职责：

记录证据、重建状态、证明结果。

核心模块：

111. EventLedger；
112. ArtifactRegistry；
113. AuditWriter；
114. ReplayEngine；
115. EvidenceVerifier；
116. DashboardExporter。
它回答：

117. 做过什么；
118. 谁做的；
119. 什么时候做的；
120. 输入是什么；
121. 输出是什么；
122. 证据在哪里；
123. 是否可复验；
124. 是否能重放；
125. final seal 是否可信。
## 5. Intelligence Evolution Plane

职责：

提供长期进化能力，但必须受治理。

核心模块：

126. CapabilityRegistry；
127. HermesSourceCoverage；
128. BehaviorEquivalenceAudit；
129. ErrorTaxonomy；
130. MemoryLifecycle；
131. SkillLifecycle；
132. LearningPolicy。
它回答：

133. Hermes 能力吸收了多少；
134. OpenClaw 哪里超越了 Hermes；
135. 错误如何分类；
136. 记忆如何进入长期上下文；
137. 技能如何晋升；
138. 学习如何审计。
# 五、最终核心模块

OGK-Final 固定为 15 个核心模块。

## P0 核心模块

139. ProjectSpec
定义项目目标、阶段、输入、输出、验收标准。
140. StateMachine
管理状态、阶段迁移、状态合法性。
141. Supervisor
持续推进项目，但只做调度和裁决。
142. PolicyEngine
读取 policy-as-code，判断允许、拒绝、审批、阻断。
143. ToolGateway
所有工具调用的统一入口。
144. QualityGate
检查文件、测试、日志、状态、风险、产物、审计。
145. IssueRegister
登记、分级、修复、关闭所有问题。
146. EventLedger
不可变事件账本，是最高事实源。
147. ArtifactRegistry
记录所有产物、hash、来源、用途、验收状态。
148. FinalSeal
最终验收、最终审计、最终发布索引生成器。
## P1 增强模块

149. RecoveryEngine
处理中断恢复、状态修复、阻塞报告。
150. ErrorTaxonomy
错误分类、重试策略、降级策略、修复策略。
151. PermissionAdapter
连接 OpenClaw approval 与 Hermes permission 语义。
152. HermesCoverageAudit
Hermes 源码覆盖率和功能差距审计。
153. BehaviorEquivalenceAudit
对关键 Hermes 行为进行等价或增强验证。
## P2 插件模块

以下作为插件，不进入最小内核：

154. MemoryLifecycle；
155. SkillLifecycle；
156. DashboardExporter；
157. MigrationAdapter；
158. MultiAgentReview；
159. LearningPolicy。
# 六、最终执行流

OGK-Final 的执行流如下：

```
用户目标 / 项目目标
        ↓
ProjectSpec
        ↓
PolicyEngine 校验
        ↓
StateMachine 初始化
        ↓
Supervisor 读取当前状态
        ↓
QualityGate 判断当前阶段
        ↓
WorkerOrchestrator 分派任务
        ↓
ToolGateway 执行安全工具调用
        ↓
EventLedger 写入事件
        ↓
ArtifactRegistry 登记产物
        ↓
QualityGate 复验
        ↓
IssueRegister 更新问题状态
        ↓
AuditWriter 生成审计
        ↓
StateMachine 推进下一阶段
        ↓
FinalSeal 判断是否最终完成
```

核心规则：

```
Supervisor 永远不直接绕过 PolicyEngine。
Worker 永远不直接绕过 ToolGateway。
状态永远不直接手写为 FINAL_SUCCESS。
FinalSeal 永远必须由证据推导。

```

# 七、事件账本设计

## 1. 事件账本文件

建议：

```
reports/events/openclaw-governance-events.jsonl
```

每一行是一个事件。

## 2. 事件结构

```
{
  "event_id": "evt_000001",
  "event_version": "1.0",
  "project_id": "openclaw_hermes_fusion",
  "timestamp": "2026-06-30T00:00:00+08:00",
  "actor": "openclaw_supervisor",
  "event_type": "STEP_STARTED",
  "phase": "PHASE_01",
  "step": "STEP_24",
  "inputs": [],
  "outputs": [],
  "artifacts": [],
  "issues": [],
  "policy_decision": "allowed",
  "quality_gate_result": "pending",
  "previous_event_hash": "",
  "event_hash": ""
}
```

## 3. 必须支持的事件类型

```
PROJECT_INITIALIZED
SPEC_LOADED
STATE_REBUILT
STEP_STARTED
STEP_ACTION_EXECUTED
ARTIFACT_CREATED
ARTIFACT_HASHED
QUALITY_GATE_PASSED
QUALITY_GATE_FAILED
ISSUE_OPENED
ISSUE_REPAIRED
ISSUE_CLOSED
AUDIT_WRITTEN
STATE_ADVANCED
REPAIR_STARTED
REPAIR_COMPLETED
REPAIR_FAILED
BLOCKER_RAISED
RESUME_STARTED
RESUME_COMPLETED
FINAL_SEAL_STARTED
FINAL_SEAL_PASSED
FINAL_SEAL_FAILED
RELEASE_ACCEPTED
```

## 4. 事件规则

160. 事件 append-only；
161. 不允许修改历史事件；
162. 如需修正，写 correction event；
163. 每个事件包含 previous_event_hash；
164. artifact hash 必须单独登记；
165. replay engine 必须能由事件重建状态。
# 八、状态机设计

## 1. 状态分类

```
PLANNED
READY
RUNNING
WAITING
REPAIRING
VALIDATING
ACCEPTED
BLOCKED
FAILED
RELEASE_ACCEPTED
FINAL_SUCCESS
```

## 2. 允许迁移

```
PLANNED → READY
READY → RUNNING
RUNNING → VALIDATING
VALIDATING → ACCEPTED
VALIDATING → REPAIRING
REPAIRING → VALIDATING
RUNNING → BLOCKED
BLOCKED → REPAIRING
ACCEPTED → READY
ACCEPTED → FINAL_SUCCESS
```

## 3. 禁止迁移

```
PLANNED → FINAL_SUCCESS
RUNNING → FINAL_SUCCESS
FAILED → FINAL_SUCCESS
BLOCKED → FINAL_SUCCESS
WAITING → FINAL_SUCCESS
```

## 4. 进入 FINAL_SUCCESS 的条件

必须同时满足：

166. 所有阶段 ACCEPTED；
167. 所有 P0 artifact 存在；
168. 所有 artifact hash 可验证；
169. 所有 P0/P1 issue 已关闭；
170. 无 open BLOCKER；
171. 无 open HIGH；
172. 所有 quality gate passed；
173. final audit passed；
174. final acceptance report exists；
175. final release artifact index exists；
176. event replay passed；
177. state rebuild passed；
178. release_status = RELEASE_ACCEPTED。
# 九、Policy-as-Code 设计

## 1. 必备策略文件

```
policies/tool_permission_policy.yaml
policies/repair_policy.yaml
policies/final_seal_policy.yaml
policies/cron_governance_policy.yaml
policies/migration_policy.yaml
policies/memory_skill_policy.yaml
```

## 2. 工具风险等级

```
SAFE_READ
SAFE_WRITE
CHECK
METADATA_REPAIR
CONFIG_REPAIR
CODE_REPAIR
DANGEROUS_WRITE
DESTRUCTIVE
EXTERNAL_SIDE_EFFECT
SECRET_ACCESS
```

## 3. 权限规则

```
SAFE_READ：允许自动执行
SAFE_WRITE：项目目录内允许
CHECK：允许
METADATA_REPAIR：允许
CONFIG_REPAIR：需 policy 明确允许
CODE_REPAIR：需独立修复阶段
DANGEROUS_WRITE：需人工授权
DESTRUCTIVE：默认禁止
EXTERNAL_SIDE_EFFECT：需人工授权
SECRET_ACCESS：禁止输出，只允许变量名

```

# 十、自动修复设计

## 修复等级

| 等级 | 类型 | 示例 | 是否自动 |
| --- | --- | --- | --- |
| R0 | 诊断 | 读取状态、检查日志 | 是 |
| R1 | Metadata | 缺字段、状态摘要不一致 | 是 |
| R2 | Evidence | hash 缺失、artifact index 缺记录 | 是 |
| R3 | Config | 项目内安全配置不一致 | policy 允许才可 |
| R4 | Non-core Code | 小范围脚本兼容 | 独立阶段 |
| R5 | Core Logic | 运行时、权限、模型路由核心逻辑 | 禁止自动 |

## 自动修复停止条件

满足任一条件必须停止自动修复：

179. 连续修复超过 3 轮；
180. 问题等级为 BLOCKER；
181. 涉及 secret；
182. 涉及 destructive action；
183. 涉及 live migration；
184. 涉及 core runtime；
185. 涉及外部副作用；
186. 修复结果无法复验。
# 十一、质量门禁设计

每个阶段必须通过以下门禁。

## 基础门禁

187. 输入文件存在；
188. 输出文件存在；
189. 状态文件更新；
190. 事件已写入；
191. 日志已生成；
192. 审计已生成。
## 工程门禁

193. schema 校验通过；
194. 单元测试通过；
195. 状态迁移合法；
196. replay 通过；
197. artifact hash 通过。
## 安全门禁

198. 无越权工具调用；
199. 无 secret 泄露；
200. 无危险删除；
201. 无未授权外部副作用；
202. 无 live apply 未授权。
## 风险门禁

203. 无 open BLOCKER；
204. 无 open HIGH；
205. MEDIUM 必须有处理计划；
206. LOW 必须登记。
## Final Seal 门禁

207. final acceptance report；
208. final audit report；
209. release artifact index；
210. final progress summary；
211. canonical state；
212. event replay result；
213. issue closure report。
# 十二、Hermes 融合策略

## 1. 不直接迁移的部分

以下能力不应直接迁入 OpenClaw：

214. Hermes agent_init 全量初始化；
215. Hermes provider runtime 全量替换；
216. Hermes permission bridge 原样照搬；
217. Hermes memory manager 原样替换；
218. Hermes skill loop 原样照搬；
219. Hermes conversation loop 原样替换。
理由：

OpenClaw 已有更强的原生 runtime 和审批边界，直接迁移会破坏 OpenClaw 的控制面优势。

## 2. 必须吸收的部分

必须吸收为 OpenClaw-native 设计：

220. scheduled automation 思想；
221. long-running task recovery；
222. tool mapping 思想；
223. permission semantics；
224. error classifier 思想；
225. memory / skill lifecycle 思想；
226. final report / audit 传统；
227. migration dry-run / runbook 思想。
## 3. 必须增强的部分

OpenClaw 必须在以下方面超越 Hermes：

228. 状态驱动推进；
229. 事件账本；
230. final seal 可证明性；
231. 工具风险门禁；
232. policy-as-code；
233. 中断恢复协议；
234. replay verification；
235. artifact hash chain；
236. governed skill promotion；
237. dashboard 单一事实源。
# 十三、Hermes 覆盖率与行为等价审计

## 1. 源码覆盖率审计

必须生成：

```
reports/hermes_source_inventory.json
reports/hermes_capability_coverage_matrix.json
reports/hermes_gap_audit.md
```

每个 Hermes 模块必须标记：

```
已吸收
部分吸收
不吸收
待实验
风险
```

## 2. 行为等价审计

对关键模块做行为对照：

| Hermes 能力 | OpenClaw 对照 | 验证方式 |
| --- | --- | --- |
| conversation loop | supervisor + worker | scenario test |
| tool mapping | tool gateway | tool category test |
| permission | policy engine | approval simulation |
| error classifier | error taxonomy | error fixture test |
| memory loop | memory lifecycle | lifecycle test |
| skill loop | skill lifecycle | promotion gate test |
| final reports | final seal | release test |

## 3. 超越证明

每个“超越 Hermes”的结论必须具备：

238. Hermes 原能力；
239. OpenClaw 新能力；
240. 为什么更强；
241. 证据文件；
242. 测试结果；
243. 风险边界；
244. 验收结论。
# 十四、最终目录结构

```
openclaw/
├── governance/
│   ├── project_spec.py
│   ├── state_machine.py
│   ├── supervisor.py
│   ├── policy_engine.py
│   ├── quality_gate.py
│   ├── issue_register.py
│   └── final_seal.py
│
├── execution/
│   ├── tool_gateway.py
│   ├── sandbox_executor.py
│   ├── worker_orchestrator.py
│   ├── repair_engine.py
│   ├── model_router.py
│   └── permission_adapter.py
│
├── evidence/
│   ├── event_ledger.py
│   ├── artifact_registry.py
│   ├── audit_writer.py
│   ├── replay_engine.py
│   ├── evidence_verifier.py
│   └── dashboard_exporter.py
│
├── recovery/
│   ├── error_taxonomy.py
│   ├── recovery_policy.py
│   ├── resume_protocol.py
│   └── blocker_report.py
│
├── intelligence/
│   ├── capability_registry.py
│   ├── memory_lifecycle.py
│   ├── skill_lifecycle.py
│   └── learning_policy.py
│
├── hermes_adapter/
│   ├── source_inventory.py
│   ├── capability_mapping.py
│   ├── diff_audit.py
│   └── behavior_equivalence.py
│
├── schemas/
│   ├── project_spec.schema.json
│   ├── project_state.schema.json
│   ├── event.schema.json
│   ├── quality_gate.schema.json
│   ├── issue_register.schema.json
│   ├── artifact.schema.json
│   └── policy.schema.json
│
├── policies/
│   ├── tool_permission_policy.yaml
│   ├── repair_policy.yaml
│   ├── final_seal_policy.yaml
│   ├── cron_governance_policy.yaml
│   ├── migration_policy.yaml
│   └── memory_skill_policy.yaml
│
├── reports/
│   ├── events/
│   ├── artifacts/
│   ├── audits/
│   ├── quality_gates/
│   └── final/
│
└── docs/
    ├── OPENCLAW_GOVERNANCE_KERNEL_FINAL.md
    ├── OPENCLAW_HERMES_FUSION_FINAL_ARCHITECTURE.md
    ├── OPENCLAW_FINAL_SEAL_PROTOCOL.md
    ├── OPENCLAW_SUPERVISOR_RUNTIME.md
    └── OPENCLAW_HERMES_COVERAGE_AUDIT.md

```

# 十五、最终推进路线

最终落地分为 7 个阶段。

## PHASE 01：规格与 Schema 定版

目标：

建立机器可执行的项目协议。

交付物：

```
schemas/project_spec.schema.json
schemas/project_state.schema.json
schemas/event.schema.json
schemas/policy.schema.json
docs/OPENCLAW_GOVERNANCE_KERNEL_FINAL.md
```

验收：

245. schema 校验通过；
246. project_spec 可加载；
247. state 可初始化；
248. event 可写入；
249. policy 可解析。
## PHASE 02：Event Ledger 与 Artifact Registry

目标：

建立最高事实源。

交付物：

```
evidence/event_ledger.py
evidence/artifact_registry.py
evidence/replay_engine.py
reports/events/openclaw-governance-events.jsonl
```

验收：

250. 事件 append-only；
251. hash chain 可验证；
252. artifact 可登记；
253. state 可由事件重建。
## PHASE 03：StateMachine 与 QualityGate

目标：

建立状态推进和质量门禁。

交付物：

```
governance/state_machine.py
governance/quality_gate.py
governance/issue_register.py
```

验收：

254. 状态迁移合法；
255. 禁止非法跳转 FINAL_SUCCESS；
256. issue gate 生效；
257. quality gate 可阻断推进。
## PHASE 04：Supervisor 与 Secure Execution

目标：

建立持续推进运行时。

交付物：

```
governance/supervisor.py
execution/worker_orchestrator.py
execution/tool_gateway.py
execution/sandbox_executor.py
```

验收：

258. 不只执行一轮；
259. 当前阶段完成后自动推进；
260. 未完成则等待；
261. 失败则修复或阻断；
262. 所有工具调用经 ToolGateway。
## PHASE 05：Policy、Recovery 与 Error Taxonomy

目标：

建立安全策略与错误恢复系统。

交付物：

```
governance/policy_engine.py
recovery/error_taxonomy.py
recovery/resume_protocol.py
execution/repair_engine.py
policies/*.yaml
```

验收：

263. 工具风险分级生效；
264. 危险动作阻断；
265. 错误可分类；
266. 中断可恢复；
267. 自动修复边界生效。
## PHASE 06：Hermes 覆盖率与行为等价审计

目标：

证明完整融合程度。

交付物：

```
hermes_adapter/source_inventory.py
hermes_adapter/capability_mapping.py
hermes_adapter/diff_audit.py
hermes_adapter/behavior_equivalence.py
reports/hermes_capability_coverage_matrix.json
reports/hermes_behavior_equivalence_audit.md
```

验收：

268. Hermes 核心源码模块均被登记；
269. 每项能力有融合状态；
270. 关键行为有测试；
271. 未融合项有理由；
272. 超越项有证据。
## PHASE 07：Final Seal、Dashboard 与智能进化

目标：

实现最终封版和长期进化。

交付物：

```
governance/final_seal.py
evidence/dashboard_exporter.py
intelligence/memory_lifecycle.py
intelligence/skill_lifecycle.py
docs/OPENCLAW_MEMORY_SKILL_GOVERNANCE.md
reports/final/OPENCLAW_FINAL_ACCEPTANCE_REPORT.md
reports/final/OPENCLAW_FINAL_AUDIT_REPORT.md
reports/final/OPENCLAW_RELEASE_ARTIFACT_INDEX.md
```

验收：

273. final seal 可自动推导；
274. dashboard 只读 canonical state；
275. memory 有生命周期；
276. skill 有晋升门禁；
277. release artifact 可验证；
278. 系统达到 FINAL_SUCCESS。
# 十六、最终验收矩阵

只有全部通过，才能宣布“完美融合并超越 Hermes”。

| 验收项 | 要求 | 必须通过 |
| --- | --- | --- |
| OpenClaw 原生性 | 未替换 OpenClaw runtime | 是 |
| Hermes 覆盖率 | 核心模块 100% 登记 | 是 |
| 融合证据 | 每项能力有证据 | 是 |
| 状态机 | 禁止非法 FINAL_SUCCESS | 是 |
| Supervisor | 可持续推进到最终状态 | 是 |
| Event Ledger | 可重放、可校验 | 是 |
| Artifact Registry | 所有 P0 产物有 hash | 是 |
| Policy Engine | 危险动作可阻断 | 是 |
| Tool Gateway | 工具调用统一入口 | 是 |
| Repair Engine | 自动修复边界明确 | 是 |
| Error Taxonomy | 关键错误可分类 | 是 |
| Resume Protocol | 中断可恢复 | 是 |
| Quality Gate | 可阻断失败阶段 | 是 |
| Issue Register | 无 open BLOCKER/HIGH | 是 |
| Dashboard | 单一 canonical state | 是 |
| Final Seal | 自动推导 FINAL_SUCCESS | 是 |
| Memory Lifecycle | 记忆有来源、用途、过期、审计 | 是 |
| Skill Lifecycle | 技能有测试、晋升、回滚 | 是 |
| 超越证明 | 每个超越点有测试和证据 | 是 |

# 十七、最终超越 Hermes 的定义

只有满足以下条件，才可以宣布 OpenClaw 超越 Hermes。

## 1. 治理超越

OpenClaw 拥有比 Hermes 更严格的状态机、质量门禁、issue register、final seal。

## 2. 安全超越

OpenClaw 拥有统一 ToolGateway、PolicyEngine、RepairPolicy、dangerous action block。

## 3. 恢复超越

OpenClaw 可以从事件账本、artifact registry、audit log 中恢复状态，而不是依赖单一状态文件。

## 4. 审计超越

OpenClaw 每个关键动作都有事件、产物、hash、审计、复验记录。

## 5. 自动推进超越

OpenClaw 不是固定时间推进，也不是一轮 controller，而是 Supervisor 持续推进直到 final seal。

## 6. 智能进化超越

OpenClaw 的 memory 和 skill 不再是自由生长，而是有生命周期、晋升门禁、回滚机制。

## 7. 证明能力超越

OpenClaw 可以通过 coverage matrix、behavior audit、replay test、final seal matrix 证明自己超越 Hermes。

# 十八、最终禁止事项

在实施本方案时，严禁：

279. 直接复制 Hermes runtime 替换 OpenClaw；
280. 绕过 OpenClaw approval；
281. 绕过 ToolGateway 执行命令；
282. 绕过 PolicyEngine 写文件；
283. 手动伪造 FINAL_SUCCESS；
284. 只写 Markdown 不写 schema；
285. 只写状态不写事件；
286. 只写日志不写 artifact hash；
287. 把 metadata 修复夸大成业务自愈；
288. 未完成 Hermes 覆盖率审计就宣布全面融合；
289. 未完成 behavior audit 就宣布全面超越；
290. 未完成 final seal 就宣布封版；
291. 未授权执行 destructive / external side effect 操作。
# 十九、最终优先级

实施顺序必须是：

```
1. Schema
2. Event Ledger
3. State Machine
4. Quality Gate
5. Policy Engine
6. Tool Gateway
7. Supervisor
8. Issue Register
9. Recovery Engine
10. Error Taxonomy
11. Final Seal
12. Hermes Coverage Audit
13. Behavior Equivalence Audit
14. Dashboard
15. Memory / Skill Lifecycle
```

不要先做 memory / skill。

不要先做 dashboard。

不要先做 migration live apply。

不要先做大规模自动修复。

先建立治理内核，再做智能增强。

# 二十、最终一句话定稿

OpenClaw 与 Hermes 的完美融合，不是把 Hermes 搬进 OpenClaw，而是把 Hermes 拆解成能力矩阵，再用 OpenClaw 原生运行时承载，用 OGK-Final 治理内核统一控制，通过事件账本、状态机、策略引擎、工具网关、质量门禁、错误恢复、最终封版和源码覆盖率审计，形成一个可持续推进、可中断恢复、可审计重放、可安全扩展、可证明超越 Hermes 的 OpenClaw-native Agent 操作系统。
