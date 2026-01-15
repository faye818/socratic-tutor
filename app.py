import streamlit as st
from google import genai
from google.genai.types import Part
import os
from dotenv import load_dotenv
from PIL import Image
import io

# 1. 密钥获取（兼容本地与云端）
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="多模态苏格拉底导师", page_icon="🦉", layout="centered")
st.title("🦉 多模态苏格拉底导师")
st.caption("可以看图的教育 Agent | 基于 Gemini 2.0 Flash | ZPD 理论演示")

# 2. 初始化：使用列表手动存储对话记忆
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 新增功能区：侧边栏上传图片 ---
with st.sidebar:
    st.header("🖼️ 上传学习素材")
    uploaded_file = st.file_uploader("上传一张图片（例如：错题、实验图）", type=["jpg", "jpeg", "png"])
    image_part = None # 用于存储准备发给 API 的图片数据

    if uploaded_file is not None:
        # 在侧边栏展示预览图
        image = Image.open(uploaded_file)
        st.image(image, caption='已上传素材', use_container_width=True)
        
        # 将图片转换为 API 需要的格式 (MIME type + Raw Bytes)
        image_part = Part.from_bytes(
            data=uploaded_file.getvalue(),
            mime_type=uploaded_file.type
        )
        st.success("图片已就绪，请在右侧输入框提问。")

# --- 主聊天区域 ---

# 3. 渲染历史消息 (只渲染文本部分，避免界面过于混乱)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # 历史记录里只显示文本内容
        st.markdown(msg["content_text"])

# 4. 交互逻辑
if prompt := st.chat_input("向导师提问 (如果上传了图片，导师会结合图片回答)..."):
    if not api_key:
        st.error("❌ 未检测到 API Key，请检查配置。")
        st.stop()
        
    # 展示用户输入
    with st.chat_message("user"):
        st.markdown(prompt)
        # 如果这轮对话带有图片，也在聊天记录里再展示一下
        if image_part:
             st.image(uploaded_file, width=200)
    
    # 准备存储到记忆中的用户消息内容
    user_memory_content = prompt
    if image_part:
        user_memory_content += " [已发送图片素材]"
    st.session_state.messages.append({"role": "user", "content_text": user_memory_content})
    
    try:
        # 每次都创建新鲜的 client
        client = genai.Client(api_key=api_key)
        
        # 将我们手里的 messages 转换为 SDK 需要的纯文本 history 格式
        # (目前 SDK 中 Chat 模式对多模态历史支持有限，我们采取“当前帧多模态，历史帧纯文本”的策略)
        history_for_api = []
        for m in st.session_state.messages[:-1]: # 不包含当前这一条
            history_for_api.append({
                'role': 'user' if m['role'] == 'user' else 'model',
                'parts': [{'text': m['content_text']}]
            })
        
        # 创建对话流
        chat = client.chats.create(
            model="models/gemini-2.0-flash-lite-preview-02-05", # 确保使用支持多模态的最新模型
            config={'system_instruction': "你是一位苏格拉底式导师，绝对不给答案。如果用户提供了图片，请结合图片内容，通过反问启发学生思考图片的含义或解题线索。"},
            history=history_for_api
        )
        
        # --- 核心改动：发送消息时的组装 ---
        # 如果有图片，发送的消息就是一个列表：[文本, 图片]
        # 如果没有图片，就只发送文本
        message_payload = [prompt, image_part] if image_part else prompt
        
        with st.spinner("导师正在观察思考..."):
            response = chat.send_message(message_payload)
        
        # 展示并存储助手回复
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content_text": response.text})
        
    except Exception as e:
        st.error(f"⚠️ 对话出错：{e} (如果是 429 错误，请稍等一分钟)")
