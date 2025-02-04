import requests
import re
import json
from datetime import datetime

def update_kbs_links():
    # KBS 1TV和2TV的播放链接获取
    kbs_links = {
        'KBS1TV': '',
        'KBS2TV': ''
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.kbs.co.kr',
            'Origin': 'https://www.kbs.co.kr',
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }

        # 配置会话
        session = requests.Session()

        # 获取KBS 1TV链接
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/11'
        response = session.get(auth_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'channel_item' in data and len(data['channel_item']) > 0:
                kbs_links['KBS1TV'] = data['channel_item'][0]['service_url']

        # 获取KBS 2TV链接
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/12'
        response = session.get(auth_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'channel_item' in data and len(data['channel_item']) > 0:
                kbs_links['KBS2TV'] = data['channel_item'][0]['service_url']

        return kbs_links
    except Exception as e:
        print(f'Error updating KBS links: {str(e)}')
        return None

def update_mbn_link():
    try:
        # 通过MBN认证接口获取播放链接
        auth_url = "https://www.mbn.co.kr/player/mbnStreamAuth_new_live.mbn?vod_url=https://hls-live.mbn.co.kr/mbn-on-air/600k/playlist.m3u8"
        response = requests.get(auth_url)
        if response.status_code == 200:
            return response.text.strip()
            
    except Exception as e:
        print(f'Error updating MBN link: {str(e)}')
    return None

def update_m3u_file():
    # 读取现有的m3u文件
    with open('Korea.m3u', 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新KBS链接
    kbs_links = update_kbs_links()
    if kbs_links:
        for channel, url in kbs_links.items():
            if url:
                # 使用正则表达式更新链接
                pattern = f'(#EXTINF:-1.*?{channel}.*?\n)https?://[^\n]+'
                replacement = f'\\1{url}'
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 更新MBN链接
    mbn_link = update_mbn_link()
    if mbn_link:
        # 使用与KBS相同的正则表达式格式
        pattern = '(#EXTINF:-1.*?MBN.*?\n)https?://[^\n]+'
        replacement = f'\\1{mbn_link}'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 写入更新后的内容
    with open('Korea.m3u', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Links updated successfully at {datetime.now()}')

if __name__ == '__main__':
    update_m3u_file()