#!/usr/bin/env python3
"""给所有 SKILL.md 添加 YAML frontmatter"""

import os

SKILLS = {
    "metal4-api": "Metal 4 新特性参考 — Metal Shader Converter 4.0、MetalFX 等 WWDC25 技术",
    "switch-metal-api": "metal-cpp 核心 API 使用模式 — MTLDevice、MTLCommandQueue、MTLBuffer、MTLTexture",
    "switch-metal-backend": "项目全景与模式选择器 — 技术路线、工作约定、五大工作模式",
    "switch-metal-debug": "GPU 运行时调试 — 崩溃分析、渲染花屏、性能问题、GPU hang 排查",
    "switch-metal-reference-projects": "Metal 后端外部参考项目百科 — MoltenVK、Ryujinx 等 Metal 实现参考",
    "switch-metal-toolchain": "工具链路径与编译命令 — slangc、metal-shaderconverter、spirv-cross、dxc",
    "switch-ryubing-gal": "Ryubing GAL 接口参考 — 图形抽象层接口签名与调用约定",
    "switch-shader-debug": "着色器编译错误排查 — SPIR-V、Slang、DXIL、MSC 编译失败诊断",
}

base = os.path.join(os.path.dirname(__file__) or ".", "skills")

for name, desc in SKILLS.items():
    path = os.path.join(base, name, "SKILL.md")
    if not os.path.isfile(path):
        print(f"SKIP {name}: 文件不存在")
        continue
    
    with open(path, "r") as f:
        content = f.read()
    
    if content.startswith("---"):
        print(f"SKIP {name}: 已有 frontmatter")
        continue
    
    frontmatter = f"---\nname: {name}\ndescription: {desc}\n---\n\n"
    new_content = frontmatter + content
    
    with open(path, "w") as f:
        f.write(new_content)
    
    print(f"DONE {name}")

print("\n=== 完成！运行以下命令提交 ===")
print("git add skills/*/SKILL.md")
print('git commit -m "feat: 所有 SKILL.md 添加 YAML frontmatter (name+description)"')
print("git push")
