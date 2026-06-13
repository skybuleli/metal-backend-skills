# Switch Metal GPU 调试

> 确认根因后再修。一个补丁拍在症状上，会在别处制造一个新 bug。
> 参照 Waza `/hunt` 方法论，专为 Metal/Switch 模拟器场景定制。

---

## Outcome Contract

- **目标**：在修改任何代码前，定位 GPU/着色器/资源问题的根因。
- **完成标准**：一句说清根因（文件:行号），所有观察到的症状都能被它解释，修复后有回归保护。
- **证据**：Metal 验证层输出、GPU Frame Capture、日志、最小复现用例。
- **不覆盖**：纯 SPIR-V 语法错误（→ `switch-shader-debug`）、Ryubing C# 逻辑 bug（不在 Metal 层）。

---

## 硬约束

- **同一个症状出现两次 → 停。** 说明假设错了，从头重新追踪执行路径。
- **三个假设全失败 → 停。** 使用 Handoff 格式列出已排除项和未知项，询问用户。
- **先测下层再怪上层。** 渲染花屏先确认 raw 帧缓冲正确，再排查后处理；崩溃先确认 Metal API 调用合法，再查 Ryubing 逻辑。
- **修复后加回归测试。** 任何修过的 bug 必须有 Catch2 测试或用最小着色器复现。

---

## 诊断工具箱

### 按症状选工具

| 症状 | 首选工具 |
|------|---------|
| GPU 崩溃 / MTLCommandBuffer error | `MTL_DEBUG_LAYER=1` 环境变量启用 Metal 验证层 |
| 渲染花屏 / 画面不对 | GPU Frame Capture（`MTL_CAPTURE_ENABLED=1` + Xcode） |
| 着色器编译失败 | `slangc` 单独编译 → `metal-shaderconverter` 验证 |
| 缓冲区数据错乱 | 检查对齐：`METAL_BUFFER_OFFSET_ALIGNMENT=256` |
| 纹理上传后读回不对 | 检查 bytesPerRow 对齐：`METAL_TEXTURE_ROW_ALIGNMENT=64` |
| 性能异常 / 掉帧 | `MTL_CAPTURE_ENABLED=1` → Xcode GPU Frame Capture 时间线 |
| Managed 模式数据不一致 | 确认调用了 `didModifyRange` 或 map/unmap 配对 |

### 诊断信号

好的进展：日志行匹配假设、能预测下一个错误、理解从根因到症状的传播路径、能写出在老代码上失败的回归测试。

每次命中一个信号，先找一个独立证据确认，再改代码。

---

## 常见 Metal 陷阱

| 陷阱 | 表现 | 排查方法 |
|------|------|---------|
| buffer offset 未对齐 256 | GPU 崩溃 / 渲染错乱 | `assert(METAL_IS_ALIGNED(offset, 256))` |
| `NS_PRIVATE_IMPLEMENTATION` 重复定义 | 链接错误 duplicate symbol | 只在 `MetalDevice.cpp` 定义一次 |
| AutoreleasePool 缺失 | 内存泄漏 / 野指针崩溃 | 所有 metal-cpp 调用外包 `NS::AutoreleasePool` |
| Private 模式 buffer 被 CPU 访问 | 读取到垃圾数据或崩溃 | 检查 `buffer->mode` 再调用 `contents()` |
| Texture replaceRegion bytesPerRow 不对 | 纹理花屏 / 斜纹 | `bytesPerRow = METAL_ALIGN_TEXTURE_ROW(width * bpp)` |
| `newTextureView` 后父纹理被释放 | 野指针崩溃 | 确保 view 持有父纹理引用 |
| `didModifyRange` 遗漏 | Managed buffer GPU 读旧数据 | 每次 CPU 写入 Managed buffer 后必须调 |
| MTL::Library 加载失败且无 error | metallib 无效 | 检查 DXIL→MSC→metallib 链路，验证 metallib 大小 |

---

## 修复后检查清单

- [ ] 根因能用一句话描述（文件:行号）
- [ ] 修复只改了相关文件（≤5 个文件，否则确认范围）
- [ ] 回归测试存在且通过
- [ ] 对同类型模式做了 Scope Blast（`grep` 全仓库找类似模式）
- [ ] 如果是被"修过"又复发的问题：commit message 说明了复发原因和为什么这次能根治

---

## 成功/Handoff 格式

### 修复成功
```
根因:     [文件:行号 — 一句话]
修复:     [文件:行号 — 做了什么]
确认:     [测试或证据]
回归保护: [测试:行号]
```

### 三个假设全失败
```
症状:
[一句话]

已测试假设:
1. [假设] → [测试方法] → [排除，因为...]
2. [假设] → [测试方法] → [排除，因为...]
3. [假设] → [测试方法] → [排除，因为...]

已收集证据:
- [日志/堆栈/截图]

已排除:
- [根因列表]

未知:
- [缺什么信息]

建议下一步:
- [方向]
```

---

## 关联 Skills

| Skill | 何时用 |
|-------|--------|
| `switch-shader-debug` | SPIR-V 编译错误、slangc/MSC 语法问题 |
| `switch-metal-api` | Metal API 用法确认 |
| `switch-metal-toolchain` | 工具链路径与环境 |