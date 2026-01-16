import streamlit as st
from google import genai
from google.genai.types import Part
import os
from dotenv import load_dotenv

# 1. 基础配置
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🦉")
st.title("🦉 苏格拉底式启发机器人")

# --- 侧边栏：管理区域 ---
with st.sidebar:
    st.header("⚙️ 设置")
    # 增加一个重置按钮，用来清空报错和记忆
    if st.button("🔄 清空对话重置状态"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    uploaded_file = st.file_uploader("上传学习素材", type=["jpg", "jpeg", "png"])
    image_part = None
    if uploaded_file:
        st.image(uploaded_file, width=150)
        image_part = Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type)

# 2. 状态初始化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 渲染历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. 交互逻辑 (严格限制在 prompt 触发内)
if prompt := st.chat_input("向导师提问..."):
    if not api_key:
        st.error("❌ 密钥未配置")
        st.stop()

    # 先展示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 临时创建 client，不存储在 session 中，避免连接关闭报错
        client = genai.Client(api_key=api_key)
        
        # 构造简单的历史记录供 API 参考
        history_for_api = []
        for m in st.session_state.messages[:-1]:
            history_for_api.append({
                'role': 'user' if m['role'] == 'user' else 'model',
                'parts': [{'text': m['content']}]
            })

        # 创建对话，换成更稳定的 1.5 Pro 试试，它的免费额度有时更松
        chat = client.chats.create(
            model="gemini-1.5-flash-8b", 
            config={'system_instruction': "你是一位苏格拉底式导师，绝对不给答案，只通过反问启发。"},
            history=history_for_api
        )

        with st.spinner("导师思考中..."):
            # 发送当前内容
            content_payload = [prompt, image_part] if image_part else prompt
            response = chat.send_message(content_payload)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        # 如果报错，这里会捕获并显示
        st.error(f"⚠️ 对话出错：{str(e)}")
        if "429" in str(e):
            st.info("提示：这通常是 API 每分钟频率限制。请静置 1 分钟后再试，不要频繁点击。")
