# -*- coding: utf-8 -*-
"""高考志愿填报助手 - Streamlit版"""
import streamlit as st
import json
import os

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="高考志愿填报助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
/* 隐藏默认header */
header[data-testid="stHeader"] { display: none; }
div[data-testid="stToolbar"] { display: none; }

/* 主内容区 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.main .block-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1rem;
}

/* 标题 */
h1 { color: #4f46e5; font-weight: 700; }
h2 { color: #374151; font-weight: 600; }

/* 卡片 */
.uni-card {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    background: #fafafa;
    transition: all 0.2s;
}
.uni-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

/* 标签 */
.tag-985 { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
.tag-211 { background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }
.tag-double { background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; }

/* 聊天气泡 */
.chat-user {
    background: #4f46e5;
    color: white;
    padding: 0.8rem 1.2rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.5rem 0;
    max-width: 80%;
    margin-left: auto;
}
.chat-ai {
    background: #f3f4f6;
    color: #1f2937;
    padding: 0.8rem 1.2rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.5rem 0;
    max-width: 80%;
}

/* 输入框 */
.stTextInput input, .stTextArea textarea {
    border-radius: 8px !important;
    border: 1px solid #d1d5db !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1) !important;
}

/* 按钮 */
.stButton button {
    border-radius: 8px;
    font-weight: 500;
}
.stButton button[data-testid="baseButton-primary"] {
    background: #4f46e5;
    color: white;
}

/* 统计卡片 */
.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: 700;
}
.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_universities():
    """加载大学数据"""
    data_path = os.path.join(os.path.dirname(__file__), "universities_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

universities = load_universities()

# 专业分类数据
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

# 省份列表
PROVINCES = sorted(set(u["province"] for u in universities))
TIERS = ["985", "211", "双一流", "公办本科", "民办本科", "公办专科"]

# ============================================================
# DeepSeek API 调用
# ============================================================
def call_deepseek(messages, api_key=None):
    """调用DeepSeek API"""
    import httpx
    
    if api_key is None:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    if not api_key:
        return "请先配置 DeepSeek API Key。在 Streamlit Cloud 中，请在 Secrets 中添加 DEEPSEEK_API_KEY。"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API调用失败: {str(e)}"

# ============================================================
# 页面函数
# ============================================================
def page_recommend():
    """智能推荐页面"""
    st.markdown("## 🎯 智能推荐")
    st.markdown("输入你的成绩信息，AI为你推荐冲、稳、保三档院校")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        score = st.number_input("高考分数", min_value=0, max_value=750, value=600)
    with col2:
        rank = st.number_input("省排名", min_value=1, max_value=1000000, value=10000)
    with col3:
        province = st.selectbox("所在省份", PROVINCES)
    
    preference = st.selectbox("偏好方向", ["无偏好", "理工类", "综合类", "师范类", "财经类", "医药类", "政法类"])
    
    if st.button("获取推荐", type="primary", use_container_width=True):
        with st.spinner("AI正在分析推荐..."):
            prompt = f"""你是一位资深高考志愿填报专家。请根据以下信息，给出冲、稳、保三档院校推荐：

考生信息：
- 高考分数：{score}分
- 省排名：第{rank}名
- 所在省份：{province}
- 偏好方向：{preference}

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
        
        st.markdown("### 推荐结果")
        st.markdown(response)

def page_university():
    """院校查询页面"""
    st.markdown("## 🏫 院校查询")
    
    # 统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(universities)}</div><div class="stat-label">收录院校</div></div>', unsafe_allow_html=True)
    with col2:
        count_985 = sum(1 for u in universities if u["tier"] == "985")
        st.markdown(f'<div class="stat-card"><div class="stat-number">{count_985}</div><div class="stat-label">985高校</div></div>', unsafe_allow_html=True)
    with col3:
        count_211 = sum(1 for u in universities if u["tier"] == "211")
        st.markdown(f'<div class="stat-card"><div class="stat-number">{count_211}</div><div class="stat-label">211高校</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 筛选条件
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("搜索院校", placeholder="输入院校名称、城市或专业关键词...")
    with col2:
        province_filter = st.selectbox("省份", ["全部"] + PROVINCES)
    with col3:
        tier_filter = st.selectbox("层次", ["全部"] + TIERS)
    
    # 筛选
    filtered = universities
    if search:
        search_lower = search.lower()
        filtered = [u for u in filtered if 
                    search_lower in u["name"].lower() or 
                    search_lower in u["city"].lower() or
                    any(search_lower in f for f in u.get("features", []))]
    if province_filter != "全部":
        filtered = [u for u in filtered if u["province"] == province_filter]
    if tier_filter != "全部":
        filtered = [u for u in filtered if u["tier"] == tier_filter]
    
    st.markdown(f"**共找到 {len(filtered)} 所院校**")
    
    # 分页显示
    page_size = 20
    total_pages = (len(filtered) + page_size - 1) // page_size
    page = st.number_input("页码", min_value=1, max_value=total_pages, value=1, key="uni_page")
    
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered[start:end]
    
    # 显示院校卡片
    for u in page_data:
        tier_class = "tag-985" if u["tier"] == "985" else "tag-211" if u["tier"] == "211" else "tag-double"
        features = u.get("features", [])
        features_html = " · ".join(features[:3])
        if len(features) > 3:
            features_html += f" +{len(features)-3}"
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{u['name']}** · {u['city']}")
                st.caption(f"{features_html}")
            with col2:
                st.markdown(f'<span class="{tier_class}">{u["tier"]}</span>', unsafe_allow_html=True)

def page_major():
    """专业探索页面"""
    st.markdown("## 📚 专业探索")
    st.markdown("按学科门类浏览专业，了解专业详情和就业方向")
    
    # 学科选择
    selected_cat = st.selectbox("选择学科门类", list(MAJOR_CATEGORIES.keys()))
    
    if selected_cat:
        majors = MAJOR_CATEGORIES[selected_cat]
        cols = st.columns(3)
        for i, major in enumerate(majors):
            with cols[i % 3]:
                st.markdown(f"**{major}**")
                
                # AI解读按钮
                if st.button(f"了解 {major}", key=f"major_{selected_cat}_{i}"):
                    with st.spinner("AI正在解读..."):
                        prompt = f"请详细介绍「{major}」专业：1）主要学什么课程 2）就业方向有哪些 3）适合什么样的学生 4）推荐院校（3-5所）。"
                        messages = [
                            {"role": "system", "content": "你是一位高校专业咨询专家，回答要具体、实用、有针对性。"},
                            {"role": "user", "content": prompt}
                        ]
                        response = call_deepseek(messages)
                    st.markdown(response)

def page_ai_chat():
    """AI咨询页面"""
    st.markdown("## 💬 AI咨询")
    st.markdown("有任何志愿填报问题，都可以问我")
    
    # 初始化聊天记录
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示历史记录
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # 快捷问题
    st.markdown("---")
    st.markdown("**常见问题：**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("计算机专业怎么选学校？"):
            quick_q = "计算机专业怎么选学校？除了清北浙交，还有哪些性价比高的选择？"
            st.session_state.pending_question = quick_q
            st.rerun()
    with col2:
        if st.button("文科生适合什么专业？"):
            quick_q = "文科生适合什么专业？未来就业前景怎么样？"
            st.session_state.pending_question = quick_q
            st.rerun()
    with col3:
        if st.button("平行志愿怎么填？"):
            quick_q = "平行志愿怎么填才能最大化录取概率？有什么技巧？"
            st.session_state.pending_question = quick_q
            st.rerun()
    
    # 处理快捷问题
    if "pending_question" in st.session_state:
        question = st.session_state.pending_question
        del st.session_state.pending_question
        
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        messages = [
            {"role": "system", "content": "你是一位专业的高考志愿填报顾问，回答要具体、有数据支撑、实用。"},
            *st.session_state.chat_history
        ]
        response = call_deepseek(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    # 用户输入
    user_input = st.text_input("输入你的问题", key="chat_input", placeholder="例如：600分在江苏能上什么学校？")
    
    if st.button("发送", type="primary"):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            messages = [
                {"role": "system", "content": "你是一位专业的高考志愿填报顾问，回答要具体、有数据支撑、实用。"},
                *st.session_state.chat_history
            ]
            response = call_deepseek(messages)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

# ============================================================
# 主程序
# ============================================================
# 侧边栏导航
st.sidebar.markdown("## 🎓 高考志愿填报助手")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择功能",
    ["智能推荐", "院校查询", "专业探索", "AI咨询"],
    label_visibility="collapsed"
)

# 页面路由
if page == "智能推荐":
    page_recommend()
elif page == "院校查询":
    page_university()
elif page == "专业探索":
    page_major()
elif page == "AI咨询":
    page_ai_chat()

# 页脚
st.sidebar.markdown("---")
st.sidebar.caption(f"收录 {len(universities)} 所高校 · AI驱动")
