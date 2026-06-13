# Metal Backend Skills

> Switch Metal 后端开发技能包 — 支持 Claude Code / Codex / OpenCode / Pi 等主流 AI 编程 Agent。

## 安装

### Claude Code
```bash
npx skills add skybuleli/metal-backend-skills -a claude-code -g -y
```

### Codex CLI
```bash
npx skills add skybuleli/metal-backend-skills -a codex -g -y
```

### Codex 桌面版

> CLI 与桌面版的技能存储独立，CLI 安装的技能不会自动同步到桌面版。

```bash
# 克隆仓库
git clone https://github.com/skybuleli/metal-backend-skills.git ~/MetalBackend/metal-backend-skills/
```

配置方式任选其一：

**方式一：全局 AGENTS.md（推荐）**
将 AGENTS.md 合并到 Codex 桌面版全局指令文件，每次启动自动加载：
```bash
cat ~/MetalBackend/metal-backend-skills/AGENTS.md >> ~/.codex/AGENTS.md
```

**方式二：项目级引用**
在项目根目录放置 AGENTS.md：
```bash
cd /your/project
cp ~/MetalBackend/metal-backend-skills/AGENTS.md ./
```

**方式三：全局技能目录**
将技能文件夹复制到 Codex 桌面版全局技能目录：
```bash
mkdir -p ~/.codex/skills/
cp -r ~/MetalBackend/metal-backend-skills/skills/* ~/.codex/skills/
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
