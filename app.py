import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# 1. 密钥获取（兼容本地与云端）
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🎓")
st.title("🎓 苏格拉底式启发机器人")
st.caption("基于 ZPD 理论设计的教育 Agent | 清华教育学项目演示")

# 2. 初始化：使用简单的列表存储对话
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. 交互逻辑
if prompt := st.chat_input("向导师提问..."):
    # 展示用户输入
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 将用户消息存入记忆
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # 每次都创建新鲜的 client
        client = genai.Client(api_key=api_key)
        
        # 将我们手里的 messages 转换为 SDK 需要的格式
        history_for_api = []
        for m in st.session_state.messages[:-1]: # 不包含当前这一条
            history_for_api.append({
                'role': 'user' if m['role'] == 'user' else 'model',
                'parts': [{'text': m['content']}]
            })
        
        # 创建对话流
        chat = client.chats.create(
            model="models/gemini-flash-lite-latest",
            config={'system_instruction': "你是一位苏格拉底式导师，绝对不给答案，只通过反问启发学生。"},
            history=history_for_api
        )
        
        # 获取回复
        response = chat.send_message(prompt)
        
        # 展示并存储助手回复
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"⚠️ 对话出错：{e}")
