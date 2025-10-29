import requests
import re
import json
from datetime import datetime

def update_kbs_links():
    # 关键修改1：字典key改为和kr.txt一致的频道名（KBS1/KBS2，无TV后缀）
    kbs_links = {
        'KBS1': '',
        'KBS2': ''
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.kbs.co.kr',
            'Origin': 'https://www.kbs.co.kr',
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }

        session = requests.Session()

        # 获取KBS1链接（对应channel_code=11，匹配kr.txt的KBS1）
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/11'
        response = session.get(auth_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'channel_item' in data and len(data['channel_item']) > 0:
                kbs_links['KBS1'] = data['channel_item'][0]['service_url']

        # 获取KBS2链接（对应channel_code=12，匹配kr.txt的KBS2）
        auth_url = 'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/12'
        response = session.get(auth_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'channel_item' in data and len(data['channel_item']) > 0:
                kbs_links['KBS2'] = data['channel_item'][0]['service_url']

        return kbs_links
    except Exception as e:
        print(f'Error updating KBS links: {str(e)}')
        return None

# 保留MBN更新函数（若kr.txt后续要加MBN，可直接用；暂时不用也不影响）
def update_mbn_link():
    try:
        auth_url = "https://www.mbn.co.kr/player/mbnStreamAuth_new_live.mbn?vod_url=https://hls-live.mbn.co.kr/mbn-on-air/600k/playlist.m3u8"
        response = requests.get(auth_url)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f'Error updating MBN link: {str(e)}')
    return None

def update_kr_txt_file():  # 函数名修改：明确操作kr.txt，而非m3u
    # 关键修改2：读取目标改为kr.txt（CSV格式：频道名,链接）
    try:
        # 读取kr.txt所有行，存入列表（每行对应一个频道的“名+链接”）
        with open('kr.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()  # lines是列表，每个元素是一行字符串（如"KBS1,https://old-link.m3u8\n"）
    except FileNotFoundError:
        print(f'Error: kr.txt文件未找到，请确保文件在脚本同一文件夹下')
        return
    except Exception as e:
        print(f'Error reading kr.txt: {str(e)}')
        return

    # 更新KBS链接（核心逻辑修改：按行解析CSV，匹配频道名更新）
    kbs_links = update_kbs_links()
    if kbs_links:
        # 遍历kr.txt的每一行，逐行处理
        updated_lines = []
        for line in lines:
            line = line.strip()  # 去除行首尾的空格、换行符（避免空行/空格干扰）
            if not line:  # 跳过空行
                updated_lines.append('\n')
                continue
            
            # 关键：分割“频道名”和“链接”（CSV格式用逗号分隔）
            # split(',', 1)表示只分割一次，避免链接中含逗号的情况（虽然少见，但更稳健）
            channel_part, url_part = line.split(',', 1) if ',' in line else (line, '')
            
            # 若当前行的频道名在kbs_links中（即KBS1/KBS2），且有新链接，则替换
            if channel_part in kbs_links and kbs_links[channel_part]:
                new_line = f'{channel_part},{kbs_links[channel_part]}\n'  # 拼接新的“频道名,新链接”
                updated_lines.append(new_line)
                print(f'Updated {channel_part}: {kbs_links[channel_part]}')
            else:
                # 非KBS1/KBS2频道，或无新链接，保留原行内容
                updated_lines.append(line + '\n')

        # 关键修改3：写入更新后的内容到kr.txt（覆盖原文件）
        with open('kr.txt', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)  # 批量写入所有行

    # （可选）若kr.txt要更新MBN，可添加以下逻辑（和KBS逻辑一致）
    mbn_link = update_mbn_link()
    if mbn_link:
        updated_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                updated_lines.append('\n')
                continue
            channel_part, url_part = line.split(',', 1) if ',' in line else (line, '')
            if channel_part == 'MBN' and mbn_link:
                updated_lines.append(f'MBN,{mbn_link}\n')
                print(f'Updated MBN: {mbn_link}')
            else:
                updated_lines.append(line + '\n')
        with open('kr.txt', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

    print(f'Links updated successfully at {datetime.now()}')

# 关键修改4：执行修改后的函数（操作kr.txt）
if __name__ == '__main__':
    update_kr_txt_file()
