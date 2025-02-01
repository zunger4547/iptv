import requests
import json

def get_kbs_stream_urls():
    try:
        # 设置API请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.kbs.co.kr'
        }
        
        # 获取KBS1的播放链接
        kbs1_response = requests.get('https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/11', headers=headers)
        kbs1_response.raise_for_status()
        kbs1_data = kbs1_response.json()
        kbs1_url = kbs1_data['channel_item'][0]['service_url']
        
        # 获取KBS2的播放链接
        kbs2_response = requests.get('https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/12', headers=headers)
        kbs2_response.raise_for_status()
        kbs2_data = kbs2_response.json()
        kbs2_url = kbs2_data['channel_item'][0]['service_url']
        
        return {
            'KBS1': kbs1_url,
            'KBS2': kbs2_url
        }
    except Exception as e:
        print(f"Error fetching KBS stream URLs: {str(e)}")
        return None

def get_mbn_stream_url():
    try:
        # 获取MBN的认证链接
        auth_url = "https://www.mbn.co.kr/player/mbnStreamAuth_new_live.mbn?vod_url=https://hls-live.mbn.co.kr/mbn-on-air/600k/playlist.m3u8"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.mbn.co.kr'
        }
        
        response = requests.get(auth_url, headers=headers)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching MBN stream URL: {str(e)}")
        return None

def update_m3u_file(new_urls):
    try:
        # 读取现有的m3u文件
        with open('Korea.m3u', 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        # 更新KBS1、KBS2和MBN的链接
        new_content = []
        i = 0
        while i < len(content):
            line = content[i]
            if 'KBS 1TV' in line:
                new_content.append(line)
                i += 1
                if i < len(content):
                    new_content.append(new_urls['KBS1'] + '\n')
            elif 'KBS 2TV' in line:
                new_content.append(line)
                i += 1
                if i < len(content):
                    new_content.append(new_urls['KBS2'] + '\n')
            elif 'MBN' in line:
                new_content.append(line)
                i += 1
                if i < len(content):
                    new_content.append(new_urls['MBN'] + '\n')
            else:
                new_content.append(line)
            i += 1
        
        # 写入更新后的内容
        with open('Korea.m3u', 'w', encoding='utf-8') as file:
            file.writelines(new_content)
            
        print("Successfully updated KBS and MBN links in Korea.m3u")
        
    except Exception as e:
        print(f"Error updating m3u file: {str(e)}")

def main():
    # 获取新的播放链接
    kbs_urls = get_kbs_stream_urls()
    mbn_url = get_mbn_stream_url()
    
    if kbs_urls and mbn_url:
        # 合并所有URL
        all_urls = {
            'KBS1': kbs_urls['KBS1'],
            'KBS2': kbs_urls['KBS2'],
            'MBN': mbn_url
        }
        # 更新m3u文件
        update_m3u_file(all_urls)

if __name__ == "__main__":
    main()