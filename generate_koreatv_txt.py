#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从 koreatv.json 读取频道信息，提取 name 和 uris，生成 Korea.txt
格式：name,uris (每个频道一行，多个uris用#分隔)
"""

import json
import os
import sys
from pathlib import Path

def load_json_file(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 '{file_path}'")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 错误：JSON 格式无效 - {e}")
        return None

def extract_name_uris(data):
    """
    从 JSON 数据中提取 name 和 uris
    根据提供的格式，数据是一个列表，每个元素包含 name 和 uris
    """
    extracted = []
    skipped = 0
    
    # 检查数据是否为列表
    if not isinstance(data, list):
        print(f"❌ 错误：期望的数据格式是列表，但得到的是 {type(data)}")
        return []
    
    for idx, item in enumerate(data, 1):
        if not isinstance(item, dict):
            print(f"⚠️ 警告：第 {idx} 条数据不是字典格式，已跳过")
            skipped += 1
            continue
        
        # 获取 name
        name = item.get('name', '')
        if not name:
            print(f"⚠️ 警告：第 {idx} 条数据缺少 name 字段，已跳过")
            skipped += 1
            continue
        
        # 获取 uris
        uris = item.get('uris', [])
        if not uris:
            print(f"⚠️ 警告：频道 '{name}' 没有 uris 字段或为空，已跳过")
            skipped += 1
            continue
        
        # 处理 uris 数组
        if isinstance(uris, list):
            # 过滤掉空值和非字符串
            valid_uris = [u for u in uris if u and isinstance(u, str)]
            if not valid_uris:
                print(f"⚠️ 警告：频道 '{name}' 的 uris 中没有有效的地址，已跳过")
                skipped += 1
                continue
            
            # 用 # 连接多个 uris
            uris_str = '#'.join(valid_uris)
        else:
            print(f"⚠️ 警告：频道 '{name}' 的 uris 不是数组格式，已跳过")
            skipped += 1
            continue
        
        # 添加到结果
        extracted.append(f"{name},{uris_str}")
        print(f"✅ 已处理: {name} ({len(valid_uris)} 个地址)")
    
    return extracted, skipped

def save_to_file(lines, output_path):
    """保存结果到文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    except Exception as e:
        print(f"❌ 写入文件失败：{e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🔍 开始处理 koreatv.json...")
    print("=" * 50)
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    input_file = script_dir / 'koreatv.json'
    output_file = script_dir / 'Korea.txt'
    
    # 检查输入文件是否存在
    if not input_file.exists():
        print(f"❌ 错误：{input_file} 不存在！")
        print("请确保 koreatv.json 文件与脚本在同一目录下。")
        sys.exit(1)
    
    print(f"📂 输入文件: {input_file}")
    print(f"📂 输出文件: {output_file}")
    print("-" * 50)
    
    # 加载 JSON
    data = load_json_file(input_file)
    if data is None:
        sys.exit(1)
    
    # 提取信息
    lines, skipped = extract_name_uris(data)
    
    if not lines:
        print("❌ 错误：没有提取到任何频道信息")
        print("请检查 JSON 文件格式是否正确")
        sys.exit(1)
    
    # 保存文件
    if save_to_file(lines, output_file):
        print("-" * 50)
        print(f"✅ 成功生成文件：{output_file}")
        print(f"📊 统计信息：")
        print(f"   - 总频道数: {len(data)}")
        print(f"   - 成功提取: {len(lines)}")
        print(f"   - 跳过无效: {skipped}")
        print("-" * 50)
        
        # 显示前几行作为预览
        print("📄 文件预览（前5行）：")
        for i, line in enumerate(lines[:5], 1):
            # 如果地址太长，截断显示
            if len(line) > 80:
                display_line = line[:77] + "..."
            else:
                display_line = line
            print(f"  {i}. {display_line}")
        
        if len(lines) > 5:
            print(f"  ... 共 {len(lines)} 行")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
