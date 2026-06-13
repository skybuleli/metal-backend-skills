# Metal 4 API 全览

> WWDC25 发布的 Metal 4 完整技术知识。用于 Switch 模拟器 Metal 后端开发时参考，也可用于任何 Metal 4 API 使用场景。
> 知识来源：Apple Developer 官方演讲 "Discover Metal 4"、技术文档与社区分析。

---

## 1. 概述

Metal 4 是 Apple 低层级图形与计算 API 的重大更新，与旧版 Metal API **共存**于同一框架。
所有 MTL4 前缀的新类型与旧版 MTL 类型可在同一应用中混合使用。

**硬件要求**：
- Mac：M1 及更新芯片（Intel Mac 不再支持）
- iOS/iPadOS：A14 Bionic 及更新芯片
- 增强特性（Neural Accelerators、量化张量格式）：M5 Pro / M5 Max 独占

---

## 2. MTL4 命令系统

### 2.1 MTL4CommandQueue

```cpp
// 从设备获取新队列类型，与旧版 MTL::CommandQueue 共存
// 关键变化：命令缓冲区与队列解耦
NS::SharedPtr<MTL4::CommandQueue> queue = NS::TransferPtr(device->newCommandQueue4());
```

**与旧版关键区别**：
- 命令缓冲区（MTL4CommandBuffer）从 Device 直接获取，不再从 Queue 创建
- 支持从**任意线程**提交工作（work submission）
- 减少 CPU 运行时开销和内存占用
- commit 时工作立即发送到 GPU

### 2.2 MTL4CommandBuffer

```cpp
// 命令缓冲区从 Device 申请，与队列解耦
NS::SharedPtr<MTL4::CommandBuffer> cmdBuf = NS::TransferPtr(device->newCommandBuffer4());

// 支持并行编码——多个线程可同时向不同命令缓冲区编码
cmdBuf->commit();
```

### 2.3 统一命令编码器

**MTL4ComputeCommandEncoder** — 三合一：
- 合并了旧版 `MTLBlitCommandEncoder` + `MTLComputeCommandEncoder` + `MTLAccelerationStructureCommandEncoder`
- 位块传输、计算调度、加速结构构建在同一个编码器内完成

**MTL4RenderCommandEncoder** — 附件映射：
```cpp
// 逻辑着色器输出可动态映射到物理颜色附件
// Attachment Map 可在运行时切换，无需分配多个渲染编码器
encoder->setAttachmentMap(attachmentMap);
```

---

## 3. 资源管理：无绑定资源与参数表

### 3.1 设计原理

传统 Metal：每个着色器阶段有 N 个固定绑定点，场景复杂度增长时 CPU 绑定开销线性增长。
Metal 4：绑定信息移至**参数缓冲区**，整个场景只需 O(1) 次绑定。

### 3.2 MTL4ArgumentTable

```cpp
// 为编码器每个阶段指定参数表，可在阶段间共享
MTL4::ArgumentTableDescriptor* desc = MTL4::ArgumentTableDescriptor::alloc()->init();
// 描述实际需要的绑定点——在无绑定场景中可能只需一个缓冲区绑定
desc->setBindingCount(1);

NS::SharedPtr<MTL4::ArgumentTable> argTable = NS::TransferPtr(
    device->newArgumentTable4(desc)
);

// 绑定资源到参数表
argTable->setBuffer(buffer, 0, 0);

// 编码器使用参数表
encoder->useArgumentTable(argTable, MTL4::RenderStageVertex);
```

**关键优势**：
- 编码器不再为每个资源类型存储完整绑定表——只消耗实际需要的内存
- 单个参数表可跨**多个编码器**、甚至**不同命令缓冲区**复用
- 资源在多个绘制调用间共享时，避免重复绑定开销

---

## 4. 着色器编译：MTL4Compiler

### 4.1 架构变化

| | Metal 3（旧） | Metal 4（新） |
|---|---|---|
| 编译入口 | 通过 MTLDevice 提交到 OS | 独立的 MTL4Compiler |
| 控制粒度 | 隐式，系统决定时机 | 显式，应用控制时机 |
| 多线程 | 有限 | 支持**优先级调度** |
| 与设备耦合 | 紧耦合 | **解耦** |

### 4.2 使用方式

```cpp
// 从 Device 分配编译器接口（与设备分离）
NS::SharedPtr<MTL4::Compiler> compiler = NS::TransferPtr(device->newCompiler4());

// 显式控制编译时机
compiler->compile(source, options, ^(MTL4::CompiledShader* result, NSError* error) {
    // 编译完成回调
});
```

**优先级调度**：多线程同时编译时，OS 优先处理高优先级线程请求——确保应用最重要的着色器**最先被编译**。直接影响游戏加载时间和首次渲染延迟。

---

## 5. 机器学习原生集成

### 5.1 MTLTensor — 原生张量类型

Metal 4 首次将张量内建为 API 一等公民：

```cpp
// 创建 4D 张量（例如 NCHW 格式的 ML 数据）
MTL4::TensorDescriptor* tensorDesc = MTL4::TensorDescriptor::alloc()->init();
tensorDesc->setShape({1, 3, 256, 256});       // batch, channel, height, width
tensorDesc->setDataType(MTL::DataTypeFloat16);
tensorDesc->setStorageMode(MTL::StorageModePrivate);

NS::SharedPtr<MTL::Tensor> tensor = NS::TransferPtr(device->newTensor4(tensorDesc));
```

**关键特性**：
- 可扩展到**二维以上**（不受纹理 2D 限制）
- 同时集成到 **Metal 着色语言**（`metal::tensor`）
- 抽象多维索引操作——着色器代码无需手动计算偏移

```metal
// 在 Metal Shading Language 中直接操作张量
metal::tensor<float, 4> inputTensor [[buffer(0)]];
float val = inputTensor.read({batch, channel, y, x});
```

### 5.2 MachineLearningCommandEncoder

```cpp
// 直接在 Metal 命令缓冲区中执行 ML 模型
NS::SharedPtr<MTL4::MachineLearningCommandEncoder> mlEncoder =
    NS::TransferPtr(cmdBuf->newMachineLearningCommandEncoder4());

mlEncoder->executeModel(mlModel, arguments);
mlEncoder->endEncoding();
```

**设计要点**：
- 张量通过参数表映射，编码到同一 MTL4CommandBuffer
- 支持**屏障（Barriers）**与渲染/计算编码器同步——ML 推理与渲染在**同一条 GPU 时间线**上
- 兼容 Core ML 包格式——用 Metal 工具链转换后直接输入
- 无需 CPU↔GPU 往返和框架间内存拷贝

### 5.3 ShaderML — 着色器嵌入式 ML

对于小型网络（如神经 BRDF 材质），直接在着色器中集成 ML 操作：

```metal
// mpp::tensor_ops 针对 Apple Silicon 优化，编译器直接内联
#include <metal_performance_primitives>
using namespace mpp;

float4 evaluate_neural_material(tensor<float, 2> weights, float2 uv) {
    return tensor_ops::dense(weights, uv);  // 编译器内联，无编码器切换开销
}
```

**适用场景**：神经 BRDF 材质评估、ML 纹理合成、实时风格迁移后处理。

---

## 6. MetalFX：升采样、帧插值与降噪

### 6.1 Temporal Upscaler（时序升采样器）

```cpp
// 以低分辨率渲染，MetalFX 重建全分辨率
MTLFX::UpscalerDescriptor* desc = MTLFX::UpscalerDescriptor::alloc()->init();
desc->setInputSize({1280, 720});   // 低分辨率输入
desc->setOutputSize({2560, 1440}); // 全分辨率输出
desc->setMode(MTLFX::UpscalerModeTemporal);

NS::SharedPtr<MTLFX::Upscaler> upscaler = NS::TransferPtr(
    device->newUpscaler(desc)
);
```

**技术亮点**：
- 利用 **Neural Engine** + **Neural Accelerators**（M5 Pro/Max）
- 支持**动态输入尺寸**——简单帧用较高分辨率，复杂帧自动降低
- 从低分辨率输入中重建高频细节
- Apple 定位为 "production-ready"，非实验性功能

### 6.2 Frame Interpolation（帧插值）

在每两个渲染帧之间生成中间帧，提高感知帧率而不增加 GPU 渲染负担。
针对 Apple Silicon UMA 架构优化——帧间光流计算无需跨内存池传输。

### 6.3 Ray Tracing Denoising（光线追踪降噪）

在**升采样过程中直接降噪**——减少每像素光线数，ML 驱动的降噪器输出全尺寸去噪图像。
对实时路径追踪管线意义重大。

---

## 7. 分阶段迁移策略（Phased Adoption）

Metal 3 和 Metal 4 API 可**在同一应用中并存**，渐进迁移：

| 阶段 | 内容 | 风险 |
|------|------|------|
| 第一阶段 | 新功能模块使用 MTL4 编码器和参数表，现有管线不变 | 低 |
| 第二阶段 | 着色器编译迁移至 MTL4Compiler | 低 |
| 第三阶段 | 集成 MetalFX 升采样和帧插值 | 中 |
| 第四阶段 | 引入 ML 编码器实现神经渲染 | 中高 |

---

## 8. 与 DirectX 12 / Vulkan 对比

| 特性 | Metal 4 | DirectX 12 | Vulkan |
|------|---------|-----------|--------|
| 命令队列模型 | MTL4CommandQueue（与缓冲区解耦） | ID3D12CommandQueue | VkQueue |
| 资源绑定 | MTL4ArgumentTable（无绑定） | Descriptor Heaps | Descriptor Sets |
| 着色器编译 | MTL4Compiler（运行时/构建时） | dxc（构建时） | 外部编译器（构建时） |
| ML 集成 | 原生 Tensor + ML Encoder | DirectML（独立 API） | 无原生方案 |
| 超分辨率 | MetalFX Temporal Upscaler | DirectSR/DLSS | FSR（跨平台） |
| 内存架构 | 统一内存（UMA） | 分离式显存 | 取决于硬件 |

**可移植性**：Metal 4 在设计上收敛于 DX12/Vulkan 的底层范式（显式 GPU 控制、最小化 CPU 开销），方便从这些平台迁移。

---

## 9. Apple Silicon 支持矩阵

| 芯片 | 支持级别 | 特性 |
|------|----------|------|
| M1 系列 | ✅ 完整基础 | 含 MetalFX Upscaling |
| M2 系列 | ✅ 完整基础 | 增强 GPU 性能 |
| M3 系列 | ✅ 完整基础 | 硬件光追增强 |
| M4 系列 | ✅ 完整基础 | 更高 ML 吞吐 |
| M5 Pro/Max | ★ 增强 | Neural Accelerators、量化张量、MetalFX 完整加速 |
| A14 Bionic+ | ✅ 完整基础 | iOS/iPadOS 兼容 |

---

## 10. 关键注意事项

- MTL4 前缀类型可与旧 MTL 类型共存——无需一次性重写
- 在 M1 上，Shared 和 Managed 存储模式行为相同（UMA 架构）
- MTL4CommandBuffer 从 Device 获取，不是从 Queue——API 设计的关键心智模型变化
- Argument Table 大小由应用按需决定——无绑定场景中极简
- MTL4Compiler 的优先级调度对首帧延迟有**直接可测量**的影响
- MetalFX 依赖 Neural Engine 的增强特性仅在 M5 Pro/Max 可用，但基础升采样在所有 M 系列芯片上可用
- 没有完整 Xcode 的情况下：MSC（metal-shaderconverter）仍可工作，但 `xcrun metal`（Path B）不可用——与旧版工具链约束一致

---

## 11. 参考资源

| 资源 | 链接 / 路径 |
|------|------------|
| WWDC25 演讲 | https://www.youtube.com/watch?v=t18z64iecZM |
| Apple 官方文档 | https://developer.apple.com/metal/ |
| 本地工具链 Skill | `ally://skills/switch-metal-toolchain/SKILL.md` |
| 本地 API 速查 Skill | `ally://skills/switch-metal-api/SKILL.md` |
| 详细分析报告 | `ally://chats/019eb735-a5d0-73fb-b0ab-21b45f6f4c89/deliverables/metal4_deep_technical_analysis.html` |
| MetalFX 对比报告 | `ally://chats/019eb735-a5d0-73fb-b0ab-21b45f6f4c89/deliverables/metalfx_deep_comparison.html` |

---

## 12. MetalFX vs 竞品对比速查

### 12.1 升采样

| | MetalFX | DLSS 4 | FSR 4 | XeSS 2 |
|---|---|---|---|---|
| 算法 | 时序重建 + 空间混合 | AI 时序重建（Transformer） | AI 时序重建 | AI 时序重建 |
| ML 模型 | CNN + Neural Engine | Transformer | ML（RDNA4 AI） | XMX / DP4a |
| 画质排名 | 良好 | **最佳** | 良好 | 良好（XMX） |
| 跨平台 | ⛔ Apple 独占 | ⛔ NVIDIA 独占 | ✅ 跨 GPU | ✅ 跨 GPU |

### 12.2 帧生成

| | MetalFX Frame Interp. | DLSS FG | FSR 3 FG | XeSS-FG |
|---|---|---|---|---|
| 生成能力 | 每2帧→1中间帧 | 每2帧→1~3帧 (MFG) | 每2帧→1中间帧 | 每2帧→1~3帧 |
| 延迟 | ~2-3ms | +Reflex 补偿 | AFMF 较高 | +XeLL 补偿 |
| 硬件 | Apple Silicon | RTX 40+ (FG) / RTX 50+ (MFG) | 跨平台 | Arc 最优 |

### 12.3 光追降噪

| | MetalFX Denoising | DLSS Ray Reconstruction | FSR Ray Regeneration |
|---|---|---|---|
| 模型架构 | CNN | Transformer (DLSS 4) | 神经网络 (RDNA4) |
| 集成 | 嵌入 Upscaling 管线 | 独立 + 可选组合 | 独立降噪器 |
| 已知问题 | 偶见色彩偏移 | 某些纹理反射不佳 | 较粗糙 |

### 12.4 总体定位

- **Apple 生态**：MetalFX 是唯一选择，Metal 4 一站式集成 Upscale + FG + Denoise
- **极致画质**：DLSS 4 Transformer 模型领先，Ray Reconstruction 最成熟
- **跨平台覆盖**：FSR 4 开源 + 跨 GPU，覆盖最广
- **Intel 生态**：XeSS 在 Arc GPU 上接近 DLSS 体验