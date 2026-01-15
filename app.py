import streamlit as st
from google import genai
import os
from dotenv import load_dotenv  # 导入翻译官

# 1. 加载秘密文件
load_dotenv()
# 从系统环境变量里取 Key，如果取不到则为空
api_key = os.getenv("GEMINI_API_KEY")

# 2. 页面配置
st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🎓")

# 3. 初始化 Gemini (使用刚才读到的秘密 Key)
if "client" not in st.session_state:
    if not api_key:
        st.error("未找到 API Key，请检查 .env 文件是否配置正确。")
        st.stop()
    
    st.session_state.client = genai.Client(api_key=api_key)
    # ... 后面的代码保持不变import streamlit as st
from google import genai
import os

# 1. 页面配置
st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🎓")
st.title("🎓 苏格拉底式启发机器人")
st.caption("基于 ZPD 理论设计的教育 Agent | 清华教育学项目演示")

# 2. 初始化 Gemini 客户端
# 面试演示建议：将 Key 存入 Streamlit 的 Secrets 中
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key="你的_新_API_KEY")
    st.session_state.chat = st.session_state.client.chats.create(
        model="models/gemini-flash-lite-latest",
        config={'system_instruction': "你是一位苏格拉底式导师，绝对不给答案，只做启发式提问。"}
    )

# 3. 聊天记录初始化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 展示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 用户输入
if prompt := st.chat_input("向导师提问（例如：为什么冰会浮在水面上？）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取 AI 回复
    response = st.session_state.chat.send_message(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})