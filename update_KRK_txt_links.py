import requests
import re
import json
from datetime import datetime
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_kbs_cookies_and_tokens():
    """
    模拟浏览器访问KBS主页，获取必要的cookies和token
    """
    session = requests.Session()
    
    # 第一步：访问KBS主页，获取cookies
    home_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        print("正在访问KBS主页获取cookies...")
        home_response = session.get('https://www.kbs.co.kr/', headers=home_headers, verify=False, timeout=15)
        print(f"主页状态码: {home_response.status_code}")
        print(f"获取到cookies: {dict(session.cookies)}")
        
        # 等待一下，模拟人类浏览行为
        time.sleep(2)
        
        # 第二步：访问一个中间页面，获取可能需要的token
        intermediate_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.kbs.co.kr/',
        }
        
        # 访问直播页面
        live_page_url = 'https://www.kbs.co.kr/live/'
        live_response = session.get(live_page_url, headers=intermediate_headers, verify=False, timeout=10)
        print(f"直播页面状态码: {live_response.status_code}")
        
        # 尝试从页面中提取可能的token
        token_patterns = [
            r'csrf[_\-]?token["\']?\s*:\s*["\']([^"\']+)["\']',
            r'access[_\-]?token["\']?\s*:\s*["\']([^"\']+)["\']',
            r'api[_\-]?key["\']?\s*:\s*["\']([^"\']+)["\']'
        ]
        
        tokens = {}
        for pattern in token_patterns:
            matches = re.findall(pattern, live_response.text, re.IGNORECASE)
            if matches:
                tokens['csrf_token'] = matches[0]
                print(f"找到token: {matches[0][:20]}...")
        
        return session, tokens
        
    except Exception as e:
        print(f"获取cookies时出错: {e}")
        return requests.Session(), {}

def update_kbs_links():
    """
    更新KBS官方频道（完整模拟浏览器行为）
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
    
    kbs_links = {channel: '' for channel in kbs_channels.keys()}
    
    try:
        # 获取带cookies的session和可能的tokens
        session, tokens = get_kbs_cookies_and_tokens()
        
        # 基础请求头
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.kbs.co.kr/live/',
            'Origin': 'https://www.kbs.co.kr',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # 如果有csrf token，添加到请求头
        if tokens.get('csrf_token'):
            base_headers['X-CSRF-TOKEN'] = tokens['csrf_token']
            base_headers['X-XSRF-TOKEN'] = tokens['csrf_token']
        
        # 遍历所有KBS频道获取链接
        for channel_name, channel_code in kbs_channels.items():
            auth_url = f'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/{channel_code}'
            
            try:
                print(f"\n{'='*50}")
                print(f"正在处理 {channel_name} (频道代码: {channel_code})...")
                print(f"请求URL: {auth_url}")
                
                # 每次请求前更新cookies
                response = session.get(auth_url, headers=base_headers, verify=False, timeout=15)
                print(f"HTTP状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"响应内容预览: {response.text[:200]}")
                    
                    try:
                        data = response.json()
                        
                        # 方法1：从channel_item获取service_url
                        if 'channel_item' in data and len(data['channel_item']) > 0:
                            service_url = data['channel_item'][0].get('service_url', '')
                            
                            if service_url:
                                kbs_links[channel_name] = service_url
                                print(f"  ✓ 从channel_item获取成功: {service_url[:80]}...")
                            else:
                                print(f"  ⚠ channel_item中的service_url为空")
                                
                                # 方法2：检查其他可能的字段
                                for key, value in data['channel_item'][0].items():
                                    if isinstance(value, str) and ('m3u8' in value or 'mp4' in value or 'stream' in value):
                                        kbs_links[channel_name] = value
                                        print(f"  ✓ 从字段 '{key}' 找到链接: {value[:80]}...")
                                        break
                                else:
                                    # 方法3：检查整个响应中是否有m3u8链接
                                    response_str = json.dumps(data, ensure_ascii=False)
                                    m3u8_matches = re.findall(r'https?://[^"\']+\.m3u8[^"\']*', response_str)
                                    if m3u8_matches:
                                        kbs_links[channel_name] = m3u8_matches[0]
                                        print(f"  ✓ 从响应文本中找到m3u8链接: {m3u8_matches[0][:80]}...")
                                    else:
                                        print(f"  ✗ 未找到任何直播链接")
                        
                        # 打印完整的响应结构（调试用）
                        print(f"响应数据结构: {list(data.keys())}")
                        
                    except json.JSONDecodeError as e:
                        print(f"  ✗ JSON解析失败: {e}")
                        
                        # 直接从文本中尝试提取m3u8链接
                        m3u8_matches = re.findall(r'https?://[^"\']+\.m3u8[^"\']*', response.text)
                        if m3u8_matches:
                            kbs_links[channel_name] = m3u8_matches[0]
                            print(f"  ✓ 直接从响应文本提取到m3u8: {m3u8_matches[0][:80]}...")
                else:
                    print(f"  ✗ 请求失败: {response.status_code}")
                    print(f"响应内容: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print(f"  ✗ 请求超时")
            except requests.exceptions.ConnectionError as e:
                print(f"  ✗ 连接错误: {str(e)}")
            except Exception as e:
                print(f"  ✗ 请求异常: {str(e)}")
            
            # 请求间隔，避免请求过快
            time.sleep(1)

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
    print("\n" + "=" * 60)
    print("开始更新KBS频道直播链接")
    print("=" * 60)
    
    kbs_links = update_kbs_links()
    
    print("\n" + "=" * 60)
    print("获取结果汇总:")
    success_count = 0
    for channel, url in kbs_links.items():
        if url:
            status = "✓ 成功"
            success_count += 1
        else:
            status = "✗ 失败"
        print(f"{channel}: {status}")
    
    if success_count == 0:
        print("\n❌ 错误: 未能获取任何有效的KBS链接")
        print("可能的原因和建议:")
        print("1. KBS API 可能需要特定的地域访问（韩国IP）")
        print("2. 可能需要登录账号")
        print("3. API 可能已变更")
        print("\n建议尝试方案2：使用hwado.net的PHP代理方式")
        return
    
    # 生成输出内容
    output_lines = []
    for channel_name, channel_url in kbs_links.items():
        if channel_url:
            output_lines.append(f'{channel_name},{channel_url}')
            print(f"  - {channel_name}: {channel_url[:60]}...")
    
    # 写回文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print("\n" + "=" * 60)
        print(f"✅ 文件已更新: {output_file}")
        print(f"📅 更新时间: {datetime.now()}")
        
        total_count = len(kbs_links)
        print(f"📊 更新统计: {success_count}/{total_count} 个频道成功获取直播链接")
        print("=" * 60)
            
    except Exception as e:
        print(f"❌ 写入文件时出错: {str(e)}")

if __name__ == '__main__':
    update_krk_txt_file()
