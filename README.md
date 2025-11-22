# 自动面试系统 (Dual-Agent Interview System)

> 🤖 基于LLM的双Agent自动面试模拟系统

## 📌 项目简介

本系统采用**双Agent架构**，面试官和候选人均由AI扮演，实现完全自动化的面试流程。候选人Agent具备可配置的能力画像和性格特质，能够自主生成符合其人设的回答。

### 核心特点
- ✅ **双Agent架构**：面试官Agent + 候选人Agent 完全自动化对话
- ✅ **可配置候选人**：预设技能水平、性格特质、经验背景
- ✅ **随机性格生成**：🆕 每次自动生成不同性格特质，支持多种策略和原型
- ✅ **自主交互**：无需人工干预，自动完成完整面试流程
- ✅ **批量测试**：支持多候选人配置并行测试

### 应用场景
1. **面试系统测试**：验证面试官Agent的提问和评估质量
2. **训练数据生成**：自动生成大量面试对话数据
3. **候选人模型研究**：研究不同特质候选人的表现模式
4. **招聘流程优化**：测试不同面试策略的效果

---

## 🏗️ 项目结构

```
HRM1/
├── agents/                      # Agent模块
│   ├── interviewer_agent.py    # 面试官Agent
│   ├── candidate_agent.py      # 候选人Agent
│   └── prompts/                # Prompt模板
├── config/                      # 配置文件
│   ├── candidate_templates/    # 候选人模板
│   ├── jobs/                   # 职位配置
│   └── companies/              # 公司信息
├── core/                        # 核心引擎
│   ├── interview_engine.py     # 面试引擎
│   ├── evaluation.py           # 评估模块
│   └── batch_runner.py         # 批量执行
├── data/                        # 数据存储
│   ├── interviews/             # 面试记录
│   └── analysis/               # 分析结果
├── database/                    # 数据库文件
├── Docs/                        # 项目文档
├── .env                        # 环境变量配置
├── .gitignore
├── requirements.txt            # Python依赖
└── README.md                   # 本文件
```

---

## 🚀 快速开始

### 1. 环境准备

**系统要求**：
- Python >= 3.10
- pip 或 conda

**安装依赖**：
```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 conda
conda create -n hrm python=3.10
conda activate hrm
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，配置已使用 iflow API：

```bash
# .env 文件配置
QWEN_API_KEY=your_qwen_api_key_here
QWEN_API_URL=https://apis.iflow.cn/v1
QWEN_MODEL=qwen3-max
```

**API说明**：
- 本项目使用 iflow API 访问 qwen3-max 模型
- iflow 提供 OpenAI 兼容的 API 接口
- API Key 已配置，可以直接使用

### 3. 运行Demo

**方式1：命令行运行（推荐）**

```bash
# 运行Demo模式（快速演示，3个问题）
python main.py --mode demo

# 运行完整模式（所有问题）
python main.py --mode full

# 运行随机性格模式（🆕 每次生成不同性格特质）
python main.py --mode random
```

**方式2：Python脚本**

```python
from core.interview_engine import InterviewEngine
from config import load_candidate_template

# 加载候选人模板
candidate_config = load_candidate_template("ideal_candidate")

# 启动面试
engine = InterviewEngine()
result = engine.run_interview(
    job_file="senior_backend",
    company_file="tech_startup",
    candidate_config=candidate_config,
    mode="demo"
)

print(f"面试评分: {result.recommendation_score}/100")
```

**输出示例**：

```
============================================================
🚀 开始面试流程
============================================================

🏛️  创新科技有限公司
💼 高级后端工程师 职位面试
👤 候选人: 李明
============================================================

👔 面试官: 你好，欢迎来到创新科技有限公司面试高级后端工程师职位。请先简单介绍一下你自己。

👤 李明: 您好，我叫李明，有7年软件开发经验...

[面试问答过程...]

============================================================
📊 面试评估报告
============================================================
🎯 推荐度评分: 85/100
📝 招聘建议: 强烈推荐
```

---

## 📚 详细文档

详细的功能说明和开发文档请查看：
- [功能文档](Docs/自动面试系统-功能文档.md)
- [随机性格系统使用指南](Docs/随机性格系统使用指南.md) 🆕

---

## 🛠️ 技术栈

- **后端框架**：Python + FastAPI
- **LLM模型**：qwen3-max (通过 iflow API)
- **API接口**：OpenAI 兼容接口
- **前端界面**：Streamlit
- **数据库**：SQLite
- **数据分析**：Pandas + Plotly

---

## 📈 开发路线图

### ✅ Phase 1 - MVP（已完成）
- [x] 基础候选人配置（JSON格式）
- [x] 简单能力匹配回答生成
- [x] 面试官问题生成（复用原系统）
- [x] 自动对话流程
- [x] 基础评估报告
- [x] LLM客户端封装
- [x] 完整面试引擎
- [x] 面试记录保存

### ✅ Phase 2 - 性格系统（已完成）
- [x] 性格特质参数化
- [x] 随机性格生成器（4种策略 + 6种原型）
- [x] 风格驱动的回答生成
- [x] 候选人模板库（3个固定 + 无限随机）
- [x] 性格配置保存与复用

### Phase 3 - 批量测试（1周）
- [ ] 批量配置与执行
- [ ] 并行面试支持
- [ ] 多候选人对比视图

### Phase 4 - 数据分析（1周）
- [ ] 特质影响分析
- [ ] 可视化报表
- [ ] 导出功能（CSV/JSON）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📮 联系方式

如有问题或建议，请提交 Issue。

---

**创建日期**：2024年11月  
**最后更新**：2024年11月
