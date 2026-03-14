import requests
import re
import json
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_live_url_from_php(php_url):
    """
    通过PHP链接获取最新的直播链接
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'http://www.hwado.net/',
            'Connection': 'keep-alive'
        }
        
        # 修复URL中的反斜杠（如果有）
        php_url = php_url.replace('\\', '/')
        
        # 发起请求，允许重定向
        response = requests.get(php_url, headers=headers, verify=False, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # 获取最终的URL（重定向后的URL）
            final_url = response.url
            
            # 检查是否是有效的直播URL（不是PHP文件）
            if not final_url.endswith('.php'):
                print(f"成功获取直播链接: {final_url}")
                return final_url
            else:
                # 如果最终URL还是PHP，尝试从响应内容中提取
                print(f"最终URL仍然是PHP文件，尝试从内容提取: {final_url}")
                
                # 尝试查找常见的直播流格式
                patterns = [
                    r'https?://[^\s"\']+\.m3u8[^\s"\']*',
                    r'https?://[^\s"\']+\.mp4[^\s"\']*',
                    r'https?://[^\s"\']+\.flv[^\s"\']*',
                    r'https?://[^\s"\']+/playlist\.m3u8[^\s"\']*',
                    r'https?://[^\s"\']+/chunklist\.m3u8[^\s"\']*',
                    r'file:\s*["\'](https?://[^"\']+)["\']',
                    r'source:\s*["\'](https?://[^"\']+)["\']',
                    r'src:\s*["\'](https?://[^"\']+)["\']'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        live_url = matches[0]
                        print(f"从内容中找到直播链接: {live_url}")
                        return live_url
                
                # 如果以上方法都失败，尝试查找包含m3u8的script标签
                m3u8_pattern = r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']'
                m3u8_matches = re.findall(m3u8_pattern, response.text)
                if m3u8_matches:
                    print(f"找到m3u8链接: {m3u8_matches[0]}")
                    return m3u8_matches[0]
        
        print(f"无法从PHP链接获取直播流: {php_url}")
        return None
        
    except Exception as e:
        print(f"获取PHP链接时出错 {php_url}: {str(e)}")
        return None

def update_regional_kbs_links():
    """
    更新地区性KBS频道的链接（使用新的hwado.net地址）
    """
    regional_channels = {
        '대전 KBS1': 'http://www.hwado.net/webtv/public/11_087155E9.php',
        '광주 KBS1': 'http://www.hwado.net/webtv/public/12_7066CF5A.php',
        '대구 KBS1': 'http://www.hwado.net/webtv/public/13_B4E209CA.php',
        '울산 KBS1': 'http://www.hwado.net/webtv/public/14_ECE1A251.php',
        '부산 KBS1': 'http://www.hwado.net/webtv/public/15_6B9253F0.php'
    }
    
    updated_links = {}
    
    for channel_name, php_url in regional_channels.items():
        print(f"正在处理 {channel_name}...")
        live_url = get_live_url_from_php(php_url)
        if live_url:
            updated_links[channel_name] = live_url
        else:
            # 如果无法获取新链接，保持原PHP链接
            updated_links[channel_name] = php_url
    
    return updated_links

def update_other_channels_links():
    """
    更新其他频道的链接（JTBC）
    """
    other_channels = {
        'JTBC': 'http://www.hwado.net/webtv/catv/5006_F2AACF78.php',
    }
    
    updated_links = {}
    
    for channel_name, php_url in other_channels.items():
        print(f"正在处理 {channel_name}...")
        live_url = get_live_url_from_php(php_url)
        if live_url:
            updated_links[channel_name] = live_url
        else:
            # 如果无法获取新链接，保持原PHP链接
            updated_links[channel_name] = php_url
    
    return updated_links

def update_kbs_links():
    """
    更新KBS官方频道（现在全部通过hwado.net的PHP地址获取）
    """
    kbs_channels = {
        'KBS1': 'http://www.hwado.net/webtv/public/1_EA49B3B2.php',
        'KBS2': 'http://www.hwado.net/webtv/public/3_2C9275B7.php',
        'KBS News': 'http://www.hwado.net/webtv/catv/1_5FA37789.php',
        'KBS Drama': 'http://www.hwado.net/webtv/catv/2_02F85E1F.php',
        'KBS Joy': 'http://www.hwado.net/webtv/catv/3_39C33D26.php',
        'KBS Story': 'http://www.hwado.net/webtv/catv/4_084D1308.php',
        'KBS Life': 'http://www.hwado.net/webtv/catv/5_606FFDED.php',
        'KBS Kid': 'http://www.hwado.net/webtv/catv/6_970B6159.php',
        'KBS World': 'http://www.hwado.net/webtv/catv/7_A9D3B425.php'
    }
    
    kbs_links = {}
    
    for channel_name, php_url in kbs_channels.items():
        print(f"正在处理 {channel_name}...")
        live_url = get_live_url_from_php(php_url)
        if live_url:
            kbs_links[channel_name] = live_url
        else:
            # 如果无法获取新链接，保持原PHP链接
            kbs_links[channel_name] = php_url
    
    return kbs_links

def update_mbn_link():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Referer': 'http://www.hwado.net/'
        }
        auth_url = "https://www.mbn.co.kr/player/mbnStreamAuth_new_live.mbn?vod_url=https://hls-live.mbn.co.kr/mbn-on-air/600k/playlist.m3u8"
        response = requests.get(auth_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f'Error updating MBN link: {str(e)}')
    return None

def update_kr_txt_file():
    try:
        # 读取原文件内容
        with open('kr.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f'Error: kr.txt文件未找到，请确保文件在脚本同一文件夹下')
        return
    except Exception as e:
        print(f'Error reading kr.txt: {str(e)}')
        return

    # 更新各种链接
    kbs_links = update_kbs_links()
    regional_links = update_regional_kbs_links()
    other_links = update_other_channels_links()
    
    updated_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            updated_lines.append('')
            continue
        
        # 分割频道名和链接
        if ',' in line:
            parts = line.split(',', 1)
            channel_part = parts[0].strip()
            url_part = parts[1].strip() if len(parts) > 1 else ''
        else:
            channel_part = line.strip()
            url_part = ''
        
        # 更新KBS官方频道
        if kbs_links and channel_part in kbs_links:
            new_line = f'{channel_part},{kbs_links[channel_part]}'
            updated_lines.append(new_line)
            print(f'Updated {channel_part}: {kbs_links[channel_part][:50]}...')
        # 更新地区性KBS频道
        elif channel_part in regional_links:
            new_line = f'{channel_part},{regional_links[channel_part]}'
            updated_lines.append(new_line)
            print(f'Updated {channel_part}: {regional_links[channel_part][:50]}...')
        # 更新其他频道（JTBC等）
        elif channel_part in other_links:
            new_line = f'{channel_part},{other_links[channel_part]}'
            updated_lines.append(new_line)
            print(f'Updated {channel_part}: {other_links[channel_part][:50]}...')
        else:
            # 保持原行
            updated_lines.append(line)

    # 更新MBN链接（如果需要）
    mbn_link = update_mbn_link()
    if mbn_link:
        final_lines = []
        for line in updated_lines:
            if line.startswith('MBN,') and mbn_link:
                final_lines.append(f'MBN,{mbn_link}')
                print(f'Updated MBN: {mbn_link[:50]}...')
            else:
                final_lines.append(line)
        updated_lines = final_lines

    # 写回文件
    try:
        with open('kr.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        print(f'Links updated successfully at {datetime.now()}')
        
        # 显示更新统计
        if kbs_links:
            kbs_success = sum(1 for link in kbs_links.values() if not link.endswith('.php'))
            kbs_total = len(kbs_links)
            print(f'KBS官方频道更新统计: {kbs_success}/{kbs_total} 个频道成功获取直播链接')
        
        if regional_links:
            regional_success = sum(1 for link in regional_links.values() if not link.endswith('.php'))
            regional_total = len(regional_links)
            print(f'地区KBS频道更新统计: {regional_success}/{regional_total} 个频道成功获取直播链接')
            
        if other_links:
            other_success = sum(1 for link in other_links.values() if not link.endswith('.php'))
            other_total = len(other_links)
            print(f'其他频道更新统计: {other_success}/{other_total} 个频道成功获取直播链接')
            
    except Exception as e:
        print(f'Error writing kr.txt: {str(e)}')

if __name__ == '__main__':
    update_kr_txt_file()
