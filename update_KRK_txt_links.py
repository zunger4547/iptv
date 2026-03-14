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
        # 使用与PHP代码更接近的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.kbs.co.kr/',
            'Origin': 'https://www.kbs.co.kr'
        }

        session = requests.Session()
        session.headers.update(headers)

        # 遍历所有KBS频道获取链接
        for channel_name, channel_code in kbs_channels.items():
            auth_url = f'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/{channel_code}'
            
            try:
                print(f"正在处理 {channel_name} (频道代码: {channel_code})...")
                response = session.get(auth_url, headers=headers, verify=False, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'channel_item' in data and len(data['channel_item']) > 0:
                            service_url = data['channel_item'][0]['service_url']
                            kbs_links[channel_name] = service_url
                            print(f"  ✓ 获取成功: {service_url[:80]}...")
                        else:
                            print(f"  ✗ channel_item 为空或不存在")
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
                            kbs_links[channel_name] = ''
                else:
                    print(f"  ✗ 请求失败: {response.status_code}")
                    kbs_links[channel_name] = ''
                    
            except Exception as e:
                print(f"  ✗ 请求异常: {str(e)}")
                kbs_links[channel_name] = ''
                continue

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
    
    if not kbs_links:
        print("错误: 未能获取任何KBS链接")
        return
    
    # 生成输出内容
    output_lines = []
    for channel_name, channel_url in kbs_links.items():
        if channel_url:  # 只添加成功获取到链接的频道
            output_lines.append(f'{channel_name},{channel_url}')
        else:
            print(f"警告: {channel_name} 未能获取到有效链接")
    
    # 写回文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print("=" * 60)
        print(f"文件已更新: {output_file}")
        print(f"更新时间: {datetime.now()}")
        
        # 显示更新统计
        success_count = sum(1 for url in kbs_links.values() if url)
        total_count = len(kbs_links)
        print(f"更新统计: {success_count}/{total_count} 个频道成功获取直播链接")
        
        if success_count > 0:
            print("\n成功更新的频道:")
            for channel_name, channel_url in kbs_links.items():
                if channel_url:
                    print(f"  - {channel_name}")
        
        print("=" * 60)
            
    except Exception as e:
        print(f"写入文件时出错: {str(e)}")

if __name__ == '__main__':
    update_krk_txt_file()
