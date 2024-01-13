# Azure_Speech_Reader
使用Azure语音生成功能阅读小说的工具，自动识别对话与旁白分开设定讲话人,对话可以识别情绪，让阅读更生动
识别情绪的功能需要模型，我已经训练好了，请自行下载然后放入model文件夹里：https://drive.google.com/file/d/1St1TfcXcLeso_XctVSxLQSmxmgRIo_al/view?usp=drive_link
想自己训练请参考该项目:https://github.com/jie12366/sentiment_analysis
请自备API，安装好依赖后直接执行

uvicorn app:app --host 127.0.0.1 --port 8751 --reload

直接从txt读取文本需要注意编码，默认是UTF-8

仅支持中文阅读，其他语音请自己修改后台代码，要是没有读完，可以点保存文本方便下次接着读


在Google Colab打开DEMO：[https://colab.research.google.com/github/liu547161153/Azure_Speech_Reader/blob/main/%E9%98%85%E8%AF%BB%E5%99%A8DEMO.ipynb](https://colab.research.google.com/drive/1F2FLKixrbr49cqtiAJmC7V2lQepELc8c?usp=sharing)

![image](https://github.com/liu547161153/Azure_Speech_Reader/assets/18525855/92e50ac8-1d1d-4911-9669-faf8b69d443a)
