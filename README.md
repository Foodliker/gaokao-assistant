# 高考志愿填报助手 - Streamlit Cloud 部署指南

## 快速部署

### 1. 上传到 GitHub

```bash
# 初始化仓库
cd gaokao_streamlit
git init
git add .
git commit -m "高考志愿填报助手 Streamlit应用"

# 在GitHub创建仓库后
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

**注意：** `.streamlit/secrets.toml` 中的 API Key 不要上传！确保 `.gitignore` 包含：
```
.streamlit/secrets.toml
```

### 2. 部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io/
2. 登录 GitHub 账号
3. 点击 "New app"
4. 填写：
   - **Repository**: 你的GitHub仓库地址
   - **Branch**: main
   - **Main file path**: app.py
   - **App URL**: 自定义一个简短的URL

5. 点击 "Advanced settings"，在 **Secrets** 中添加：
   ```toml
   DEEPSEEK_API_KEY = "sk-你的DeepSeek密钥"
   ```

6. 点击 "Deploy" 即可

### 3. 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册/登录
3. 进入 API Keys 页面创建密钥
4. 复制密钥（格式：sk-xxx）

### 4. 本地测试

```bash
cd gaokao_streamlit

# 在 .streamlit/secrets.toml 中填入你的API Key
# DEEPSEEK_API_KEY = "sk-你的密钥"

# 启动
streamlit run app.py
```

## 项目结构

```
gaokao_streamlit/
├── app.py                    # 主程序
├── universities_data.json    # 2836所高校数据
├── requirements.txt          # 依赖
├── .streamlit/
│   └── secrets.toml          # API密钥（本地）
└── README.md                 # 本文件
```

## 功能说明

- **智能推荐**：根据分数/排名/省份推荐冲稳保院校
- **院校查询**：按省份、层次、关键词筛选2836所高校
- **专业探索**：10大学科门类、数十个专业详情
- **AI咨询**：DeepSeek驱动的智能问答

## 费用说明

DeepSeek API 按调用量计费，价格极低（约0.1元/千tokens），日常使用月费约10-50元。
