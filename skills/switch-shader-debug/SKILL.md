---
name: switch-shader-debug
description: 着色器编译错误排查 — SPIR-V、Slang、DXIL、MSC 编译失败诊断
---

# Switch Metal 着色器调试

> SPIR-V / Slang / DXIL / MSC 着色器编译调试。当编译错误排查时引用。

---

## Outcome Contract

- **目标**：快速定位着色器编译错误的阶段和原因（Slang？MSC？SPIR-V？）。
- **完成标准**：确定错误发生在哪一步、给出修复建议或明确指出上游限制。
- **证据**：编译器错误输出、SPIR-V 验证结果、中间文件大小对比。

---

## 分阶段排查

着色器编译涉及多步，出问题时先确定**哪一步崩了**：

```
Slang源代码 → (1) slangc → (2) DXIL → (3) MSC → (4) metallib
                        ↘ SPIR-V → spirv-val → spirv-cross → MSL
```

**快速定位**：
- 步骤 1 失败 → Slang 语法/目标问题
- 步骤 2 无输出 → 检查 `-profile sm_6_0`
- 步骤 3 失败 → MSC 版本/兼容性（常见：DXIL 版本过高）
- 步骤 4 文件极小 → metallib 无效，回溯步骤 3
- spirv-val 报错 → SPIR-V 语义问题

---

## 常见错误速查

| 错误 | 原因 | 修复 |
|------|------|------|
| slangc 无输出 | 缺少 `-profile sm_6_0` | `slangc ... -profile sm_6_0` |
| slangc "unknown target" | 目标名错误 | `slangc -targets` 查：`dxil`/`spirv`/`metal` |
| MSC "unsupported DXIL version" | DXIL 版本过高 | 尝试更低 shader model |
| spirv-cross "MSL requires buffer block" | 缺少 BufferBlock 装饰 | 加 `--msl-decoration-binding` |
| glslangValidator "syntax error" | GLSL 语法不兼容 | 检查 Maxwell 兼容子集 GLSL 460 |
| DXIL > 0 但 metallib = 0 | MSC 静默失败 | 检查 DXIL 有效性（`dxil-dis`） |
| GLSL→DXIL 报 E36107 | std140 UBO 语义不兼容 | 改用 Slang 原生语法（`ConstantBuffer<T>`） |

---

## Gotchas（真实踩坑记录）

| 踩过的坑 | 教训 |
|---------|------|
| GLSL→slangc DXIL 报 E36107，以为是 MSC 问题 | 根因在 Slang 层：std140 UBO 无法映射到 DXIL SM6.0。改为 Slang 原生语法解决 |
| `metal-shaderconverter` 无输出也不报错 | MSC 对部分 DXIL 特性静默失败。始终检查输出文件大小 |
| spirv-val 通过但 spirv-cross 输出空 MSL | val 只检查格式，不检查内容。始终检查 spirv-cross 输出 |
| slangc 的 `SV_IsHelperInvocation` 不被 DXIL 支持 | 已知远期限制，记录在 workaround flag `METAL_WA_HELPER_INVOCATION` |
| 写死 `-profile sm_6_0` 后忘记验证 metallib 大小 | 加入健康检查：metallib 必须 > DXIL |
| SPIR-V 反汇编看起来正确但 MSC 不认 | DXIL 和 SPIR-V 的语义差异不可见。以 MSC 实际输出为准 |

---

## 验证命令速查

```bash
# Path A 逐步验证
slangc input.slang -target dxil -profile sm_6_0 -o out.dxil
ls -l out.dxil                          # > 0B ?
metal-shaderconverter out.dxil -o out.metallib
ls -l out.metallib                      # > out.dxil ?

# SPIR-V 验证
spirv-val out.spv
spirv-dis out.spv -o out.spvasm         # 反汇编检查
spirv-cross out.spv --msl --output out.msl

# 查看 metallib 是否有效（C++ 中验证）
# MTL::Device::newLibrary(metallib_data, &error)
```

---

## 关联 Skills

| Skill | 何时用 |
|-------|--------|
| `switch-metal-debug` | GPU 运行时崩溃、渲染花屏（不是编译错误） |
| `switch-metal-toolchain` | 工具路径与完整编译命令 |
| `switch-metal-backend` | 项目全景与技术路线 |
