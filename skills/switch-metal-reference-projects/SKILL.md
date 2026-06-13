---
name: switch-metal-reference-projects
description: Metal 后端外部参考项目百科 — MoltenVK、Ryujinx 等 Metal 实现参考
---

# Metal 后端外部参考项目百科

> 最后更新：2026-06-13
> 涵盖 DXMT、WickedEngine、Kosmickrisp 三个外部项目 + Slang PR 优先级 + Metal 限制清单。
> 当需要查"某个 Metal 问题可以参考哪个项目"时读取本 Skill。

---

## 1. 三个项目速览

| 项目 | 仓库 | 定位 | 核心价值 |
|------|------|------|----------|
| **DXMT** | `3Shain/dxmt` | D3D11→Metal 翻译层 | DXBC→AIR 直接转换、GS 分解、状态映射 |
| **WickedEngine** | `turanszkij/WickedEngine` | 多平台游戏引擎 | HLSL→Metal 管线、PSO管理、渲染Pass架构 |
| **Kosmickrisp (kk)** | `mesa/mesa` 主线 `src/kosmickrisp/` | Vulkan→Metal 驱动 | Metal API 桥接、子群/纹理降级、workaround清单 |

---

## 2. 快速查阅表：每个技术问题应该参考谁

| 我要做…… | 主要参考 | 文件/路径 |
|-----------|----------|-----------|
| 创建 MTLDevice/MTLCompiler | **kk** | `bridge/mtl_device.m`, `bridge/mtl_compiler.m` |
| DXIL→Metal 着色器转换 | **DXMT** + WE | `airconv/dxbc_converter.cpp`, `metal_irconverter/` |
| 渲染 Pass 和 PSO 管理 | **WickedEngine** | `WickedEngine/Utility/metal/` |
| Buffer 绑定和描述符布局 | **kk** | `kk_private.h`, `kk_nir_lower_descriptors.c` |
| 三级 buffer 绑定模式 | **kk** | `compiler/nir_to_msl.c` (emit_inputs 函数) |
| Geometry Shader → Mesh 转换 | **DXMT** | `airconv/dxbc_converter_gs.cpp` |
| 曲面细分 → Compute 转换 | **kk** | 曲面细分提交 `68048759` |
| Wave/子群 → Metal SIMD | **kk** | `compiler/msl_nir_lower_subgroups.c` |
| 纹理操作限制处理 | **kk** | `compiler/msl_nir_lower_common.c` |
| Metal 编译器 workaround | **kk** | `mtl_compiler.m`, `kk_private.h` |
| 像素格式映射表 | **kk** + DXMT | `vk_to_mtl_map.c`, `d3d11/` |
| 稀疏资源和 MTLHeap | **kk** | `bridge/mtl_heap.m` |
| MetalFX 上采样 | **WickedEngine** | `Utility/metal/MetalFX/` |
| HLSL 着色器组织方式 | **WickedEngine** | `shaders/` (ShaderInterop_*.h) |
| AIR 直接生成（备选路径） | **DXMT** | `airconv/metallib_writer.cpp` |
| NIR 降级 pass 模式 | **kk** | `compiler/msl_nir_lower_*.c` |

---

## 3. DXMT 深度剖析

### 3.1 架构
```
D3D11 API → dxmt core → nativemetal → Metal 运行时
              │
              ├── airconv/    (DXBC→AIR 着色器转换)
              ├── d3d11/      (D3D11 状态管理)
              ├── dxgi/       (DXGI 交换链)
              └── nativemetal/ (C++ Metal 封装)
```

### 3.2 airconv — 核心着色器转换器
- `dxbc_converter.cpp` — 主转换器：DXBC 字节码 → Apple IR (AIR)
- `dxbc_converter_gs.cpp` — **Geometry Shader → AIR 转换**（证明 GS 可以通过 AIR 表达！）
- `dxbc_converter_ts.cpp` — Tessellation Shader 转换
- `metallib_writer.cpp` — AIR → metallib 二进制写入
- `air_type.cpp` / `air_signature.cpp` — AIR 类型系统和函数签名

### 3.3 对我们的启示
- **Path B 备选方案：** Slang→DXIL→(参考 airconv)→AIR→metallib。如果 MSC 转换质量不够，可以参考 DXMT 的模式自建转换。
- **GS 处理：** `dxbc_converter_gs.cpp` 证明了 GS 语义可以通过 AIR 表达，这为我们的 Mesh Shader 替代提供了语义参考。
- **状态映射：** D3D11 渲染状态 → Metal 渲染状态的映射表可直接参考。

---

## 4. Kosmickrisp 深度剖析

### 4.1 目录架构
```
src/kosmickrisp/
├── bridge/        # Metal API ObjC 封装层 (30+ 文件)
│   ├── mtl_device.m, mtl_compiler.m, mtl_buffer.m
│   ├── mtl_texture.m, mtl_sampler.m, mtl_heap.m
│   ├── mtl_command_buffer.m, mtl_command_queue.m
│   ├── mtl_encoder.m, mtl_render_state.m, mtl_sync.m
│   ├── mtl_format.h, mtl_types.h
│   └── vk_to_mtl_map.c          # VK→MTL 枚举映射表
├── compiler/      # NIR→MSL 编译器
│   ├── nir_to_msl.c             # 核心编译器 ~2300行
│   ├── msl_nir_lower_common.c   # 纹理/输出降级 (641行)
│   ├── msl_nir_lower_subgroups.c # 子群操作降级 (116行)
│   ├── msl_type_inference.c     # 类型推断 (925行)
│   ├── msl_iomap.c              # I/O 映射
│   └── msl_nir_algebraic.py     # 代数优化规则
├── vulkan/        # Vulkan API 实现
│   ├── kk_nir_lower_descriptors.c  # 描述符降级 (901行)
│   ├── kk_nir_lower_vbo.c          # 顶点缓冲降级
│   ├── kk_nir_lower_textures.c     # 纹理操作降级
│   ├── kk_nir_lower_multiview.c    # 多视图降级
│   └── kk_private.h                # 关键常量
├── libkk/         # 核心库
├── clc/           # OpenCL 编译器
└── util/          # 工具集
```

### 4.2 着色器编译管线
```
SPIR-V → Mesa NIR → NIR Lowering Passes → nir_to_msl.c (文本生成) → MTL4Compiler → MTLLibrary → PSO
```

### 4.3 三级 Buffer 绑定（kk 的 emit_inputs）
```c
// 从 nir_to_msl.c 中提取：
constant Buffer &buf0 [[buffer(0)]];       // 根描述符表
constant SamplerTable &sampler_table [[buffer(1)]]; // 采样器表
constant Buffer &per_draw [[buffer(2)]];   // Per-draw 动态数据
```

### 4.4 关键常量（kk_private.h）
| 常量 | 值 | 用途 |
|------|-----|------|
| KK_MIN_UBO_ALIGNMENT | 64 | UBO 最小对齐（Metal 比 Vulkan 高） |
| KK_MIN_SSBO_ALIGNMENT | 16 | SSBO 最小对齐 |
| KK_MAX_CBUF_SIZE | 64KB | 常量缓冲最大尺寸 |
| KK_MAX_SETS | 32 | 最大描述符集数 |
| KK_MAX_SAMPLES | 8 | 最大 MSAA 采样数 |
| KK_MAX_MULTIVIEW_VIEW_COUNT | 32 | 多视图最大数 |
| KK_SPARSE_ADDR_SPACE_SIZE | 512GB (1<<39) | 稀疏地址空间 |

### 4.5 资源选项（已证实可用）
```c
#define KK_MTL_RESOURCE_OPTIONS \
   MTL_RESOURCE_STORAGE_MODE_SHARED |          // UMA 架构
   MTL_RESOURCE_CPU_CACHE_MODE_DEFAULT_CACHE |  // 默认缓存
   MTL_RESOURCE_TRACKING_MODE_UNTRACKED         // 不追踪（性能）
```

### 4.6 Metal 编译器 Workaround 清单
| 问题 | 表现 | kk 的解决方案 |
|------|------|--------------|
| 多 MTL4Compiler 并发 | 进程崩溃 | 全局单例（每 MTLDevice 一个） |
| MSL 4.0 float16 | M1/M2 上超时 | 降级到 `MTLLanguageVersion3_2` |
| Scratch buffer 初始化 | 未初始化导致随机值 | `KK_WORKAROUND_1`: 显式 `= {0}` |
| 编译器实例生命周期 | — | `@autoreleasepool` 包裹每个操作 |

### 4.7 子群操作限制（必须显式降级）
kk 的 `msl_nir_lower_subgroups.c` 揭示的 Metal 限制：
- **SIMD 宽度固定 32**（`.subgroup_size = 32`）
- **Shuffle 需 uniform delta**（`.lower_relative_shuffle = true`）
- **Reduce 不支持某些类型/集群大小**（`.lower_reduce = true`）
- **Rotate 不支持集群大小**（`.lower_rotate_clustered_to_shuffle = true`）
- **Bool 需 widening 到 32bit**（Metal 子群操作不支持 1-bit bool）
- **Ballot/Vote 全部需要降级**（`.lower_subgroup_masks / lower_vote_* / lower_inverse_ballot = true`）

### 4.8 纹理限制（必须降级）
- `lower_1d = true` — Metal 不支持 1D 纹理
- `lower_tg4_offsets = true` — 不支持每采样 TG4 偏置
- `lower_txf_offset = true` — 不支持 texelFetch 偏置
- `lower_txd_cube_map = true` — Cube map LOD 梯度需要降级
- `lower_sampler_lod_bias = true` — LOD 偏置需要软件模拟

### 4.9 曲面细分方案
- **方案：** "Same approach as HK"（Honeykrisp）— Compute Shader 实现
- **流程：** NIR tess shader → `kernel void` → MTLComputePipelineState → dispatch
- **提交：** `68048759` (实现), `84929be1` (多阶段编译重构), `73172824` (draw dispatch 重构)
- **额外处理：** instance_id 降级、per-draw 上传清理、prefix count 子群优化

---

## 5. WickedEngine 参考要点

### 5.1 Metal 实现位置
- `WickedEngine/Utility/metal/` — Metal API 的 C++ 封装
  - `Metal/` — 核心 Metal 封装
  - `MetalFX/` — MetalFX 上采样
  - `metal_irconverter/` — Apple IRCompiler 封装（HLSL→Metal）
  - `metal_irconverter_ext/` — 扩展（含 `Metal_HLSL.inc`）

### 5.2 适用参考场景
- **渲染 Pass 管理：** PSO 缓存策略、render pass descriptor 构造
- **Shader reflection：** 从编译后的 metallib 提取绑定信息
- **引擎级架构：** 如何组织 multi-backend 渲染器的 Metal 分支

---

## 6. Slang PR 优先级（2026-06 分析）

### P0 — 必须关注/合入即用
| PR | 标题 | 状态 |
|----|------|------|
| #11578 | Implement scalar layout for Metal device buffers | 开放 |
| #11331 | Metal: lower pointer-to-pointer in buffer types | **已合并** |
| #11073 | Emit [[buffer(n)]] for DescriptorHandle on Metal | **已合并** |

### P1 — 优先跟踪
| PR | 标题 | 状态 |
|----|------|------|
| #10051 | Fix Metal vertex shader parameters | 开放 |
| #11570 | Diagnose unsupported target intrinsics | 开放 |
| #11135 | [Reflection]: Track "used" for uniforms | 开放 |

### P2 — 重要但不紧急
| PR | 标题 | 状态 |
|----|------|------|
| #10741 | Fix HLSL emission for mesh shader output parameters | **已合并** |
| #11544 | Fix HLSL mesh-shader output qualifiers exactly once | **已合并** |
| #11430 | Fix unaligned byte-address descriptor loads | **已合并** |
| #11348 | Bump DXC to v1.10.2605.24 | **已合并** |
| #11461 | Enable default DXC source builds on macOS | **已合并** |
| #11489 | Fix DXC source build with Apple Clang 21+ | **已合并** |

### 已合并的 Metal 相关 PR（升级 slangc 后即可用）
#10981 (framebuffer fetch), #11073 ([[buffer(n)]]), #11331 (pointer-to-pointer), #10849 (DescriptorHandle cast), #11099 (cooperative matrix)

---

## 7. 三者整合策略

三者不冲突——覆盖不同技术层次：
- **DXMT** → 着色器转换参考（DX→AIR 模式）
- **WickedEngine** → 引擎架构参考（PSO/渲染Pass）
- **Kosmickrisp** → 驱动适配参考（Metal API桥接/workaround）

Metal 端适配经验（buffer绑定、纹理限制、子群降级、编译器bug规避）三者完全共享，不存在"选A弃B"。

### 12 步整合路线（详见 `dxmt-we-kk-integration.html`）
- **阶段1（Bridge层）：** 参考 kk 搭建 libmetal_bridge + 单例编译器 + 格式映射
- **阶段2（着色器管线）：** Slang→DXIL + MSC验证 + GS→Mesh替代
- **阶段3（资源架构）：** 三级绑定+AB混合 + 渲染Pass管理
- **阶段4（集成优化）：** C# P/Invoke对接 + workaround清单维护

---

## 8. 关联 Skills

| Skill | 关系 |
|-------|------|
| `switch-metal-backend` | 项目全景（引用本 Skill 获取参考细节） |
| `switch-metal-toolchain` | 工具链路径（本 Skill 不重复） |
| `switch-metal-api` | Metal API 语法速查 |
| `metal4-api` | Metal 4 新特性 |
| `switch-shader-debug` | 着色器调试流程 |
