---
name: switch-metal-backend
description: 项目全景与模式选择器 — 技术路线、工作约定、五大工作模式
---

# Switch Metal 后端项目全景

> 最后更新：2026-06-13
> 主仓库：`https://github.com/skybuleli/metal-backend`
> 当前分支：`codex/p3-ryubing-sync`
> 进度源：仓库内 `PROGRESS.md`（每次会话动态拉取，不写死在本 Skill）

---

## Outcome Contract

- **目标**：Agent 读取本 Skill 后直接进入工作状态，无需用户解释背景。
- **完成标准**：已从 GitHub 拉取最新 PROGRESS.md、确认工具链可用、知道从哪个模式启动。
- **不覆盖**：工具链命令（→ `switch-metal-toolchain`）、Metal API 语法（→ `switch-metal-api`）、外部参考项目细节（→ `switch-metal-reference-projects`）、着色器调试（→ `switch-shader-debug`）。

---

## Mode Picker

| 用户说什么 | 模式 | 核心流程 |
|-----------|------|---------|
| "实现 Px"、"继续开发"、"写代码" | **开发** | 拉 PROGRESS.md→定位任务→写代码+测试→提交→更新进度 |
| "审查"、"review"、"看看代码质量" | **审查** | 拉 diff→提取项目约束→对照硬指标→输出审查报告→验证命令跑过 |
| "调研"、"分析这个技术"、"能不能用" | **调研** | 收集源码+文档→消化核心技术→对照项目需求→输出采纳建议 |
| "修 bug"、"崩溃了"、"渲染不对" | **调试** | 复现→隔离→假设→确认根因→修复→回归保护 |
| "路线对不对"、"下一步做什么" | **规划** | 读 PROGRESS.md→对照技术路线→评估偏离→提出调整 |

### 歧义消解
- "帮我看看这个"：有报错 → 调试；有 diff → 审查；否则问用户
- "分析一下"：新技术 → 调研；代码质量 → 审查；bug → 调试
- 含 URL 的请求：先拉取内容 → 按内容类型分流

---

## 项目概述

- 为 Ryubing 添加原生 Metal 图形后端，替代 MoltenVK 转译层
- 当前 Phase 4（核心后端实现），总 144 任务，各阶段进度见 PROGRESS.md
- 已完成：Phase 0（工具链）、Phase 1（着色器验证）、Phase 2（渐进式 Demo，D8 1098 FPS）、Phase 3（GAL 集成、空白窗口不崩溃）
- 进行中：Phase 4.1 资源管理已完工（Device/Buffer/Texture/Sampler），下一步 P4.2 着色器编译器

---

## 关键仓库

| 仓库 | 用途 |
|------|------|
| `skybuleli/metal-backend` | 主仓库 |
| `Ryubing/Ryubing` | 上游模拟器 |
| `mesa/mesa` → `src/kosmickrisp/` | Mesa Metal 驱动（kk），Metal API 桥接参考 |
| `3Shain/dxmt` | DX→Metal 翻译层，DXBC→AIR 着色器转换 |
| `turanszkij/WickedEngine` | 多平台引擎，HLSL→Metal 管线参考 |

---

## 技术路线

| 路径 | 流程 | 地位 | 参考 |
|------|------|------|------|
| A | Slang→DXIL→MSC→metallib | ✅ **主路径** | — |
| B | Slang→DXIL→AIR→metallib | 🟡 备选 | DXMT airconv |
| C | Slang→SPIR-V→NIR→MSL→MTL4Compiler | 🔵 远期 | kk 编译器 |
| D | 手写 MSL | ✅ Phase 2 Demo | — |

**路径选择策略：**
- 首选 Path A（Apple 官方 MSC，已验证端到端可用）
- Path B 作为后备——当 MSC 转换质量不足时（如 Wave→SIMD 丢失），参考 DXMT 的 airconv 模式自建 DXIL→AIR 转换。DXMT 已证明 GS 可通过 AIR 表达
- Path C 太依赖 Mesa 生态，仅在需要极度精细的 Metal 优化时考虑

---

## 架构

```
C# (Ryujinx.Graphics.Metal)   ← IRenderer/IPipeline/Resources
    │ P/Invoke
C++ (libmetal_bridge.a)        ← C ABI: opaque handle + type tag
    │ metal-cpp 或直接 ObjC
Metal 运行时 (macOS)
```

**关键决策**：
- C ABI 采用 opaque handle + `metal_release(void*)` 统一析构
- 存储模式：UMA 用 Shared，Discrete 分 Managed/Private
- 着色器编译暂为 stub（P4.2 补齐）
- 无需 IR 中间层（slangc 已是完整编译器）
- bridge 层文件组织参考 kk 的 `bridge/` 目录（按 Metal 对象类型拆分）

---

## 外部参考项目（详见 `switch-metal-reference-projects` Skill）

三个参考项目覆盖不同技术层次，完全互补：

| 项目 | 层次 | 主要参考内容 |
|------|------|-------------|
| **Kosmickrisp (kk)** | 驱动/桥接层 | Metal API ObjC 封装、编译 workaround、buffer 绑定策略、子群/纹理降级 |
| **DXMT** | API 翻译层 | DXBC→AIR 着色器转换、GS 语义分解、D3D→Metal 状态映射 |
| **WickedEngine** | 引擎架构层 | 渲染 Pass 管理、PSO 缓存、HLSL→Metal 管线组织 |

**快速查阅：** 遇到具体 Metal 问题时读取 `switch-metal-reference-projects` 的"快速查阅表"定位到对应项目和文件。

---

## kk / DXMT 资产采纳摘要

### 已采纳
- workaround 位掩码（7 flag）、编译器 langVersion=3.2
- 硬件限制常量（`metal_limits.h`）
- 53 种像素格式映射
- MTL4Compiler 单例模式
- 三级 Buffer 绑定布局（buffer(0)=根表, buffer(1)=采样器, buffer(2)=per-draw）

### 待完善
- 子群限制编码（Wave→SIMD 转换验证）
- discard guard / helper writes 实现
- MSC 转换质量验证（对照 kk 的纹理/子群限制清单）
- DXMT airconv 模式的 Path B 备选方案评估

### Slang PR 优先采纳清单
- **P0 立即升级：** #11331 (pointer-to-pointer Metal lowering)、#11073 ([[buffer(n)]] for DescriptorHandle)
- **P1 跟踪合入：** #11578 (Metal scalar layout)、#11570 (cross-target diagnostics)、#11135 (reflection used tracking)
- **已合并待用：** #10981 (framebuffer fetch)、#10741/#11544 (mesh HLSL fixes)、#11461/#11489 (macOS DXC build)

---

## 工作约定

- 注释和 commit message **中文**
- Path A 为主路径
- C++ 仅在 `MetalDevice.cpp` 定义 `NS_PRIVATE_IMPLEMENTATION` / `MTL_PRIVATE_IMPLEMENTATION`
- metal-cpp 调用必须在 `NS::AutoreleasePool` 作用域内
- 每完成一个任务同步更新 PROGRESS.md
- 产出文件放在 `deliverables/`，证据放在 `docs/evidence/`
- 遇到 Metal 编译器怪异行为，优先检查 `switch-metal-reference-projects` 的 workaround 清单

---

## 新会话启动

```
1. 读取本 Skill
2. git clone https://github.com/skybuleli/metal-backend.git
   git checkout codex/p3-ryubing-sync
3. cat PROGRESS.md → 确认进度
4. cat NEXT_TASK.md → 定位任务
5. 参考 switch-metal-toolchain 验证工具链
6. 按 Mode Picker 选定模式 → 开始
```

启动提示词：
> "读取 Skill 'switch-metal-backend'，拉取 metal-backend 仓库 codex/p3-ryubing-sync 分支，确认 PROGRESS.md 最新状态后开始 [具体任务]"

---

## 关联 Skills

| Skill | 用途 |
|-------|------|
| `switch-metal-reference-projects` | 🆕 外部参考项目百科（DXMT/WE/kk 细节） |
| `switch-metal-toolchain` | 工具链路径与命令 |
| `switch-metal-api` | metal-cpp API 模式 |
| `switch-metal-debug` | GPU 运行时调试（Metal 验证层、Frame Capture） |
| `switch-shader-debug` | 着色器编译错误排查（Slang/DXIL/MSC/SPIR-V） |
| `switch-ryubing-gal` | Ryubing GAL 接口 |
| `metal4-api` | Metal 4 新特性 |
