import requests
import re
import json
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_kbs_links():
    """
    更新KBS官方频道（通过KBS API获取）
    """
    # 定义所有KBS频道及其对应的channel_code
    kbs_channels = {
        'KBS1': '11',
        'KBS2': '12', 
        'KBS World': '14',
        'KBS News D': '81',
        'KBS Drama': 'N91',
        'KBS Joy': 'N92',
        'KBS Life': 'N93',
        'KBS Story': 'N94',
        'KBS Kid': 'N96'
    }
    
    kbs_links = {}
    
    try:
        # 简化请求头，避免被拒绝
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.kbs.co.kr/',
            'Origin': 'https://www.kbs.co.kr'
        }

        session = requests.Session()
        session.headers.update(headers)

        # 遍历所有KBS频道获取链接
        for channel_name, channel_code in kbs_channels.items():
            auth_url = f'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/{channel_code}'
            
            try:
                print(f"\n正在处理 {channel_name} (频道代码: {channel_code})...")
                print(f"请求URL: {auth_url}")
                
                response = session.get(auth_url, headers=headers, verify=False, timeout=10)
                print(f"HTTP状态码: {response.status_code}")
                
                if response.status_code == 200:
                    # 打印部分响应内容用于调试
                    print(f"响应内容预览: {response.text[:200]}")
                    
                    try:
                        data = response.json()
                        print(f"JSON解析成功，数据类型: {type(data)}")
                        print(f"JSON键: {list(data.keys()) if isinstance(data, dict) else '不是字典'}")
                        
                        if 'channel_item' in data:
                            print(f"channel_item类型: {type(data['channel_item'])}")
                            print(f"channel_item长度: {len(data['channel_item'])}")
                            
                            if len(data['channel_item']) > 0:
                                print(f"channel_item[0]键: {list(data['channel_item'][0].keys()) if isinstance(data['channel_item'][0], dict) else '不是字典'}")
                                
                                if 'service_url' in data['channel_item'][0]:
                                    service_url = data['channel_item'][0]['service_url']
                                    kbs_links[channel_name] = service_url
                                    print(f"  ✓ 获取成功: {service_url[:80]}...")
                                else:
                                    print(f"  ✗ service_url不存在")
                                    kbs_links[channel_name] = ''
                            else:
                                print(f"  ✗ channel_item为空数组")
                                kbs_links[channel_name] = ''
                        else:
                            print(f"  ✗ 响应中没有channel_item字段")
                            print(f"完整响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                            kbs_links[channel_name] = ''
                            
                    except json.JSONDecodeError as e:
                        print(f"  ✗ JSON解析失败: {e}")
                        # 尝试使用正则表达式提取
                        match = re.search(r'"service_url":"(.*?)"', response.text)
                        if match:
                            service_url = match.group(1)
                            kbs_links[channel_name] = service_url
                            print(f"  ✓ 正则提取成功: {service_url[:80]}...")
                        else:
                            print(f"  ✗ 正则提取失败，未找到service_url")
                            kbs_links[channel_name] = ''
                else:
                    print(f"  ✗ 请求失败: {response.status_code}")
                    print(f"响应内容: {response.text[:200]}")
                    kbs_links[channel_name] = ''
                    
            except requests.exceptions.Timeout:
                print(f"  ✗ 请求超时")
                kbs_links[channel_name] = ''
            except requests.exceptions.ConnectionError as e:
                print(f"  ✗ 连接错误: {str(e)}")
                kbs_links[channel_name] = ''
            except Exception as e:
                print(f"  ✗ 请求异常: {str(e)}")
                kbs_links[channel_name] = ''

        return kbs_links
        
    except Exception as e:
        print(f'更新KBS链接时出错: {str(e)}')
        return {}

def update_krk_txt_file():
    """
    更新KRK.txt文件中的KBS频道链接
    """
    output_file = 'KRK.txt'
    
    # 获取更新的KBS链接
    print("=" * 60)
    print("开始更新KBS频道直播链接")
    print("=" * 60)
    
    kbs_links = update_kbs_links()
    
    print("\n" + "=" * 60)
    print("获取结果汇总:")
    for channel, url in kbs_links.items():
        status = "✓ 成功" if url else "✗ 失败"
        print(f"{channel}: {status}")
    
    if not any(kbs_links.values()):  # 检查是否至少有一个成功
        print("\n错误: 未能获取任何有效的KBS链接")
        print("可能的原因:")
        print("1. KBS API服务器暂时不可用")
        print("2. 网络连接问题")
        print("3. IP被限制（可能需要使用代理）")
        print("4. API接口已变更")
        return
    
    # 生成输出内容
    output_lines = []
    for channel_name, channel_url in kbs_links.items():
        if channel_url:  # 只添加成功获取到链接的频道
            output_lines.append(f'{channel_name},{channel_url}')
        else:
            print(f"警告: {channel_name} 未能获取到有效链接，已跳过")
    
    # 写回文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print("\n" + "=" * 60)
        print(f"✅ 文件已更新: {output_file}")
        print(f"📅 更新时间: {datetime.now()}")
        
        # 显示更新统计
        success_count = sum(1 for url in kbs_links.values() if url)
        total_count = len(kbs_links)
        print(f"📊 更新统计: {success_count}/{total_count} 个频道成功获取直播链接")
        
        if success_count > 0:
            print("\n✅ 成功更新的频道:")
            for channel_name, channel_url in kbs_links.items():
                if channel_url:
                    print(f"  - {channel_name}")
        
        print("=" * 60)
            
    except Exception as e:
        print(f"❌ 写入文件时出错: {str(e)}")

if __name__ == '__main__':
    update_krk_txt_file()
