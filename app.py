# -*- coding: utf-8 -*-
"""高考志愿填报助手 - Streamlit版（还原HTML设计）"""
import streamlit as st
import json
import os
import html as html_lib

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="高考志愿填报助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_universities():
    data_path = os.path.join(os.path.dirname(__file__), "universities_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

universities = load_universities()

# 建立名称→数据索引，方便查询
uni_index = {u["name"]: u for u in universities}

MAJOR_CATEGORIES = {
    "工学": ["计算机科学与技术", "软件工程", "人工智能", "电子信息工程", "通信工程", "自动化", "机械工程", "土木工程", "建筑学", "材料科学与工程", "化学工程", "电气工程", "航空航天工程", "生物工程", "环境工程"],
    "理学": ["数学", "物理学", "化学", "生物科学", "天文学", "地理科学", "地质学", "统计学", "心理学", "大气科学"],
    "医学": ["临床医学", "口腔医学", "中医学", "药学", "护理学", "公共卫生", "基础医学", "法医学"],
    "经济学": ["经济学", "金融学", "国际经济与贸易", "财政学", "保险学", "统计学", "金融工程"],
    "管理学": ["工商管理", "会计学", "财务管理", "市场营销", "人力资源管理", "行政管理", "物流管理", "旅游管理"],
    "法学": ["法学", "知识产权", "社会学", "政治学", "外交学", "公安学"],
    "文学": ["汉语言文学", "外国语言文学", "新闻学", "传播学", "广告学", "编辑出版学"],
    "教育学": ["教育学", "学前教育", "小学教育", "特殊教育", "教育技术学"],
    "艺术学": ["美术学", "设计学", "音乐学", "舞蹈学", "戏剧影视", "动画"],
    "农学": ["农学", "园艺", "植物保护", "动物医学", "林学", "水产养殖学"]
}

PROVINCES = sorted(set(u["province"] for u in universities))
TIERS = ["985", "211", "双一流", "公办本科", "民办本科", "公办专科"]

# ============================================================
# DeepSeek API
# ============================================================
def call_deepseek(messages, api_key=None):
    import httpx
    if api_key is None:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return "请先配置 DeepSeek API Key。在 Streamlit Cloud 的 Secrets 中添加 `DEEPSEEK_API_KEY`。"
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"model": "deepseek-chat", "messages": messages, "stream": False, "temperature": 0.7, "max_tokens": 2000}
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API调用失败: {str(e)}"

# ============================================================
# 自定义CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', system-ui, sans-serif;
}
.stApp { background: #f8fafc; }
header[data-testid="stHeader"] { display: none; }
div[data-testid="stToolbar"] { display: none; }
section[data-testid="stSidebar"] { display: none; }
div[data-testid="stSidebarUserContent"] { display: none; }
div[data-testid="collapsedControl"] { display: none; }
.main .block-container {
    padding-top: 0;
    padding-bottom: 1rem;
    max-width: 1100px;
}
button[data-testid="stDeployButton"] { display: none; }
#MainMenu { display: none; }
footer { display: none; }
[data-testid="stAppViewContainer"] > section:first-child { display: none; }

/* === 院校详情按钮样式覆盖 === */
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }

/* === Tab === */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    padding: 12px 20px;
    background: none;
    border: none;
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}
.stTabs [data-baseweb="tab"]:hover { color: #4f46e5; background: none; }
.stTabs [aria-selected="true"] {
    color: #4f46e5 !important;
    font-weight: 600;
    border-bottom: 3px solid #4f46e5 !important;
    background: none !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* === 面板 === */
.panel-white {
    background: white;
    border-radius: 16px;
    border: 1px solid #f1f5f9;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.panel-title { font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.panel-desc { font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px; }

/* === 输入框 === */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 8px !important;
    border: 1px solid #d1d5db !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.1) !important;
}

/* === 主按钮 === */
.stButton > button[data-testid="baseButton-primary"],
.stButton > button[kind="primary"] {
    background: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.25) !important;
}
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: #4338ca !important;
    transform: translateY(-1px) !important;
}

/* === 统计卡片 === */
.stat-card {
    background: linear-gradient(135deg, #312e81 0%, #4f46e5 50%, #0ea5e9 100%);
    color: white; padding: 24px 16px; border-radius: 14px; text-align: center;
    box-shadow: 0 4px 15px rgba(79,70,229,0.2);
}
.stat-number { font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }
.stat-label { font-size: 0.85rem; opacity: 0.85; margin-top: 4px; }

/* === 院校卡片 === */
.uni-card {
    background: white; border: 1px solid #f1f5f9; border-radius: 14px;
    padding: 18px; transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.uni-card:hover {
    transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.08); border-color: #c7d2fe;
}
.uni-name { font-weight: 700; font-size: 1rem; color: #1e293b; margin-bottom: 6px; }
.uni-meta { font-size: 0.8rem; color: #64748b; margin-bottom: 8px; }
.uni-features { font-size: 0.78rem; color: #94a3b8; }

/* === 标签 === */
.tag { display:inline-block; padding:2px 10px; border-radius:9999px; font-size:0.72rem; font-weight:600; letter-spacing:0.3px; }
.tag-985 { background:#fef3c7; color:#92400e; }
.tag-211 { background:#dbeafe; color:#1e40af; }
.tag-double { background:#d1fae5; color:#065f46; }
.tag-type { background:#f1f5f9; color:#475569; }

/* === 冲稳保 === */
.tip-card { border-radius:14px; padding:20px; border:1px solid; }
.tip-chong { background:linear-gradient(135deg,#fef2f2,#fff7ed); border-color:#fecaca; }
.tip-wen { background:linear-gradient(135deg,#eff6ff,#eef2ff); border-color:#bfdbfe; }
.tip-bao { background:linear-gradient(135deg,#f0fdf4,#ecfdf5); border-color:#bbf7d0; }
.tip-title-chong { color:#dc2626; font-weight:700; font-size:0.9rem; margin-bottom:8px; }
.tip-title-wen { color:#2563eb; font-weight:700; font-size:0.9rem; margin-bottom:8px; }
.tip-title-bao { color:#16a34a; font-weight:700; font-size:0.9rem; margin-bottom:8px; }
.tip-text { color:#64748b; font-size:0.8rem; line-height:1.6; }

/* === 聊天气泡 === */
.chat-user {
    background:#4f46e5; color:white; padding:12px 18px;
    border-radius:18px 18px 4px 18px; margin:8px 0; max-width:80%; margin-left:auto;
    font-size:0.9rem; line-height:1.6;
}
.chat-ai {
    background:#f1f5f9; color:#1e293b; padding:12px 18px;
    border-radius:18px 18px 18px 4px; margin:8px 0; max-width:85%;
    font-size:0.9rem; line-height:1.6;
}
.chat-ai p { margin:0.4em 0; }
.chat-ai h1,.chat-ai h2,.chat-ai h3 { font-weight:600; margin:0.6em 0 0.3em; }
.chat-ai ul,.chat-ai ol { margin:0.4em 0; padding-left:1.4em; }
.chat-ai code { background:rgba(0,0,0,0.06); padding:0.1em 0.3em; border-radius:3px; font-size:0.9em; }
.chat-ai strong { font-weight:600; }

/* === 推荐结果 === */
.recommend-result h1,.recommend-result h2,.recommend-result h3 { font-weight:700; color:#1e293b; margin-top:1em; }
.recommend-result h3 { font-size:1.05rem; border-left:3px solid #4f46e5; padding-left:10px; }
.recommend-result ul { padding-left:1.4em; }
.recommend-result li { margin:0.3em 0; font-size:0.9rem; color:#475569; }
.recommend-result strong { color:#1e293b; }
.recommend-result p { font-size:0.9rem; color:#475569; line-height:1.7; }

/* === 院校详情面板 === */
.uni-detail-panel {
    background: white; border-radius: 16px; border: 1px solid #e2e8f0;
    padding: 24px; margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}
.uni-detail-header {
    background: linear-gradient(135deg, #312e81 0%, #4f46e5 40%, #0ea5e9 100%);
    color: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 16px;
    display: flex; justify-content: space-between; align-items: center;
}
.uni-detail-name { font-size: 1.3rem; font-weight: 700; }
.uni-detail-tags { display: flex; gap: 6px; margin-top: 6px; }

/* === 页脚 === */
.app-footer {
    text-align:center; padding:20px 0 8px; color:#94a3b8; font-size:0.78rem;
    border-top:1px solid #f1f5f9; margin-top:2rem;
}

/* === 查看详情按钮 === */
.stButton > button[data-testid="baseButton-secondary"] {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 顶部导航
# ============================================================
st.markdown(f"""
<style>
.nav-bar {{
    background: linear-gradient(135deg, #312e81 0%, #4f46e5 40%, #0ea5e9 100%);
    padding: 12px 24px; display: flex; align-items: center; justify-content: space-between;
    margin: -1rem -1rem 0 -1rem; position: sticky; top: 0; z-index: 100;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}}
.nav-title {{ color:white; font-size:1.15rem; font-weight:700; letter-spacing:0.5px; display:flex; align-items:center; gap:8px; }}
.nav-badge {{ background:rgba(255,255,255,0.15); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.2); color:white; padding:4px 14px; border-radius:8px; font-size:0.8rem; font-weight:500; }}
</style>
<div class="nav-bar">
    <div class="nav-title">
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="stroke:white"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
        高考志愿填报助手
    </div>
    <div class="nav-badge">收录 {len(universities)} 所高校 · AI驱动</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 智能推荐
# ============================================================
def page_recommend():
    st.markdown('<div class="panel-white">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎯 智能志愿推荐</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-desc">填写你的高考信息，AI将为你生成冲/稳/保院校方案</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        province = st.selectbox("省份", PROVINCES, key="rec_province")
    with c2:
        score = st.number_input("高考分数", min_value=0, max_value=750, value=600, key="rec_score")
    with c3:
        rank = st.number_input("省排名/位次", min_value=1, max_value=1000000, value=10000, key="rec_rank")

    c4, c5 = st.columns(2)
    with c4:
        subject_type = st.selectbox("科类", ["理科/物理类", "文科/历史类", "综合改革"], key="rec_type")
    with c5:
        interest = st.text_input("兴趣方向（选填）", placeholder="例如：计算机、金融", key="rec_interest")

    location_pref = st.text_input("地域偏好（选填）", placeholder="例如：北京、上海、江浙", key="rec_location")

    if st.button("生成推荐方案", type="primary", use_container_width=True):
        with st.spinner("AI正在分析推荐..."):
            prompt = f"""你是一位资深高考志愿填报专家。请根据以下信息，给出冲、稳、保三档院校推荐：

考生信息：
- 高考分数：{score}分
- 省排名：第{rank}名
- 所在省份：{province}
- 科类：{subject_type}
- 兴趣方向：{interest or '无特别偏好'}
- 地域偏好：{location_pref or '无特别偏好'}

请给出：
1. **冲一冲**（3-5所）：录取概率30-50%的院校
2. **稳一稳**（3-5所）：录取概率50-80%的院校
3. **保一保**（3-5所）：录取概率80%以上的院校

对每所院校说明推荐理由，包括该校的优势专业和录取特点。最后给出志愿填报策略建议。"""
            messages = [
                {"role": "system", "content": "你是一位专业的高考志愿填报专家，熟悉各高校招生情况和历年录取分数线。回答要具体、有数据支撑、实用。"},
                {"role": "user", "content": prompt}
            ]
            response = call_deepseek(messages)
            st.session_state["rec_response"] = response

    if "rec_response" in st.session_state:
        st.markdown("---")
        st.markdown("### 推荐方案")
        st.markdown(f'<div class="recommend-result">{st.session_state["rec_response"]}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="tip-card tip-chong"><div class="tip-title-chong">🔴 冲一冲</div><div class="tip-text">选择历年录取位次略高于自己位次的院校，有一定风险但值得尝试，建议占志愿的20-30%。</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="tip-card tip-wen"><div class="tip-title-wen">🔵 稳一稳</div><div class="tip-text">选择与自己位次相当的院校，录取概率较大，是志愿的核心部分，建议占40-50%。</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="tip-card tip-bao"><div class="tip-title-bao">🟢 保一保</div><div class="tip-text">选择历年录取位次明显低于自己位次的院校，确保有学上，建议占20-30%。</div></div>', unsafe_allow_html=True)


# ============================================================
# 院校查询
# ============================================================
def page_university():
    # --- 院校详情弹窗 ---
    # 如果选中了某所院校，先在最顶部显示详情面板
    if "selected_uni" in st.session_state:
        uni_name = st.session_state["selected_uni"]
        u = uni_index.get(uni_name)
        if u:
            # 顶部详情面板
            st.markdown('<div class="uni-detail-panel">', unsafe_allow_html=True)

            # 头部
            tier_cls = "tag-985" if u["tier"] == "985" else "tag-211" if u["tier"] == "211" else "tag-double" if u["tier"] == "双一流" else "tag-type"
            features = u.get("features", [])
            feat_tags = " ".join([f'<span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:9999px;font-size:0.75rem;">{html_lib.escape(f)}</span>' for f in features[:5]])

            st.markdown(f"""
            <div class="uni-detail-header">
                <div>
                    <div class="uni-detail-name">{html_lib.escape(u['name'])}</div>
                    <div style="opacity:0.85;font-size:0.85rem;margin-top:4px;">{html_lib.escape(u['city'])} · {html_lib.escape(u.get('type',''))}</div>
                    <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">{feat_tags}</div>
                </div>
                <span class="tag {tier_cls}" style="font-size:0.85rem;padding:4px 14px;">{u['tier']}</span>
            </div>
            """, unsafe_allow_html=True)

            # 返回按钮 + AI生成按钮
            bc1, bc2 = st.columns([1, 1])
            with bc1:
                if st.button("← 返回列表", key="uni_back"):
                    del st.session_state["selected_uni"]
                    st.rerun()

            # 自动获取或生成AI详情
            cache_key = f"uni_detail_{uni_name}"
            if cache_key not in st.session_state:
                with st.spinner(f"AI正在生成「{uni_name}」的详细介绍..."):
                    prompt = f"""请详细介绍「{u['name']}」（位于{u['city']}，{u['tier']}，{u.get('type','')}）。
特色专业：{', '.join(features[:6])}
请从以下方面介绍：
1. **学校概况**：历史沿革、办学规模、校园特色
2. **优势学科**：王牌专业、学科评估结果
3. **录取情况**：近年分数线大致范围、录取特点
4. **就业深造**：就业率、知名校友、深造比例
5. **校园生活**：住宿条件、社团活动、周边环境
6. **报考建议**：适合什么样的考生"""
                    messages = [
                        {"role": "system", "content": "你是一位资深高校招生咨询专家，回答要具体、准确、实用。如果不确定某些数据，请说明是参考信息。"},
                        {"role": "user", "content": prompt}
                    ]
                    st.session_state[cache_key] = call_deepseek(messages)

            st.markdown(f'<div class="recommend-result">{st.session_state[cache_key]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return  # 显示详情时不显示列表

    # --- 院校列表 ---
    count_985 = sum(1 for u in universities if u["tier"] == "985")
    count_211 = sum(1 for u in universities if u["tier"] == "211")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(universities)}</div><div class="stat-label">收录院校</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{count_985}</div><div class="stat-label">985高校</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{count_211}</div><div class="stat-label">211高校</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="panel-white">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search = st.text_input("搜索院校", placeholder="搜索大学名称、城市、特色专业...", key="uni_search")
    with c2:
        province_filter = st.selectbox("省份筛选", ["全部"] + PROVINCES, key="uni_prov")
    with c3:
        tier_filter = st.selectbox("层次筛选", ["全部"] + TIERS, key="uni_tier")
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = universities
    if search:
        s = search.lower()
        filtered = [u for u in filtered if s in u["name"].lower() or s in u["city"].lower() or any(s in f for f in u.get("features", []))]
    if province_filter != "全部":
        filtered = [u for u in filtered if u["province"] == province_filter]
    if tier_filter != "全部":
        filtered = [u for u in filtered if u["tier"] == tier_filter]

    st.markdown(f'<p style="color:#94a3b8;font-size:0.82rem;margin-bottom:12px;">共找到 <strong style="color:#4f46e5">{len(filtered)}</strong> 所院校</p>', unsafe_allow_html=True)

    page_size = 12
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    page_num = st.number_input("页码", min_value=1, max_value=total_pages, value=1, key="uni_page_num")
    start = (page_num - 1) * page_size
    page_data = filtered[start:start + page_size]

    for row_start in range(0, len(page_data), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx < len(page_data):
                u = page_data[idx]
                tier_cls = "tag-985" if u["tier"] == "985" else "tag-211" if u["tier"] == "211" else "tag-double" if u["tier"] == "双一流" else "tag-type"
                features = u.get("features", [])
                feat_str = " · ".join(features[:3])
                if len(features) > 3:
                    feat_str += f" +{len(features)-3}"
                desc = u.get("desc", "")
                if len(desc) > 50:
                    desc = desc[:50] + "..."
                with col:
                    st.markdown(f"""
                    <div class="uni-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div class="uni-name">{html_lib.escape(u['name'])}</div>
                            <span class="tag {tier_cls}">{u['tier']}</span>
                        </div>
                        <div class="uni-meta">{html_lib.escape(u['city'])} · {html_lib.escape(u.get('type',''))}</div>
                        <div class="uni-features">{html_lib.escape(feat_str)}</div>
                        {"<div style='font-size:0.78rem;color:#94a3b8;margin-top:6px;line-height:1.5;'>" + html_lib.escape(desc) + "</div>" if desc else ""}
                    </div>
                    """, unsafe_allow_html=True)
                    btn_key = f"uni_view_{u['name']}_{start+idx}"
                    if st.button("🤖 AI查看详情", key=btn_key, use_container_width=True):
                        st.session_state["selected_uni"] = u["name"]
                        st.rerun()


# ============================================================
# 专业探索
# ============================================================
def page_major():
    cat_icons = {"工学":"⚙️","理学":"🔬","医学":"🏥","经济学":"📈","管理学":"📊","法学":"⚖️","文学":"📝","教育学":"🎓","艺术学":"🎨","农学":"🌾"}

    st.markdown('<div class="panel-white">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📚 专业探索</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-desc">按学科门类浏览专业，点击即可获取AI生成的专业详情</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 门类卡片
    for row_start in range(0, len(MAJOR_CATEGORIES), 4):
        cols = st.columns(4)
        cats = list(MAJOR_CATEGORIES.keys())
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx < len(cats):
                cat = cats[idx]
                icon = cat_icons.get(cat, "📖")
                count = len(MAJOR_CATEGORIES[cat])
                with col:
                    if st.button(f"{icon} {cat} ({count})", key=f"cat_{cat}", use_container_width=True):
                        st.session_state["selected_cat"] = cat
                        # 清除之前的专业选择
                        if "selected_major" in st.session_state:
                            del st.session_state["selected_major"]
                        st.rerun()

    # 显示选中门类的专业列表
    if "selected_cat" in st.session_state:
        cat = st.session_state["selected_cat"]
        st.markdown('<div class="panel-white">', unsafe_allow_html=True)

        bc1, bc2 = st.columns([5, 1])
        with bc1:
            st.markdown(f"### {cat_icons.get(cat,'📖')} {cat}")
        with bc2:
            if st.button("← 返回门类", key="major_back_cat"):
                del st.session_state["selected_cat"]
                if "selected_major" in st.session_state:
                    del st.session_state["selected_major"]
                st.rerun()

        # 专业列表 - 每行3个按钮
        majors = MAJOR_CATEGORIES[cat]
        for row_start in range(0, len(majors), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                midx = row_start + j
                if midx < len(majors):
                    major = majors[midx]
                    with col:
                        if st.button(f"📖 {major}", key=f"major_{cat}_{midx}", use_container_width=True):
                            st.session_state["selected_major"] = major
                            st.session_state["selected_major_cat"] = cat
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # 如果选中了专业，显示AI详情（自动生成，无需再点按钮）
        if "selected_major" in st.session_state and st.session_state.get("selected_major_cat") == cat:
            major = st.session_state["selected_major"]

            st.markdown('<div class="panel-white">', unsafe_allow_html=True)

            # 顶部标题栏
            tc1, tc2 = st.columns([5, 1])
            with tc1:
                st.markdown(f"### {cat_icons.get(cat,'📖')} {major}")
            with tc2:
                if st.button("← 返回专业列表", key="major_back_detail"):
                    del st.session_state["selected_major"]
                    st.rerun()

            # 自动获取或生成AI详情
            cache_key = f"major_ai_{major}"
            if cache_key not in st.session_state:
                with st.spinner(f"AI正在生成「{major}」的专业详情..."):
                    prompt = f"请详细介绍「{major}」专业：\n1）主要学什么课程（列举核心课程）\n2）就业方向有哪些（具体岗位和行业）\n3）适合什么样的学生（性格、能力、兴趣）\n4）推荐院校（3-5所，说明推荐理由）\n5）发展前景和薪资水平"
                    messages = [
                        {"role": "system", "content": "你是一位高校专业咨询专家，回答要具体、实用、有针对性，提供尽可能详细的信息。"},
                        {"role": "user", "content": prompt}
                    ]
                    st.session_state[cache_key] = call_deepseek(messages)

            st.markdown(f'<div class="recommend-result">{st.session_state[cache_key]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# AI咨询
# ============================================================
def page_ai_chat():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.markdown('<div class="panel-white" style="min-height:500px;">', unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown('<div class="panel-title">💬 AI志愿顾问</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-desc">基于 DeepSeek 大模型，为你提供专业的志愿填报建议</div>', unsafe_allow_html=True)
    with c2:
        if st.button("清空对话", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # 快捷问题
    quick_qs = ["计算机专业怎么选学校？", "文科生适合什么专业？", "平行志愿怎么填？", "哪些专业前景好？", "985和211的区别？"]
    quick_cols = st.columns(len(quick_qs))
    for i, q in enumerate(quick_qs):
        with quick_cols[i]:
            if st.button(q, key=f"quick_{i}"):
                st.session_state["pending_q"] = q
                st.rerun()

    st.markdown("---")

    # 显示历史
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="chat-ai">
                你好！我是你的AI志愿顾问。你可以问我关于大学、专业、志愿填报策略等任何问题。我会尽力为你提供专业、详细的解答。<br><br>
                <strong>温馨提示：</strong>我的建议仅供参考，具体填报请结合各省教育考试院发布的官方数据。
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div style="display:flex;justify-content:flex-end;"><div class="chat-user">{html_lib.escape(msg["content"])}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 处理快捷问题
    if "pending_q" in st.session_state:
        question = st.session_state.pop("pending_q")
        st.session_state.chat_history.append({"role": "user", "content": question})
        messages = [
            {"role": "system", "content": "你是一位专业的高考志愿填报顾问，回答要具体、有数据支撑、实用。"},
            *st.session_state.chat_history
        ]
        with st.spinner("AI正在思考..."):
            response = call_deepseek(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # 输入框
    c1, c2 = st.columns([5, 1])
    with c1:
        user_input = st.text_input("输入你的问题", key="chat_input", placeholder="例如：600分在江苏能上什么学校？", label_visibility="collapsed")
    with c2:
        send = st.button("发送", type="primary", use_container_width=True, key="chat_send")

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        messages = [
            {"role": "system", "content": "你是一位专业的高考志愿填报顾问，回答要具体、有数据支撑、实用。"},
            *st.session_state.chat_history
        ]
        with st.spinner("AI正在思考..."):
            response = call_deepseek(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()


# ============================================================
# 主程序 — Tab导航
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["⚡ 智能推荐", "🏫 院校查询", "📚 专业探索", "💬 AI咨询"])

with tab1:
    page_recommend()
with tab2:
    page_university()
with tab3:
    page_major()
with tab4:
    page_ai_chat()

st.markdown(f"""
<div class="app-footer">
    收录 {len(universities)} 所高校 · AI驱动 · 数据仅供参考
</div>
""", unsafe_allow_html=True)
