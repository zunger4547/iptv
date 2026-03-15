#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从 koreatv.json 读取频道信息，提取 name 和 uris，更新 Korea.txt 中的"新韩国电视"分组
保留原有的"原韩国电视"分组内容不变
"""

import json
import os
import sys
from pathlib import Path
import re

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

def extract_name_uris_from_json(data):
    """
    从 JSON 数据中提取 name 和 uris
    返回格式化的频道列表
    """
    channels = []
    skipped = 0
    
    # 检查数据是否为列表
    if not isinstance(data, list):
        print(f"❌ 错误：期望的数据格式是列表，但得到的是 {type(data)}")
        return [], 0
    
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
        channels.append(f"{name},{uris_str}")
        print(f"✅ 已处理: {name} ({len(valid_uris)} 个地址)")
    
    return channels, skipped

def parse_korea_file(file_path):
    """
    解析现有的 Korea.txt 文件
    返回分组字典，键为分组名，值为该分组下的频道列表
    """
    groups = {}
    current_group = None
    group_pattern = re.compile(r'^(.+),#genre#$')
    
    if not os.path.exists(file_path):
        print(f"⚠️ 警告：{file_path} 不存在，将创建新文件")
        return groups
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            # 检查是否是分组标题行
            match = group_pattern.match(line)
            if match:
                current_group = match.group(1)
                groups[current_group] = []
            elif current_group:
                # 添加到当前分组
                groups[current_group].append(line)
        
        print(f"📂 读取到现有分组: {list(groups.keys())}")
        return groups
    
    except Exception as e:
        print(f"❌ 读取文件失败：{e}")
        return groups

def write_korea_file(file_path, groups):
    """
    将分组字典写回 Korea.txt 文件
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for group_name, channels in groups.items():
                # 写入分组标题
                f.write(f"{group_name},#genre#\n")
                
                # 写入该分组下的所有频道
                for channel in channels:
                    f.write(f"{channel}\n")
                
                # 分组之间加空行（除了最后一个分组）
                f.write("\n")
        
        return True
    except Exception as e:
        print(f"❌ 写入文件失败：{e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 开始处理 koreatv.json 并更新 Korea.txt...")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    input_file = script_dir / 'koreatv.json'
    output_file = script_dir / 'Korea.txt'
    
    print(f"📂 JSON 文件: {input_file}")
    print(f"📂 TXT 文件: {output_file}")
    print("-" * 60)
    
    # 检查输入文件是否存在
    if not input_file.exists():
        print(f"❌ 错误：{input_file} 不存在！")
        print("请确保 koreatv.json 文件与脚本在同一目录下。")
        sys.exit(1)
    
    # 加载 JSON
    data = load_json_file(input_file)
    if data is None:
        sys.exit(1)
    
    # 从 JSON 提取频道信息
    new_channels, skipped = extract_name_uris_from_json(data)
    
    if not new_channels:
        print("❌ 错误：没有提取到任何频道信息")
        print("请检查 JSON 文件格式是否正确")
        sys.exit(1)
    
    print("-" * 60)
    print(f"📊 JSON 处理统计：")
    print(f"   - 总频道数: {len(data)}")
    print(f"   - 成功提取: {len(new_channels)}")
    print(f"   - 跳过无效: {skipped}")
    print("-" * 60)
    
    # 解析现有的 Korea.txt 文件
    groups = parse_korea_file(output_file)
    
    # 更新"新韩国电视"分组
    target_group = "新韩国电视"
    groups[target_group] = new_channels
    
    print(f"✅ 已更新分组 '{target_group}'，共 {len(new_channels)} 个频道")
    
    # 写回文件
    if write_korea_file(output_file, groups):
        print("-" * 60)
        print(f"✅ 成功更新文件：{output_file}")
        print(f"📊 最终文件包含 {len(groups)} 个分组：")
        for group_name, channels in groups.items():
            print(f"   - {group_name}: {len(channels)} 个频道")
        
        # 显示新分组的前几行作为预览
        print("-" * 60)
        print(f"📄 '{target_group}' 分组预览（前5行）：")
        for i, line in enumerate(new_channels[:5], 1):
            # 如果地址太长，截断显示
            if len(line) > 80:
                display_line = line[:77] + "..."
            else:
                display_line = line
            print(f"  {i}. {display_line}")
        
        if len(new_channels) > 5:
            print(f"  ... 共 {len(new_channels)} 行")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
