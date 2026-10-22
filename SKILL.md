---
name: genpic
description: "图片生成技能。用户说生成图片、genpic等时使用。支持带提示词或不带提示词运行，不带时脚本自动生成随机提示词。"
---

# 图片生成 Skill

## 功能

调用 ComfyUI 服务，服务地址在 config.json 中配置（当前：192.168.50.50:8188），并通过 QQ 发送结果。

## 什么时候用这个 Skill

- 用户要求生成图片（说"画"、"生成图片"、"genpic"、"generate picture"等）
- 用户提供提示词要求生成对应图片
- 用户没有提供提示词但要求随机生成一张图片
- 用户要求批量生成多张图片
- 用户要求"画一个xxx"、"来张图"等口语化图片生成请求

## 默认数量

**默认生成 1 张图片。** 除非用户明确指定数量（如"来3张"、"批量生成5张"），否则每次只生成 1 张。不要自作主张批量生成。

## 执行步骤

1. **调用 Python 脚本**

   执行命令（必须用 background 模式，前台最大 600s 不够）：
   ```bash
   cd /Users/excel/.openclaw/workspace/skills/genpic && python3 script.py [prompt]
   ```
   - prompt 为可选项，不提供时脚本自动生成随机 prompt
   - **如果用户提供了提示词，必须将用户的提示词完整作为命令行参数传入**，例如：`python3 script.py 用户给的提示词`
   - 必须用 background=true + notify_on_complete=true + timeout=1200
   - 如果执行超时或失败，绝对不要重试！直接返回错误信息给用户

2. **解析输出**

   - 如果输出包含 ERROR: 或脚本退出码非 0 → 提取错误信息，返回给用户
   - 如果输出包含 DONE: → 提取图片路径

3. **发送图片到 QQ**

   使用 qqimg 标签发送图片：
   ```
   <qqimg>图片本地路径</qqimg>
   ```

## 输出格式

✅ **生成成功后，必须用 qqimg 标签把图片发给用户！**

成功：
```
<qqimg>/Users/excel/Pictures/output/xxx.png</qqimg>
```

失败：
```
生成失败：错误信息
```

⚠️ 重要：图片生成完必须发！不要只输出文字结果。

⚠️ **发送图片时，必须把本次使用的 prompt 完整（一字不删）一并发给用户。不要缩短、不要精简、不要省略任何部分。** 格式示例：
```
提示词：xxx
<qqimg>/Users/excel/Pictures/output/xxx.png</qqimg>
```

## 批量生成规则

- **多张图片全部生成完成后一起发送，不要边生成边发。**
- **批量生成时，写一个临时 Python 脚本串联执行 N 次 script.py，用单个 background 进程跑完所有图片**，避免逐张 poll 消耗大量 context
- 示例批量脚本（用命令行参数控制数量，不要写死次数）：
  ```python
  import subprocess, sys
  count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
  prompt = sys.argv[2] if len(sys.argv) > 2 else None
  for i in range(count):
      print(f"=== 第{i+1}张 开始 ===")
      args = [sys.executable, "script.py"]
      if prompt:
          args.append(prompt)
      r = subprocess.run(args, capture_output=True, text=True, cwd="/Users/excel/.openclaw/workspace/skills/genpic")
      print(r.stdout)
      if r.returncode != 0:
          print(f"ERROR: {r.stderr}")
      print(f"=== 第{i+1}张 结束 ===")
  print("全部完成")
  ```
  保存为 `/tmp/batch_genpic.py`，执行示例：
  - `python3 /tmp/batch_genpic.py 3` — 随机提示词生成 3 张
  - `python3 /tmp/batch_genpic.py 5 "中文提示词"` — 指定提示词生成 5 张
  用 `background=true + notify_on_complete=true` 执行
- 全部完成后解析输出，汇总发送所有图片

## 使用规则

- **提示词语言**：用户给的中文提示词保持中文原文，不要翻译成英文。需要扩写时也用中文扩写。
- **批量生成时，全部完成后再一起发送**，不要边生成边发。逐张后台执行，每张完成后自动触发下一张，最后统一用 `<qqimg>` 发送所有图片
- **每张图附带提示词**，格式见上方输出格式

## 注意事项

- 图片路径是本地路径，需要确保路径正确
- ComfyUI 服务地址在 config.json 中配置（当前：192.168.50.50:8188）
- **exec 命令必须用 background 模式 + timeout=1200**
- **🚨 重要：如果 ComfyUI 服务超时、失败或进程被终止，绝对不要重试！重试会导致重复调用服务。直接输出错误信息给用户即可。**
- 图片生成通常需要 7-10 分钟，请耐心等待完成

## 定时任务配置（cronjob）

通过 cronjob 工具调度 genpic 时，prompt 必须明确指导子 agent **等待后台进程完成**，否则会 fire-and-forget、立即结束任务。关键写法：

1. `terminal` 必须用 `background=true, timeout=1200, notify_on_complete=true`
2. prompt 里必须写明用 `process(action='wait', session_id=上一步返回的id, timeout=1200)` 等待图片生成完成
3. 然后再解析输出、发送图片

示例 prompt 片段：
```
步骤2: 用 terminal 执行 cd /Users/excel/.openclaw/workspace/skills/genpic && python3 script.py [prompt]（如果有用户提示词则传入，否则不传参数）
参数必须设 background=true, timeout=1200, notify_on_complete=true

步骤3: 用 process(action='poll', session_id=上一步返回的session_id, timeout=600000) 等待图片生成完成
```

⚠️ 如果 prompt 里只写 `background=true` 而没有 `process(action='wait')`，子 agent 会认为命令已提交就结束任务，图片不会发送。

⚠️ 用 cronjob 的 `update` 操作会导致 `repeat` 计数器被重置为当前已执行次数（如 1/117），后续不会再执行。需要重新创建任务而非 update。

## Cron 定时任务发图

⚠️ **cron delivery 不支持 `<qqimg>` 标签！** 必须用 `MEDIA:` 语法。

- `<qqimg>` 只在主聊天（gateway 直接回复）中生效
- cron delivery 走的是 `scheduler.py` 的 `_deliver_result()`，里面有 `extract_media()` 处理 `MEDIA:` 标签
- cron 子进程**没有 `send_message` 工具**，不能用 send_message 发图

**cron 正确做法（2026-05-12 确认）：**
1. 将生成的图片复制到 `~/.openclaw/media/qqbot/genpic_latest.png`（固定文件名，每次覆盖）
2. 在最终回复中使用 `MEDIA:~/.openclaw/media/qqbot/genpic_latest.png`
3. cron delivery 通过 `extract_media()` 自动提取并作为原生附件发送到 QQ Bot

**cron prompt 发图模板：**
```
步骤3: cp [图片路径] ~/.openclaw/media/qqbot/genpic_latest.png
步骤4: 你的最终回复只包含以下内容，不要加多余文字：
提示词：[完整提示词]
MEDIA:~/.openclaw/media/qqbot/genpic_latest.png
```

## 手动执行发图（非 cron 场景）

⚠️ **手动执行时不要在回复中包含 `MEDIA:` 前缀！** gateway 看到 `MEDIA:` 会尝试自动投递，导致重复报错。

**核心规则（2026-06-24 岛主确认）：**
**岛主提交 genpic 指令后，启动后台生成，10 分钟后只检查一次输出。如果图片已生成就通过 QQ 发给我，没有生成就放弃。**

**正确流程：**
1. 用 background=true, timeout=1200 执行 `cd /Users/excel/.openclaw/workspace/skills/genpic && python3 script.py [用户提示词]`（有提示词就传，没有就不传）
2. 保存 session_id，然后**直接等待约 10 分钟**，不做任何 poll
3. 10 分钟后用 process(action='poll', session_id=保存的id, timeout=60000) **只 poll 一次**检查输出
   - 输出包含 DONE: → 提取图片路径，复制图片到 `~/.openclaw/media/qqbot/genpic_latest.png`，用 `message(action=send, channel=qqbot, target=qqbot:c2c:EB8929C892E9276C7D39162826C34C5B, media=~/.openclaw/media/qqbot/genpic_latest.png)` 发送图片
   - 输出为空或进程仍在 running → 不发送，结束任务
4. 回复中只写提示词文字，**不要写** `MEDIA:` 前缀

示例回复：
```
提示词：[完整提示词]
```

## 已知问题

- **文件名覆盖风险**：脚本用递增计数器命名（如 `openclaw_00035_.png`），但如果计数器重置或重复，会覆盖同名文件
- **无需提示词**：用户没指定提示词时直接运行，脚本会自动生成随机提示词，不要追问
- **批量生成必须全部完成后再一起发送**，不要边生成边发
- **cron repeat 计数器可能有 bug**：设 117 次可能只跑 1 次就停（显示 repeat: 1/117），需观察

## Cron 定时任务生成图片

当用户要求定时执行 genpic 时，必须注意：

### 1. Cron delivery 不支持 `<qqimg>` 标签

Cron 的 delivery 系统走独立的投递路径，**不解析 `<qqimg>` 标签**。图片会变成纯文本发出。

**正确做法**：在 cron prompt 的最终回复中使用 `MEDIA:` 语法：
``` 
提示词：[完整提示词]
MEDIA:/Users/excel/Pictures/output/openclaw_XXXXX_.png
```
Cron scheduler 会通过 `BasePlatformAdapter.extract_media()` 自动提取 `MEDIA:` 标签并作为原生附件发送。

### 2. Cron schedule 必须用 cron 表达式，不要用 `once in Nm`

- ❌ `schedule: "once in 20m"` + `repeat: 117` → 跑 1 次就 completed，不会重复
- ✅ `schedule: "*/20 * * * *"` + `repeat: 117` → 正确每 20 分钟重复执行

### 3. Cron 子进程没有 `send_message` 工具

不要在 cron prompt 里要求使用 `send_message`，子 agent 不具备该工具。

## Pitfalls（常见错误）

> ⚠️ 使用此 skill 时最常见的错误

1. **ComfyUI 服务不可用**
   - 症状：脚本超时或报 `Connection refused` / `timeout` 错误
   - ⚠️ **静默挂起**：ComfyUI 不通时脚本可能**完全没有 stdout 输出**（不是报错，而是卡住无响应），background 进程一直 running 但 output 为空。这种情况下等待 2-3 分钟后如果仍无输出，即可判定服务不可用，kill 进程并告知用户
   - 原因：ComfyUI 服务（192.168.50.50:8188）未启动、崩溃或网络不通
   - 解法：服务不可用时直接告知用户，**绝对不要重试**
   - 注意：安全扫描器会拦截对 `192.168.50.50` 的 curl/python 直接调用（raw IP + private network alert），不要用这些方式探测服务状态，只能通过脚本本身的输出来判断

2. **输出目录不存在导致生成失败**
   - 症状：脚本执行完成但找不到图片文件，或报 `FileNotFoundError`
   - 原因：`/Users/excel/Pictures/output/` 目录被删除或未创建
   - 解法：执行前确保目录存在：`mkdir -p /Users/excel/Pictures/output/`

3. **文件名序号重复导致覆盖**
   - 症状：生成的图片路径指向已存在的文件，旧图被新图覆盖
   - 原因：计数器重置或并发执行导致 `openclaw_XXXXX_.png` 命名冲突
   - 解法：批量生成时用单进程串行执行（参见批量生成规则），生成后确认文件时间戳与当前时间一致

4. **未使用 background 模式导致超时**
   - 症状：前台执行 600s 后被强制终止，图片生成未完成
   - 原因：图片生成通常需要 7-10 分钟，前台最大 600s 不够
   - 解法：必须使用 `background=true + notify_on_complete=true + timeout=1200` 执行

5. **生成成功但忘记发送图片**
   - 症状：只输出了文字描述，用户没收到图片
   - 原因：解析输出时忽略了 `DONE:` 行中的路径，或未用 `<qqimg>` 标签
   - 解法：检查输出中的 `DONE:` 行，提取路径后必须用 `<qqimg>` 标签发送

6. **config.json 包含注释导致批量生成失败**
   - 症状：`json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes`，第1张可能成功但后续全部报错
   - 原因：config.json 中有 `//注释`（如 `"width": 1536, //1536`），Python 3.8 的 `json.load` 不支持 JSON 注释
   - 解法：确保 config.json 中无任何注释，所有值必须是合法 JSON 格式。已修复，如再出现需检查是否被其他程序改回



7. **过早判断服务挂了（最常见误判）**
   - 症状：agent 在 4-5 分钟内频繁 poll，发现输出为空就判定 ComfyUI 服务不可用
   - 原因：ComfyUI 在服务端渲染，脚本只在最终完成时才打印结果，中间无任何 stdout 输出。这是**正常行为**，不是服务挂了
   - 解法：**10 分钟内不应判断服务异常**。启动后台进程后至少等 7 分钟再第一次 poll，不要每 2-3 秒 poll 一次浪费 context。只有超过 12 分钟仍无输出才怀疑服务问题
   - ⚠️ 不要频繁 poll！每次 poll 消耗 context，7-10 分钟的过程应该耐心等待，不是反复查看

## 验证

- [ ] **单张生成闭环**：运行 `python3 script.py "a cute cat"` 使用 background 模式，输出包含 `DONE:` 行和有效图片路径，图片文件存在且可打开。
- [ ] **图片发送到 QQ**：生成成功后使用 `<qqimg>` 标签发送图片路径，用户在 QQ 中收到图片。
- [ ] **无提示词模式**：不传 prompt 直接运行 `python3 script.py`，脚本自动生成随机提示词并成功产出图片。
- [ ] **ComfyUI 不可用时优雅降级**：ComfyUI 服务关闭时执行脚本，返回 `ERROR:` 信息，agent 直接告知用户而非重试。