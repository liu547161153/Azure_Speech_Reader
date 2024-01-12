import os
from dotenv import load_dotenv
from Azure_text2speech import Azure_text2speech
from fastapi import FastAPI, Request, responses
from fastapi.middleware.cors import CORSMiddleware
# import cntext as ct
use_chat_style = True  # 全局变量

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，或者您可以指定特定的来源列表
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，或者指定特定的方法列表（如 ["GET", "POST"]）
    allow_headers=["*"],  # 允许所有头部，或者指定特定的头部列表
)
# 加载 .env 文件中的环境变量
load_dotenv()
# 从环境变量中获取值
api_key = os.getenv('API_KEY')
region = os.getenv('REGION')
azure_tts = Azure_text2speech(api_key, region)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/tts")
async def read_item(request: Request):
    body = await request.json()
    media_type = 'audio/mpeg'
    params = body
    global use_chat_style # 初始设置为True，以便第一个对话使用"chat"样式
    text = params['text'].strip()
    rate = body.get('rate', 1.0)
    audio_data_combined = b''  # 假设音频数据是字节串，可以进行拼接

    segments = text.split('“')  # 以对话开始符号分割文本
    for segment in segments:
        if '”' in segment:
            # 对话部分
            dialogue, rest = segment.split('”', 1)
            dialogue = f'“{dialogue}”'
            # 在对话末尾添加短暂的暂停
            dialogue_with_pause = dialogue + "<break time='500ms'/>"  # 500毫秒的暂停
            if use_chat_style:
                audio_data = await azure_tts.text_to_speech(dialogue_with_pause, voice_name="zh-CN-XiaoxuanNeural", role="YoungAdultmale", rate=float(rate)+0.1)
                use_chat_style = False  # 下一个对话将使用默认样式
            else:
                audio_data = await azure_tts.text_to_speech(dialogue_with_pause, voice_name="zh-CN-XiaoxuanNeural", role="YoungAdultFemale", rate=float(rate)+0.1)  # 使用默认样式
                use_chat_style = True  # 下一个对话将使用"chat"样式

            audio_data_combined += audio_data if audio_data else b''

            # 处理对话后的旁白部分
            if rest:
                audio_data = await azure_tts.text_to_speech(rest, voice_name="zh-CN-XiaoxuanNeural", role="OlderAdultFemale", rate=float(rate))
                audio_data_combined += audio_data if audio_data else b''
        else:
            # 旁白部分
            audio_data = await azure_tts.text_to_speech(segment, voice_name="zh-CN-XiaoxuanNeural", role="OlderAdultFemale", rate=float(rate))
            audio_data_combined += audio_data if audio_data else b''

    if audio_data_combined:
        return responses.Response(content=audio_data_combined, media_type=media_type)
    else:
        return {"error": "Azure TTS failed"}

    # if 'rate' in params.keys():
    #     # print(params['rate'], type(params['rate']))
    #     rate = int(params['rate'])
    #     rate = f'+{rate * 2}%'
    #     communicate = edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural', rate=rate)
    # else:
    # communicate = edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural')
    #
    # return responses.StreamingResponse(
    #     content=tts_stream2(communicate),
    #     media_type=media_type
    # )

#有点鸡肋了
# async def analyze_text_and_choose_style(text):
#     # 加载情感分析字典
#     diction = ct.load_pkl_dict('DUTIR.pkl')['DUTIR']
#     # 进行情感分析
#     emotion_result = ct.sentiment(text, diction, 'chinese')
#
#     # 情绪到语音风格的映射
#     emotion_to_style = {
#         '乐_num': 'cheerful',
#         '好_num': 'friendly',
#         '怒_num': 'angry',
#         '哀_num': 'sad',
#         '惧_num': 'fearful',
#         '恶_num': 'disgruntled',
#         '惊_num': 'fearful'  # 如果 Azure 支持 'surprised'
#     }
#
#     # 移除无关的键
#     irrelevant_keys = ['stopword_num', 'word_num', 'sentence_num']
#     for key in irrelevant_keys:
#         if key in emotion_result:
#             del emotion_result[key]
#
#     # 选择数值最高的情绪
#     dominant_emotion = max(emotion_result, key=emotion_result.get)
#
#     # 返回对应的语音风格
#     voice_style = emotion_to_style.get(dominant_emotion, 'chat')  # 如果没有匹配的情绪，则默认返回 'chat'
#     print(voice_style)
#     return voice_style



