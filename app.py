from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mytts import read_item
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 如果您的 CSS 和 JS 文件在 html 文件夹下的 static 子文件夹中
app.mount("/static", StaticFiles(directory="html/static"), name="static")

@app.get("/")
async def root():
    # 直接返回 HTML 文件
    return FileResponse('html/index.html')


# 将 TTS 路由添加到应用中
app.add_api_route('/tts', read_item, methods=['POST'])

#uvicorn app:app --host 127.0.0.1 --port 8751 --reload