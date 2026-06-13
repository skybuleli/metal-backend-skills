# Switch Metal 工具链速查

> Phase 0（开发环境与工具链搭建）验证通过的全部工具知识。当 Agent 需要编译着色器、验证 SPIR-V、构建 Ryubing 时，直接引用此 Skill，无需重新验证。

---

## 1. 工具清单（已验证路径与版本）

### 着色器编译器

| 工具 | 路径 | 版本 | 用途 |
|------|------|------|------|
| slangc | `slangc`（PATH） | 最新 | GLSL→DXIL/SPIR-V/Metal 编译器 |
| glslangValidator | `/opt/homebrew/bin/glslangValidator` | 11.16.3.0 | GLSL→SPIR-V 编译器 |
| metal-shaderconverter | `/usr/local/bin/metal-shaderconverter` | 4.0 | DXIL→metallib 转换（Path A 核心） |
| libmetalirconverter | `/usr/local/lib/libmetalirconverter.dylib` | 4.0 | MSC 运行时库（P/Invoke 使用） |
| dxc | `dxc`（PATH） | 系统安装 | DXIL 编译器（备用/验证）。Slang 已内置 DXC |
| metal (CLT) | `/usr/bin/metal` | CLT SDK | Metal 编译器（仅 Path B/C，CLT 下可用性有限） |

### SPIR-V 工具链（全部在 `/opt/homebrew/bin/`）

| 工具 | 用途 |
|------|------|
| spirv-as | SPIR-V 汇编器 |
| spirv-dis | SPIR-V 反汇编器 |
| spirv-val | SPIR-V 验证器（出口验证必须） |
| spirv-opt | SPIR-V 优化器 |
| spirv-cross | SPIR-V→MSL 转换（Path C 核心） |
| spirv-link | SPIR-V 链接器 |

### 构建工具链

| 工具 | 路径 | 版本 | 用途 |
|------|------|------|------|
| dotnet | `dotnet`（PATH） | 10.0.101 | .NET SDK（Ryubing 构建） |
| rustc | `rustc`（PATH） | 1.95.0 | Rust 编译器 |
| cargo | `cargo`（PATH） | 1.95.0 | Rust 包管理 |
| devkitPro | `/opt/devkitpro/` | 最新 | Switch 开发工具链 |
| xcodebuild | `xcodebuild`（PATH） | CLT only | 仅有 CLT，无 Xcode.app |

---

## 2. 三条着色器路径（命令速查）

### Path A — 主路径（Slang→DXIL→MSC→metallib）✅ 完全可用

```bash
# 步骤 1: Slang 源码 → DXIL（必须加 -profile sm_6_0）
slangc input.slang -target dxil -entry main -stage vertex -profile sm_6_0 -o output.dxil

# 步骤 2: DXIL → metallib
metal-shaderconverter output.dxil -o output.metallib
```

### Path C — SPIR-V 桥接（glslangValidator→SPIR-V→SPIRV-Cross→MSL）✅ 完全可用

```bash
glslangValidator -V input.glsl -o output.spv
spirv-val output.spv                # 必须验证
spirv-opt -O output.spv -o opt.spv  # 可选优化
spirv-cross output.spv --msl --msl-version 30000 --output output.msl
```

### Path B — Slang→MSL→metallib ❌ 暂不可用

需要 `xcrun metal`（仅在完整 Xcode 中包含）。当前不是阻塞问题。

---

## 3. DXC 版本说明（2026-06）

- Slang 内置 DXC，升级 slangc 即可获得最新 DXC
- Slang 项目已合并 DXC 升级：v1.10.2605.24（#11348）
- macOS DXC 源码编译已修复（#11461, #11489, Apple Clang 21+/Xcode 26+ 兼容）
- 系统 DXC 可通过 `SLANG_USE_SYSTEM_DXC` 选项使用（#11448，开放中）

---

## 4. 已知陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|----------|
| slangc DXIL 不生成输出 | 无输出文件 | 必须加 `-profile sm_6_0` |
| MSC CLT 环境 | Apple 说需 Xcode 15+ | ✅ 实测 CLT SDK 足够 |
| 路径 B/C 不可用 | `xcrun: error` | 仅使用 Path A |
| Ryubing 构建目录 | 输出不在 osx-arm64 子目录 | 不带 `-r` 时无 RID 子目录 |
| dxmt 仓库 | 多个同名仓库 | 用 `3Shain/dxmt`（v0.80）非骨架版 |
| MTL4Compiler 多实例 | 并发崩溃 | 每设备仅维护一个编译器实例（kk 已验证） |
| MSL 4.0 M1/M2 超时 | float16 操作超时 | 使用 MTLLanguageVersion3_2（kk 已验证） |
| MSC Wave→SIMD 转换 | 转换质量待验证 | 对照 kk 的子群限制清单验证 |

---

## 5. 参考仓库

| 仓库 | 本地路径 | 用途 |
|------|----------|------|
| Ryubing | `~/dev/ryubing/` | Switch 模拟器 C# 源码 |
| dxmt | `~/dev/dxmt/` | 3Shain/dxmt v0.80 DirectX→Metal 翻译层 |
| mesa (kk) | `mesa/mesa` → `src/kosmickrisp/` | Mesa Vulkan→Metal 驱动（Metal bridge 参考） |
| WickedEngine | `turanszkij/WickedEngine` | 多平台引擎（Metal 渲染架构参考） |

---

## 6. 环境约束

- 设备：M1 Mac，8GB RAM，256GB SSD，macOS 26.4.1
- 仅安装 Xcode Command Line Tools，无 Xcode.app
- Path A 端到端已验证：slangc→DXIL→MSC→metallib
- Path B/C 需要完整 Xcode，暂不可用（非阻塞）
- MSC 4.0 在 CLT SDK 下完全可用（已验证）
- MTL4Compiler 在 macOS 26.4.1 上可用，推荐 langVersion=3.2