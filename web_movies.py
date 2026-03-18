import pandas as pd
import streamlit as st

# ----------------------------
# Page / Style
# ----------------------------
st.set_page_config(
    page_title="豆瓣电影 Top250 看板",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
<style>
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
[data-testid="stMetricValue"] { font-size: 1.8rem; }
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 16px 16px 6px 16px;
}
.title {
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: .5px;
  margin: 0 0 .25rem 0;
}
.subtitle { opacity: .85; margin: 0 0 1rem 0; }
hr { border: none; height: 1px; background: rgba(255,255,255,0.10); margin: 1rem 0; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="card">
  <div class="title">豆瓣电影 Top250 可视化看板</div>
  <div class="subtitle">筛选评分、看分布、看统计、看榜单</div>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Data
# ----------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # 兼容可能出现的空格/字符串评分
    df.columns = [c.strip() for c in df.columns]
    if "评分" in df.columns:
        df["评分"] = pd.to_numeric(df["评分"], errors="coerce")
    return df


df = load_data("movies.csv")

required_cols = ["名称", "评分", "引言"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"movies.csv 缺少列：{missing}。当前列为：{list(df.columns)}")
    st.stop()

df = df.dropna(subset=["评分"]).copy()

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("筛选条件")

min_val = float(df["评分"].min())
max_val = float(df["评分"].max())

score_range = st.sidebar.slider(
    "评分范围",
    min_value=float(max(0.0, (min_val // 0.1) * 0.1)),
    max_value=float(min(10.0, ((max_val // 0.1) + 1) * 0.1)),
    value=(float(max(0.0, min_val)), float(min(10.0, max_val))),
    step=0.1,
)

keyword = st.sidebar.text_input("名称关键词（可选）", value="").strip()

filtered = df[(df["评分"] >= score_range[0]) & (df["评分"] <= score_range[1])][
    ["名称", "评分", "引言"]
].copy()

if keyword:
    filtered = filtered[filtered["名称"].astype(str).str.contains(keyword, case=False, na=False)]

filtered = filtered.sort_values(["评分", "名称"], ascending=[False, True]).reset_index(drop=True)

# ----------------------------
# Top metrics
# ----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("符合条件电影数", f"{len(filtered):,}")
c2.metric("平均评分", f"{filtered['评分'].mean():.2f}" if len(filtered) else "—")
c3.metric("最高评分", f"{filtered['评分'].max():.1f}" if len(filtered) else "—")
c4.metric("最低评分", f"{filtered['评分'].min():.1f}" if len(filtered) else "—")

st.markdown("<hr/>", unsafe_allow_html=True)

# ----------------------------
# Histogram + Top list
# ----------------------------
left, right = st.columns([1.2, 1])

with left:
    st.subheader("评分直方图")

    if len(filtered) == 0:
        st.info("当前筛选条件下没有数据。")
    else:
        # 以 0.1 为粒度做直方图
        bin_size = 0.1
        start = float((filtered["评分"].min() // bin_size) * bin_size)
        end = float(((filtered["评分"].max() // bin_size) + 1) * bin_size)

        bins = [round(start + i * bin_size, 1) for i in range(int(round((end - start) / bin_size)) + 1)]
        if len(bins) < 2:
            bins = [round(start, 1), round(start + bin_size, 1)]

        cats = pd.cut(filtered["评分"], bins=bins, include_lowest=True, right=False)
        hist = (
            cats.value_counts()
            .sort_index()
            .rename_axis("区间")
            .reset_index(name="数量")
        )

        hist["区间"] = hist["区间"].astype(str)
        hist = hist.set_index("区间")

        st.bar_chart(hist["数量"], height=260)

with right:
    st.subheader("Top 榜单（按评分）")
    top_n = st.slider("Top N", min_value=5, max_value=50, value=10, step=1)
    st.dataframe(
        filtered.head(top_n),
        use_container_width=True,
        hide_index=True,
        column_config={
            "名称": st.column_config.TextColumn("名称", width="medium"),
            "评分": st.column_config.NumberColumn("评分", format="%.1f", width="small"),
            "引言": st.column_config.TextColumn("引言", width="large"),
        },
        height=260,
    )

st.markdown("<hr/>", unsafe_allow_html=True)

# ----------------------------
# Beautified table
# ----------------------------
st.subheader("完整列表")

st.caption(
    f"当前筛选：评分 {score_range[0]:.1f} ~ {score_range[1]:.1f}"
    + (f"，关键词：{keyword}" if keyword else "")
)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
    column_config={
        "名称": st.column_config.TextColumn("名称", width="medium"),
        "评分": st.column_config.NumberColumn("评分", format="%.1f", width="small"),
        "引言": st.column_config.TextColumn("引言", width="large"),
    },
    height=520,
)

st.download_button(
    "下载当前筛选结果 CSV",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="movies_filtered.csv",
    mime="text/csv",
)