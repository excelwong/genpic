# genpic — ComfyUI 图片生成 Skill

调用本机 ComfyUI 服务生成图片的脚本技能，供 Agent 在用户要求
「生成图片 / 画一个 xxx / genpic」时调用。

## 用法

```bash
python script.py [提示词]
```

- 提供提示词：完整透传为生成参数
- 不提供提示词：按 `config.json` 中的元素库随机组装
- 默认每次生成 1 张，除非明确指定数量

## 配置

`config.json`：

- ComfyUI 服务地址（当前 `192.168.50.50:8188`）
- 随机提示词元素库（发型、发色、服装、场景等）

## 文件

| 文件 | 说明 |
|---|---|
| `script.py` | 生成脚本（提交任务 → 轮询 → 下载成品） |
| `SKILL.md` | Agent Skill 定义（触发词、执行步骤、输出格式） |
| `run_loop.bat` | 循环运行入口 |
| `config.json` | 服务地址与提示词元素库 |
