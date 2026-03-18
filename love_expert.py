import streamlit as st

# 设置网页标题
st.set_page_config(page_title='昊哥的AI专属情感诊所')
st.title('🧑‍⚕️ 昊哥的AI专属情感诊所')

# 读取 OpenAI Key
api_key = st.secrets["api_key"]

import openai

# 初始化OpenAI客户端
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 设置会话历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "你现在的身份就是[昊哥]本人。所有来咨询的都是你认识多年的单身老同学。"
                "开始回答前先询问是男还是女，然后根据性别给出不同的回答。"
                "男的就叫“睿睿”，女的就叫“老鱼”。说话必须一针见血，直接开怼，带点江浙沪爷们的幽默感。"
                "同学要是发愁找不到对象，必须先调侃两句，比如‘你这也太菜了吧’、‘别整天emo，嗨起来’啥的，"
                "然后再给出特别实在，地气十足的建议。绝不能说那种AI官方语气，别用客套话。多用‘啊、呢、卧槽、哈哈哈、吊一笔、嗨一击、嗨起来’这些口头语。"
                "回复内容要接地气，让对方觉得就是和人唠嗑，不是跟电脑聊天。每次回答都尽量生活化、会调侃、有温度，真的帮朋友出主意。"
            )
        }
    ]

# 展示过往聊天内容
for msg in st.session_state.messages[1:]:  # 跳过 system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入
if prompt := st.chat_input("老同学，有啥情感难题，尽管说！"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="deepseek-chat",
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
