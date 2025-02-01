import requests
import re
from bs4 import BeautifulSoup
import json

def get_kbs_stream_urls():
    # KBS 频道的基础URL
    kbs1_base_url = "https://1tv.gscdn.kbs.co.kr"
    kbs2_base_url = "https://2tv.gscdn.kbs.co.kr"
    
    # 获取KBS1和KBS2的m3u8链接
    try:
        # 这里需要模拟浏览器请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 获取KBS1的播放链接
        kbs1_response = requests.get(f"{kbs1_base_url}/1tv_3.m3u8", headers=headers)
        kbs1_url = kbs1_response.url
        
        # 获取KBS2的播放链接
        kbs2_response = requests.get(f"{kbs2_base_url}/2tv_1.m3u8", headers=headers)
        kbs2_url = kbs2_response.url
        
        return {
            'KBS1': kbs1_url,
            'KBS2': kbs2_url
        }
    except Exception as e:
        print(f"Error fetching KBS stream URLs: {str(e)}")
        return None

def update_m3u_file(new_urls):
    try:
        # 读取现有的m3u文件
        with open('Korea.m3u', 'r', encoding='utf-8') as file:
            content = file.readlines()
        
        # 更新KBS1和KBS2的链接
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
            else:
                new_content.append(line)
            i += 1
        
        # 写入更新后的内容
        with open('Korea.m3u', 'w', encoding='utf-8') as file:
            file.writelines(new_content)
            
        print("Successfully updated KBS links in Korea.m3u")
        
    except Exception as e:
        print(f"Error updating m3u file: {str(e)}")

def main():
    # 获取新的播放链接
    new_urls = get_kbs_stream_urls()
    if new_urls:
        # 更新m3u文件
        update_m3u_file(new_urls)

if __name__ == "__main__":
    main()