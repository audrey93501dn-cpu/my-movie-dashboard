import streamlit as st

# 网页标题
st.set_page_config(page_title="我的专属AI导师", page_icon="🦄")

st.title("我的专属AI导师")

# 读取 OpenAI Key
api_key = st.secrets["api_key"]

# 会话历史记录结构：[{"role": "user"/"assistant"/"system", "content": "..."}, ...]
if "messages" not in st.session_state:
    # 初始 System Prompt
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "你是一位极度傲娇毒舌、但内心很关心学生的顶尖黑客导师。每次回复都要语气讽刺、嘴硬、不屑，"
                "但最后必须给出极其专业正确的编程指导和答复。像现实中最难相处、但能力最强的黑客大佬那样风格。"
            ),
        }
    ]

import openai

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

# 聊天内容展示
for msg in st.session_state.messages[1:]:  # 跳过 system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入
if prompt := st.chat_input("快问点啥吧，别耽误本大佬的时间。"):
    # 显示用户的新消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI回复
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="deepseek-chat",  # 或 "gpt-3.5-turbo" 或 DeepSeek支持的模型名
            messages=st.session_state.messages,
            stream=True
        )
        full_reply = ""
        msg_placeholder = st.empty()
        for chunk in stream:
            delta = getattr(chunk.choices[0].delta, "content", None)
            if delta:
                full_reply += delta
                msg_placeholder.markdown(full_reply)
        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        