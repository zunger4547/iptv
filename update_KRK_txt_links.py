def update_kbs_links():
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
    
    # 先访问主页获取cookies
    session = requests.Session()
    
    # 首先访问KBS主页
    home_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        # 先访问主页获取cookies
        session.get('https://www.kbs.co.kr/', headers=home_headers, verify=False, timeout=10)
        
        # 再请求API
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.kbs.co.kr/',
            'Origin': 'https://www.kbs.co.kr',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        for channel_name, channel_code in kbs_channels.items():
            auth_url = f'https://cfpwwwapi.kbs.co.kr/api/v1/landing/live/channel_code/{channel_code}'
            
            response = session.get(auth_url, headers=api_headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # 检查service_url是否在别的位置
                if 'channel_item' in data and len(data['channel_item']) > 0:
                    # 可能链接在别的地方
                    print(f"{channel_name} 响应完整数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    
                    # 尝试获取service_url
                    service_url = data['channel_item'][0].get('service_url', '')
                    if service_url:
                        kbs_links[channel_name] = service_url
                    else:
                        # 可能在其他字段
                        print(f"{channel_name} service_url为空，检查其他字段")
                        
    except Exception as e:
        print(f"错误: {e}")
    
    return kbs_links
