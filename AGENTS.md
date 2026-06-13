# Metal Backend Skills — AGENTS.md

> 通用 Agent 入口文件。所有兼容 Claude Code / Codex / OpenCode / Pi 的 AI 编程 Agent 通过此文件获取 Metal 后端开发能力。

## 项目背景

为 Ryubing（Switch 模拟器）开发原生 Metal 图形后端。技术路线：Slang 原生语法 → DXIL → metal-shaderconverter → metallib。

各项能力的详细内容在 `skills/<name>/SKILL.md` 中。Agent 应按需读取，而不是一次性全部加载。

## 触发规则

> **核心原则：Agent 在检测到以下触发条件时，必须自动读取对应的 SKILL.md。**
> 用户也可通过 `@技能标识` 显式调用。

| 触发条件 | 显式调用 | 读取文件 |
|----------|----------|----------|
| 提到 **项目全景 / 技术路线 / 工作约定 / 模式选择 / 开发模式 / 审查模式 / 调研模式 / 调试模式 / 规划模式** | `@metal-backend` | `skills/switch-metal-backend/SKILL.md` |
| 提到 **工具链 / slangc / metal-shaderconverter / spirv-cross / dxc / glslangValidator / 编译命令 / 环境变量** | `@toolchain` | `skills/switch-metal-toolchain/SKILL.md` |
| 提到 **metal-cpp / MTLDevice / MTLCommandQueue / MTLBuffer / MTLTexture / MTLRenderPipeline** | `@metal-api` | `skills/switch-metal-api/SKILL.md` |
| 提到 **GPU 崩溃 / 渲染花屏 / GPU 调试 / 性能问题 / GPU hang / Metal 调试** | `@metal-debug` | `skills/switch-metal-debug/SKILL.md` |
| 提到 **着色器编译失败 / SPIR-V 错误 / MSC 错误 / shader 错误 / 编译失败** | `@shader-debug` | `skills/switch-shader-debug/SKILL.md` |
| 提到 **Ryubing / GAL 接口 / 图形抽象层** | `@ryubing-gal` | `skills/switch-ryubing-gal/SKILL.md` |
| 提到 **Metal 4 / 新特性** | `@metal4` | `skills/metal4-api/SKILL.md` |

### 使用示例

```
用户: "slangc 编译报错了，帮我看看"
Agent: [检测到 "slangc" → 自动读取 skills/switch-metal-toolchain/SKILL.md]
       [检测到 "编译报错" → 自动读取 skills/switch-shader-debug/SKILL.md]

用户: "@metal-debug 渲染花屏了"
Agent: [显式调用 → 自动读取 skills/switch-metal-debug/SKILL.md]
```
