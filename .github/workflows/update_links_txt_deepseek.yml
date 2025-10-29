import requests
import re
import json
from datetime import datetime
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_kbs_links():
    kbs_links = {
        'KBS1': '',
        'KBS2': ''
    }
    
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
            'Pragma': 'no-cache'
        }

        session = requests.Session()
        session.headers.update(headers)

        # 获取KBS1链接
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/11'
        response = session.get(auth_url, headers=headers, verify=False, timeout=10)
        print(f"KBS1 请求状态: {response.status_code}")
        
        if response.status_code == 200:
            print(f"KBS1 响应内容: {response.text[:200]}")  # 调试输出
            try:
                data = response.json()
                if 'channel_item' in data and len(data['channel_item']) > 0:
                    kbs_links['KBS1'] = data['channel_item'][0]['service_url']
                    print(f"KBS1 获取成功: {kbs_links['KBS1']}")
                else:
                    print("KBS1 channel_item 为空或不存在")
            except json.JSONDecodeError as e:
                print(f"KBS1 JSON解析失败: {e}")
                # 尝试使用正则表达式提取（像PHP代码那样）
                match = re.search(r'"service_url":"(.*?)"', response.text)
                if match:
                    kbs_links['KBS1'] = match.group(1)
                    print(f"KBS1 正则提取成功: {kbs_links['KBS1']}")
        else:
            print(f"KBS1 请求失败: {response.status_code}")

        # 获取KBS2链接
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/12'
        response = session.get(auth_url, headers=headers, verify=False, timeout=10)
        print(f"KBS2 请求状态: {response.status_code}")
        
        if response.status_code == 200:
            print(f"KBS2 响应内容: {response.text[:200]}")  # 调试输出
            try:
                data = response.json()
                if 'channel_item' in data and len(data['channel_item']) > 0:
                    kbs_links['KBS2'] = data['channel_item'][0]['service_url']
                    print(f"KBS2 获取成功: {kbs_links['KBS2']}")
                else:
                    print("KBS2 channel_item 为空或不存在")
            except json.JSONDecodeError as e:
                print(f"KBS2 JSON解析失败: {e}")
                # 尝试使用正则表达式提取
                match = re.search(r'"service_url":"(.*?)"', response.text)
                if match:
                    kbs_links['KBS2'] = match.group(1)
                    print(f"KBS2 正则提取成功: {kbs_links['KBS2']}")
        else:
            print(f"KBS2 请求失败: {response.status_code}")

        return kbs_links
        
    except Exception as e:
        print(f'Error updating KBS links: {str(e)}')
        return None

def update_mbn_link():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
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

    # 更新KBS链接
    kbs_links = update_kbs_links()
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
        
        # 更新KBS频道
        if kbs_links and channel_part in kbs_links and kbs_links[channel_part]:
            new_line = f'{channel_part},{kbs_links[channel_part]}'
            updated_lines.append(new_line)
            print(f'Updated {channel_part}: {kbs_links[channel_part]}')
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
                print(f'Updated MBN: {mbn_link}')
            else:
                final_lines.append(line)
        updated_lines = final_lines

    # 写回文件
    try:
        with open('kr.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        print(f'Links updated successfully at {datetime.now()}')
    except Exception as e:
        print(f'Error writing kr.txt: {str(e)}')

if __name__ == '__main__':
    update_kr_txt_file()
