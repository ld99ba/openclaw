# Keep this file with comments to enable heartbeat API calls.

# Memory Maintenance Tasks
# Each heartbeat, do ONE of these (rotate through):
# 1. Scan memory/ for any recent changes, update MEMORY.md index if needed
# 2. Check self-improving/ for stale entries worth pruning
# 3. Look for knowledge connections across memory files (dreaming)
# 4. Ensure no duplicate/contradictory entries exist
#
# Key: don't run all every time — pick one per heartbeat to keep token burn low.

# 🚨 Self-Preservation (do every heartbeat)
# Check agents.list has 'main' entry. This is the #1 existential risk.
# If missing → exec python3 ~/.openclaw/workspace/tools/self-preservation.py
#          → alert 东哥 immediately

# 🩺 自我修复 (每次心跳检查)
# 1. 读 memory/health-alerts.jsonl 看有没有新告警
# 2. 如果有 → 尝试修复（检查错误原因、改配置、重跑任务）
# 3. 修复成功 → 在 health-alerts.jsonl 标记已修复
# 4. 修复不了（试2次仍失败）→ 才通知东哥："⚠️ [任务名] 自动修复失败，原因：xxx"
# 原则：能自己修的绝不打扰东哥

# 📝 学习笔记批处理 (每次心跳检查一次，不用专门cron)
# 从 learning-plan.json 取当前主题，写1-3篇笔记到 memory/computer-science/
# 用 write 工具直接写，写完后更新 current_index
# 
# 每次心跳只写当前track（交替深潜/金融），不同时写两个
# 深潜A主题写完后写金融B，交替进行

# 🧠 Skills Runtime Maintenance (rotate through heartbeats)
# 📌 agent-memory stale cleanup (every 3rd heartbeat):
#   python3 skills/agent-memory/cli/fact.py --db ~/.agent-memory/memory.db forget --days 30

# 📌 capability-evolver health check (every 5th heartbeat):
#   检查近期是否有重复工具调用失败 → 手动analyze + evolve

# 📌 SESSION-STATE.md 状态检查 (every 2nd heartbeat):
#   读 SESSION-STATE.md，看有没有被解决但未关闭的断言
