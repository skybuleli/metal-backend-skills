# Metal Backend Skills

> Switch Metal 后端开发技能包 — 支持 Claude Code / Codex / OpenCode / Pi 等主流 AI 编程 Agent。

## 安装

### Claude Code
```bash
npx skills add skybuleli/metal-backend-skills -a claude-code -g -y
```

### Codex
```bash
npx skills add skybuleli/metal-backend-skills -a codex -g -y
```

### OpenCode
```bash
npx skills add skybuleli/metal-backend-skills -a opencode -g -y
```

### Pi
```bash
pi install npm:@skybuleli/metal-backend-skills
```

### 其他 Agent
```bash
git clone https://github.com/skybuleli/metal-backend-skills.git ~/.metal-skills/
# 将 Agent 指令文件指向 ~/.metal-skills/AGENTS.md
```

## 包含的技能

| 技能 | 用途 |
|------|------|
| `switch-metal-backend` | 项目全景与模式选择器 |
| `switch-metal-toolchain` | 工具链路径与命令 |
| `switch-metal-api` | metal-cpp API 模式 |
| `switch-metal-debug` | GPU 运行时调试 |
| `switch-shader-debug` | 着色器编译错误排查 |
| `switch-ryubing-gal` | Ryubing GAL 接口 |
| `metal4-api` | Metal 4 新特性 |

## 更新

```bash
npx skills update -g -y
```

## 许可

MIT
