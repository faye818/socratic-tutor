import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# 1. 智能加载 Key
load_dotenv() # 本地尝试加载 .env
# 优先从 Streamlit Secrets 读取（云端），如果没找到则从系统环境读取（本地）
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🎓")
st.title("🎓 苏格拉底式启发机器人")
st.caption("基于 ZPD 理论设计的教育 Agent | 清华教育学项目演示")

# 2. 严谨初始化 (确保 chat 对象一定存在)
if "chat" not in st.session_state:
    if not api_key:
        st.error("❌ 错误：未检测到 API Key。请在 Streamlit 云端设置 Secrets 或检查本地 .env 文件。")
        st.stop()
    
    try:
        # 初始化客户端
        client = genai.Client(api_key=api_key)
        # 创建并存储对话对象
        st.session_state.chat = client.chats.create(
            model="models/gemini-flash-lite-latest",
            config={'system_instruction': "你是一位苏格拉底式导师，绝对不给答案，只通过反问启发学生。"}
        )
        st.session_state.messages = []
    except Exception as e:
        st.error(f"❌ 初始化失败：{e}")
        st.stop()

# 3. 聊天逻辑 (确保使用 session_state 里的对象)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("向导师提问..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 使用初始化好的 chat 对象发送消息
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"⚠️ 对话出错：{e}")
