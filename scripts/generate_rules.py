import os
import sys

# === 配置区域 ===
# 脚本所在目录 (MyAi_Rules/scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 规则根目录 (MyAi_Rules/rules)
RULES_ROOT = os.path.join(SCRIPT_DIR, '..', 'rules')

# 定义不同类型的规则组合
# 你可以在这里扩展，比如定义 'unity', 'python-tool' 等组合
PRESETS = {
    'cocos': [
        'common/global_style.md',
        'engines/cocos.md'
    ],
    'unity': [
        'common/global_style.md',
        # 'engines/unity.md' # 未来有了再加
    ],
    'python': [
        'common/global_style.md',
        'languages/python.md' # 假设你有这个
    ]
}

def merge_rules(preset_name='cocos'):
    """
    合并逻辑：
    1. 基础规则 (Global)
    2. 引擎规则 (Engine)
    3. 项目本地规则 (Project Specific)
    """
    
    # 1. 获取预设的文件列表
    if preset_name not in PRESETS:
        print(f"Error: 找不到预设配置 '{preset_name}'。可用预设: {list(PRESETS.keys())}")
        return

    files_to_merge = PRESETS[preset_name]
    
    final_content = []

    # 2. 读取通用规则和引擎规则
    print(f"正在生成 '{preset_name}' 模式的规则...")
    for rel_path in files_to_merge:
        full_path = os.path.join(RULES_ROOT, rel_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                final_content.append(f.read())
                final_content.append("\n\n---\n\n") # 添加分隔符
        else:
            print(f"Warning: 找不到规则文件: {rel_path}")

    # 3. 读取项目特有规则 (Layer 3)
    # 假设我们是在项目根目录运行，或者通过子模块方式运行
    # 目标是寻找项目根目录下的 'project_rules.md'
    # 脚本路径: Project/.ai-rules/scripts/generate.py
    # 项目路径: Project/
    project_root = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
    project_rule_path = os.path.join(project_root, 'project_rules.md')

    if os.path.exists(project_rule_path):
        print("发现项目特有规则 (project_rules.md)，正在合并...")
        with open(project_rule_path, 'r', encoding='utf-8') as f:
            final_content.append(f.read())
    else:
        print("未发现项目特有规则 (project_rules.md)，跳过。")

    # 4. 输出到 .cursorrules
    output_path = os.path.join(project_root, '.cursorrules')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("".join(final_content))
        print(f"✅ 成功生成 .cursorrules 文件！位置: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    # 从命令行参数获取预设名，默认为 cocos
    # 用法: python .ai-rules/scripts/generate_rules.py unity
    mode = sys.argv[1] if len(sys.argv) > 1 else 'cocos'
    merge_rules(mode)