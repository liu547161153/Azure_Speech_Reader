# Azure_Speech_Reader
使用Azure语音生成功能阅读小说的工具，自动识别对话与旁白分开设定讲话人

请自备API，安装好依赖后直接执行

uvicorn app:app --host 127.0.0.1 --port 8751 --reload

直接从txt读取文本需要注意编码，默认是UTF-8

仅支持中文阅读，其他语音请自己修改后台代码

![image](https://github.com/liu547161153/Azure_Speech_Reader/assets/18525855/92e50ac8-1d1d-4911-9669-faf8b69d443a)
