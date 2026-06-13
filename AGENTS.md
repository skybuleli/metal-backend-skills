# Metal Backend Skills — AGENTS.md

    > 通用 Agent 入口文件。所有兼容 Claude Code / Codex / OpenCode / Pi 的 AI 编程 Agent 通过此文件获取 Metal 后端开发能力。

    ## 项目背景

    为 Ryubing（Switch 模拟器）开发原生 Metal 图形后端。技术路线：Slang 原生语法 → DXIL → metal-shaderconverter → metallib。

    各项能力的详细内容在 `skills/<name>/SKILL.md` 中。Agent 应按需读取，而不是一次性全部加载。

    ## 技能索引

    需要以下能力时，读取对应的 SKILL.md：

    | 场景 | 读取 |
    |------|------|
    | 想了解项目全景、进度、技术路线、工作约定 | `skills/switch-metal-backend/SKILL.md` |
    | 需要工具链路径、编译命令、环境约束 | `skills/switch-metal-toolchain/SKILL.md` |
    | 需要 metal-cpp API 使用模式 | `skills/switch-metal-api/SKILL.md` |
    | GPU 崩溃、渲染花屏、性能问题调试 | `skills/switch-metal-debug/SKILL.md` |
    | 着色器编译失败、SPIR-V/MSC 错误 | `skills/switch-shader-debug/SKILL.md` |
    | 需要 Ryubing GAL 接口签名 | `skills/switch-ryubing-gal/SKILL.md` |
    | Metal 4 新特性参考 | `skills/metal4-api/SKILL.md` |
    