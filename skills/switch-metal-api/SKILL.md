# Metal API 速查

> metal-cpp 核心 API 模式速查。Phase 4 实现 libmetal_bridge 时直接引用。

---

## 1. 设备（MTL::Device）

```cpp
// 获取默认 GPU
NS::SharedPtr<MTL::Device> device = NS::TransferPtr(MTL::CreateSystemDefaultDevice());

// 查询 GPU 名称（用于日志）
NS::String* name = device->name();  // 如 "Apple M1"
```

## 2. 命令队列（MTL::CommandQueue）

```cpp
NS::SharedPtr<MTL::CommandQueue> queue = NS::TransferPtr(device->newCommandQueue());
// 注意：通常一个 Device 一个 Queue 即可，无需多队列
```

## 3. 缓冲区（MTL::Buffer）

```cpp
// 三种存储模式（对 M1 的关键区别）：
// - MTL::StorageModeShared    → CPU+GPU 共享（默认，适合小数据/UMA 架构）
// - MTL::StorageModeManaged   → macOS 特有，显式同步（适合大数据，M1 上等效 Shared）
// - MTL::StorageModePrivate   → GPU only（适合 GPU 中间数据，性能最优）

// 创建
NS::SharedPtr<MTL::Buffer> buf = NS::TransferPtr(
    device->newBuffer(data, size, MTL::ResourceStorageModeShared)
);
```

## 4. 纹理（MTL::Texture）

```cpp
MTL::TextureDescriptor* desc = MTL::TextureDescriptor::alloc()->init();
desc->setPixelFormat(MTL::PixelFormatRGBA8Unorm);
desc->setWidth(512);
desc->setHeight(512);
desc->setStorageMode(MTL::StorageModePrivate);
desc->setUsage(MTL::TextureUsageShaderRead | MTL::TextureUsageRenderTarget);

NS::SharedPtr<MTL::Texture> tex = NS::TransferPtr(device->newTexture(desc));
```

## 5. 渲染管线状态（MTL::RenderPipelineState）

```cpp
MTL::RenderPipelineDescriptor* rpDesc = MTL::RenderPipelineDescriptor::alloc()->init();

// 设置着色器函数
rpDesc->setVertexFunction(vertexFunc);
rpDesc->setFragmentFunction(fragmentFunc);

// 设置颜色附件格式
rpDesc->colorAttachments()->object(0)->setPixelFormat(MTL::PixelFormatBGRA8Unorm);

// 创建管线
NS::SharedPtr<MTL::RenderPipelineState> pso = NS::TransferPtr(
    device->newRenderPipelineState(rpDesc, &error)
);
```

## 6. 着色器库（MTL::Library）— Path A 加载

```cpp
// 从 metallib 字节加载（MSC 输出）
const void* metallibData = ...;  // 来自文件或内存
size_t metallibSize = ...;

NS::SharedPtr<MTL::Library> lib = NS::TransferPtr(
    device->newLibrary(dispatch_data_create(metallibData, metallibSize, ...), &error)
);

// 获取函数
NS::SharedPtr<MTL::Function> func = NS::TransferPtr(
    lib->newFunction(NS::String::string("vertexMain", NS::UTF8StringEncoding))
);
```

## 7. 命令编码器（MTL::CommandBuffer + Encoder）

```cpp
// 创建命令缓冲
NS::SharedPtr<MTL::CommandBuffer> cmd = NS::TransferPtr(queue->commandBuffer());

// 渲染编码器
MTL::RenderPassDescriptor* rpDesc = ...;
NS::SharedPtr<MTL::RenderCommandEncoder> encoder = 
    NS::TransferPtr(cmd->renderCommandEncoder(rpDesc));

encoder->setRenderPipelineState(pso.get());
encoder->setVertexBuffer(vb.get(), 0, 0);
encoder->drawPrimitives(MTL::PrimitiveTypeTriangle, NS::UInteger(0), NS::UInteger(3));
encoder->endEncoding();

// 提交
cmd->commit();
cmd->waitUntilCompleted();
```

## 8. 关键注意事项

- M1 是 UMA 架构：**Shared 和 Managed 实际行为相同**
- metal-cpp 使用 `NS::SharedPtr` 管理生命周期，无需手动 release
- 所有 `alloc()->init()` 创建的对象需手动 release，或包装为 SharedPtr
- 着色器加载失败时检查 MTL::Error 对象（`&error` 参数）