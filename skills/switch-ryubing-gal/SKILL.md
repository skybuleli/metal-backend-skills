---
name: switch-ryubing-gal
description: Ryubing GAL 接口参考 — 图形抽象层接口签名与调用约定
---

# Ryubing GAL 接口速查

> Ryubing 图形抽象层（Graphics Abstraction Layer）接口参考。Phase 3 实现 MetalRenderer/MetalPipeline 时直接引用。

---

## 1. GAL 抽象层结构

```
src/Ryujinx.Graphics.GAL/
├── IPipeline.cs        ← 所有渲染命令接口（核心）
├── IRenderer.cs        ← 渲染器生命周期管理
├── IProgram.cs         ← 着色器程序
├── ITexture.cs         ← 纹理接口
├── ISampler.cs         ← 采样器接口
├── BufferHandle.cs     ← 缓冲区句柄
└── (枚举/结构体)       ← 颜色格式、混合模式、比较操作等
```

## 2. IPipeline 方法分组

### 绘制命令
- `Draw(vertexCount, instanceCount, firstVertex, firstInstance)`
- `DrawIndexed(indexCount, instanceCount, firstIndex, firstVertex, firstInstance)`
- `DrawIndirect(BufferRange)`, `DrawIndexedIndirect(BufferRange)`
- `DrawTexture(ITexture, ISampler, srcRegion, dstRegion)`
- `DispatchCompute(groupsX, groupsY, groupsZ)`

### 清除命令
- `ClearBuffer(BufferHandle, offset, size, value)`
- `ClearRenderTargetColor(index, layer, layerCount, componentMask, color)`
- `ClearRenderTargetDepthStencil(layer, layerCount, depthValue, depthMask, stencilValue, stencilMask)`

### 管线状态
- `SetProgram(IProgram)` — 设置着色器程序（Metal: → setRenderPipelineState）
- `SetRenderTargets(Span<ITexture> colors, ITexture depthStencil)` — 设置渲染目标
- `SetViewports(ReadOnlySpan<Viewport>)`, `SetScissors(ReadOnlySpan<Rectangle>)`

### 混合与深度
- `SetBlendState(int index, BlendDescriptor)`
- `SetDepthTest(DepthTestDescriptor)`, `SetDepthMode(DepthMode)`, `SetDepthBias(...)`
- `SetStencilTest(StencilTestDescriptor)`
- `SetDepthClamp(bool)`

### 光栅化状态
- `SetFaceCulling(bool, Face)`, `SetFrontFace(FrontFace)`
- `SetPolygonMode(PolygonMode, PolygonMode)`
- `SetPrimitiveTopology(PrimitiveTopology)`, `SetPrimitiveRestart(bool, int)`
- `SetRasterizerDiscard(bool)`

### 资源绑定
- `SetVertexBuffers(ReadOnlySpan<VertexBufferDescriptor>)`
- `SetVertexAttribs(ReadOnlySpan<VertexAttribDescriptor>)`
- `SetIndexBuffer(BufferRange, IndexType)`
- `SetUniformBuffers(ReadOnlySpan<BufferAssignment>)`
- `SetStorageBuffers(ReadOnlySpan<BufferAssignment>)`
- `SetTextureAndSampler(ShaderStage, binding, ITexture, ISampler)`
- `SetImage(ShaderStage, binding, ITexture)`

### 同步
- `Barrier()`, `CommandBufferBarrier()`, `TextureBarrier()`, `TextureBarrierTiled()`

### 变换反馈
- `BeginTransformFeedback(PrimitiveTopology)`, `EndTransformFeedback()`

### 条件渲染
- `TryHostConditionalRendering(ICounterEvent, ulong, bool)` → `EndHostConditionalRendering()`

## 3. 实现 MetalRenderer 的关键映射

| GAL 概念 | Metal 映射 |
|-----------|-----------|
| IPipeline | MTLRenderCommandEncoder / MTLComputeCommandEncoder |
| IProgram | MTLRenderPipelineState + MTLFunction |
| ITexture | MTLTexture |
| ISampler | MTLSamplerState |
| BufferHandle | MTLBuffer |
| SetRenderTargets | MTLRenderPassDescriptor |
| SetViewports | MTLViewport (setViewport) |
| SetScissors | MTLScissorRect (setScissorRect) |
| SetBlendState | MTLRenderPipelineColorAttachment 的 blending 属性 |
| SetDepthTest | MTLDepthStencilState |
| SetFaceCulling | MTLCullMode (setCullMode) |
| DispatchCompute | MTLComputeCommandEncoder.dispatchThreadgroups |

## 4. 注意

- IPipeline 的所有方法签名来自真实 Ryubing 源码，禁止臆测添加
- 实现 MetalPipeline 时每个方法对应一个 `// TODO: 待实现` 的 stub
- Phase 3 只需 stub 通过编译，Phase 4/5 逐步实现
