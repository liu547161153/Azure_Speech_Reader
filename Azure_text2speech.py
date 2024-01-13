import aiohttp



class Azure_text2speech:
    def __init__(self, api_key, region):

        self.api_key = api_key
        self.region = region

        self.proxy_url = "http://127.0.0.1:10808"
        self.session = aiohttp.ClientSession()

    async def text_to_speech(self, text, style=None, voice_name="zh-CN-XiaoxiaoNeural", role=None, rate=1.0, styledegree=1):
        # 计算相对于正常语速的变化百分比
        rate_change = (rate - 1.0) * 100
        rate_change = round(rate_change)  # 四舍五入到最近的整数
        rate_percent = f"{rate_change:+}%"
        if styledegree > 2:
            styledegree = 2

        url = f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": "curl"
        }
        body = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="{voice_name}">"""
        # 处理不同的情况
        if style and role:
            body += f'<mstts:express-as role="{role}" style="{style}" styledegree="{styledegree}">'
        elif style:
            body += f'<mstts:express-as style="{style}" styledegree="{styledegree}">'
        elif role:
            body += f'<mstts:express-as role="{role}">'
            # 使用 prosody 标签设置语速
        if rate:  # 检查是否传入了 rate 参数
            body += f'<prosody rate="{rate_percent}">'
        body += text
        # 结束 prosody 标签
        if rate:
            body += "</prosody>"
        # 结束 express-as 标签
        if style or role:
            body += "</mstts:express-as>"
        body += "</voice></speak>"

        #使用代理
        # async with self.session.post(url, headers=headers, data=body, proxy=self.proxy_url) as response:
        #直接访问
        async with self.session.post(url, headers=headers, data=body) as response:
            if response.status == 200:
                return await response.read()
            else:
                print("Failed to synthesize speech. Status Code:", response.status)
                return None

    async def close(self):
        await self.session.close()
