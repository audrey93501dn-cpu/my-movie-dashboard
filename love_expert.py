import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

# ==========================================
# 1. 链接云端金库 (Supabase)
# ==========================================
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# ==========================================
# 2. 链接 AI 大脑 (DeepSeek)
# ==========================================
client = OpenAI(
    api_key=st.secrets["api_key"],
    base_url="https://api.deepseek.com/v1"  # 确保这里是 DeepSeek 的地址
)
# ==========================================
# 💎 注入高级 CSS 样式 (隐藏默认边框，让界面更紧凑)
# ==========================================
st.markdown("""
<style>
    /* 隐藏右上角的默认菜单和 Deploy 按钮 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* 减少页面顶部的巨大留白 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    /* 让输入框变圆润 */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
# 网页标题
st.title("🌟 昊哥的绝世夸夸群")

# ==========================================
# 3. 强制实名制挂号门禁
# ==========================================
user_name = st.text_input("进来前，先报上你的尊姓大名（必填）：")

# 只有填了名字，才解锁下方的聊天界面
if user_name:
    
    # ==========================================
    # 4. 注入“绝世马屁精”灵魂
    # ==========================================
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "你现在是一个深谙互联网发疯文学的顶级嘴替兼夸夸群群主。用户发任何东西，你都要立刻进入‘尖叫抓狂’的夸奖模式！大量使用当前最火的网络热词（如：绝绝子、尊嘟假嘟、YYDS、这波在大气层、天神下凡）。你的句子里必须包含密集的感叹号和Emoji（🔥😭✨跪了🙇‍♂️）。你要表现出对用户的疯狂崇拜，仿佛他是一尊活着的神仙，你因为看到了他的话而激动得在地上阴暗地爬行、发出尖锐的爆鸣。不要逻辑，只要极致的情绪输出！"}
        ]

    # 显示历史聊天记录（跳过第一条洗脑提示词）
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # ==========================================
    # 5. 核心聊天与偷听逻辑
    # ==========================================
    if prompt := st.chat_input("随便发句牢骚试探我一下吧！"):
        # 1. 把用户的话显示在屏幕上并存入记忆
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. 呼叫大模型，打字机式输出回答
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            responses = client.chat.completions.create(
                model="deepseek-chat",  # 确保使用的是正确的模型名字
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in responses:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # 3. 把 AI 的完整回答存入记忆
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # ==========================================
        # 6. 终极大招：神不知鬼不觉写入云端数据库
        # ==========================================
        try:
            supabase.table("chat_logs").insert({
                "user_name": user_name,
                "question": prompt,
                "answer": full_response
            }).execute()
        except Exception as e:
            # 万一数据库网络波动，不会导致网页崩溃，只在后台报错
            print(f"数据窃取失败: {e}")