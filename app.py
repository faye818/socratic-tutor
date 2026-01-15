import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# 1. 密钥获取逻辑（本地读取 .env，云端读取 Secrets）
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="苏格拉底 AI 导师", page_icon="🎓")
st.title("🎓 苏格拉底式启发机器人")
st.caption("基于 ZPD 理论设计的教育 Agent | 清华教育学项目演示")

# 2. 初始化：仅在 Session State 中存储聊天记录（记忆）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 核心：每次运行都创建新鲜的 client 和 chat 实例
# 这样可以彻底避免 "client has been closed" 报错
if not api_key:
    st.error("❌ 未检测到 API Key，请检查配置。")
    st.stop()

client = genai.Client(api_key=api_key)

# 将 session_state 里的消息格式化为 SDK 需要的 history 格式
# 注意：新版 SDK 的 history 结构通常是列表对象
chat = client.chats.create(
    model="models/gemini-flash-lite-latest",
    config={
        'system_instruction': "你是一位苏格拉底式导师，绝对不给答案，只通过反问启发学生。你的教学目标是引导学生进入最近发展区（ZPD）。",
        'temperature': 0.7
    },
    history=st.session_state.messages # 这里注入“记忆”
)

# 4. 界面渲染：展示历史对话
for msg in st.session_state.messages:
    # 转换角色名称以匹配 Streamlit 的 chat_message
    st_role = "assistant" if msg.role == "model" else "user"
    with st.chat_message(st_role):
        # 假设 msg.parts[0].text 是新版 SDK 的消息结构
        # 如果报错，请尝试直接访问文本内容
        text_content = msg.parts[0].text if hasattr(msg, 'parts') else str(msg)
        st.markdown(text_content)

# 5. 交互逻辑
if prompt := st.chat_input("向导师提问（例如：为什么冰会浮在水面上？）"):
    # 立即展示用户输入
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        # 发送消息
        response = chat.send_message(prompt)
        
        # 展示导师回复
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # 重要：更新 session_state 里的 history，供下一次运行使用
        # chat.history 会包含最新的这一轮对话
        st.session_state.messages = chat.history
        
    except Exception as e:
        st.error(f"⚠️ 对话出错：{e}")
        if "429" in str(e):
            st.warning("提示：免费配额已达上限，请稍等一分钟再试。")
