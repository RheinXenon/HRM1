# 智能面试系统 (Dual-Agent Interview System)

> 🤖 基于LLM的双Agent自动面试模拟系统 | 支持跨行业领域 | 知识盲区检测 | 智能追问机制

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Research-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active-success.svg)](https://github.com)

## 📌 项目简介

本系统采用**双Agent架构**，通过面试官Agent和候选人Agent的智能交互，实现完全自动化的面试流程。系统具备跨行业领域支持、知识盲区检测、智能追问等高级特性，可用于面试系统研究、人才评估模型训练等场景。

### 🎯 核心特点

- ✅ **双Agent架构**：面试官Agent + 候选人Agent 完全自动化对话
- ✅ **跨行业支持** 🆕：内置tech/marketing/healthcare领域，可扩展至任意行业
- ✅ **知识盲区机制**：模拟候选人的知识误判（过度自信/过度谦虚）
- ✅ **智能追问系统**：检测浅层回答，自动深入追问验证真实能力
- ✅ **Few-Shot Negative Examples** 🆕：通过负面示例防止候选人"圆场"
- ✅ **随机性格生成**：支持4种策略（纯随机/原型/混合/极端）+ 6种原型
- ✅ **多维度评分**：0-100标准化评分，支持深度/完整性/准确性等多个维度
- ✅ **可配置性强**：技能水平、性格特质、经验背景均可灵活配置

### 💡 应用场景

| 场景 | 说明 | 价值 |
|------|------|------|
| **面试系统评估** | 测试面试官Agent的提问质量和评估准确性 | 验证面试流程有效性 |
| **训练数据生成** | 自动生成大量高质量面试对话数据 | 用于模型训练和研究 |
| **候选人模拟** | 模拟各类候选人特质（紧张、过度自信等） | 研究不同特质对面试的影响 |
| **招聘流程优化** | 测试不同面试策略的效果 | 优化招聘决策流程 |
| **跨行业研究** | 支持技术、营销、医疗等多个领域 | 领域适应性研究 |

### ⭐ 功能亮点

#### 1. 知识盲区系统
- **过度自信**：actual_level < perceived_level，会"不懂装懂"
- **过度谦虚**：actual_level > perceived_level，明明会却说不确定
- **自知之明**：影响候选人对自身能力的认知准确度

#### 2. 智能追问机制
- 自动检测浮于表面的回答（使用高级术语但缺乏细节）
- 基于领域配置的信号词汇检测（高级术语、模糊词汇、露怯关键词）
- 动态生成深入追问，验证候选人的真实能力水平

#### 3. Few-Shot Negative Examples
- 在追问时注入负面示例，明确展示"错误回答"和"正确回答"
- 防止候选人通过"圆场"掩盖知识不足
- 迫使候选人诚实承认不懂，真实反映能力水平

#### 4. 跨行业领域支持
- **tech**：39个技能，覆盖backend/frontend/database/architecture/devops等
- **marketing**：34个技能，覆盖策略/内容/数字营销/渠道管理等
- **healthcare**：35个技能，覆盖临床/专科/管理/患者照护等
- 支持自定义添加新领域，无需修改代码

---

## 🏗️ 项目结构

```
HRM1/
├── agents/                            # 🤖 Agent模块
│   ├── __init__.py
│   ├── candidate_agent.py             # 候选人Agent（支持知识盲区、性格特质）
│   ├── interviewer_agent.py           # 面试官Agent（多维评分、追问机制）
│   └── prompts/                       # Prompt模板
│       ├── __init__.py
│       ├── candidate_prompts.py       # 候选人系统提示词（含Few-Shot Negative Examples）
│       └── interviewer_prompts.py     # 面试官系统提示词
│
├── config/                            # ⚙️ 配置文件
│   ├── __init__.py                    # 配置加载器
│   ├── candidate_templates/           # 候选人模板库
│   │   ├── ideal_candidate.json       # 理想候选人
│   │   ├── junior_candidate.json      # 初级候选人
│   │   ├── nervous_candidate.json     # 紧张型候选人
│   │   ├── overconfident_candidate.json  # 过度自信候选人
│   │   ├── underconfident_candidate.json # 不自信候选人
│   │   └── test_react_blind_spot.json    # React知识盲区测试模板
│   ├── companies/                     # 公司信息配置
│   │   └── tech_startup.json          # 科技创业公司
│   └── jobs/                          # 职位需求配置
│       └── senior_backend.json        # 高级后端工程师
│
├── core/                              # 🎯 核心引擎
│   ├── __init__.py
│   ├── batch_runner.py                # 批量面试执行器
│   ├── evaluation.py                  # 评估模块（已弃用，由LLM直接评分）
│   ├── interview_engine.py            # 面试引擎（协调Agent交互）
│   ├── llm_client.py                  # LLM客户端（封装API调用）
│   ├── personality_generator.py       # 随机性格生成器（4种策略+6种原型）
│   ├── random_generator.py            # 随机候选人生成器（支持多领域）
│   └── score_normalizer.py            # 评分标准化器（多维度→0-100分）
│
├── domains/                           # 🌍 领域配置（支持跨行业通用化）
│   ├── README.md                      # 领域配置说明
│   ├── __init__.py                    # DomainLoader加载器
│   ├── tech/                          # 技术/互联网领域
│   │   ├── domain_config.json         # 领域元信息
│   │   ├── skills_taxonomy.json       # 技能分类体系（39个技能）
│   │   ├── assessment_signals.json    # 评估信号词汇（22个高级术语）
│   │   └── question_templates.json    # 问题模板
│   ├── marketing/                     # 营销/传媒领域
│   │   ├── domain_config.json
│   │   ├── skills_taxonomy.json       # 技能分类体系（34个技能）
│   │   ├── assessment_signals.json    # 评估信号词汇（18个营销术语）
│   │   └── question_templates.json
│   └── healthcare/                    # 医疗/护理领域
│       ├── domain_config.json
│       ├── skills_taxonomy.json       # 技能分类体系（35个技能）
│       ├── assessment_signals.json    # 评估信号词汇（15个护理术语）
│       └── question_templates.json
│
├── data/                              # 💾 数据存储
│   ├── interviews/                    # 面试记录（JSON格式）
│   └── analysis/                      # 分析结果
│
├── Docs/                              # 📚 项目文档
│   ├── LLM面试官系统学术研究综述_2024-2025.md
│   ├── Phase1_实施完成报告.md
│   ├── Phase1多维度评分优化说明.md
│   ├── 手写记录.md
│   ├── 新评分方案应用总结.md
│   ├── 知识盲区追问防圆场解决方案.md        # Few-Shot Negative Examples方案
│   ├── 知识误判功能说明.md                  # 知识盲区机制文档
│   ├── 第一次随机测试分析报告.md
│   ├── 评分标准化实施方案.md                # 0-100分标准化文档
│   ├── 追问机制说明.md                      # 追问触发逻辑
│   ├── 随机性格系统使用指南.md              # 性格生成系统文档
│   ├── 领域通用化使用指南.md                # 跨行业支持文档
│   └── archive/                             # 历史文档存档
│       ├── 自动面试系统-功能文档.md
│       └── 面试官追问能力改进报告.md
│
├── test/                              # 🧪 测试套件
│   ├── run_all_tests.py               # 测试运行器
│   ├── test_blind_spot_behavior.py    # 知识盲区行为测试
│   ├── test_blind_spot_followup.py    # 知识盲区追问测试
│   ├── test_comprehensive.py          # 综合功能测试
│   ├── test_domain_loader.py          # 领域加载器测试
│   ├── test_followup.py               # 追问机制测试
│   ├── test_iflow_api.py              # iFlow API连接测试
│   ├── test_knowledge_misjudgment.py  # 知识误判测试
│   ├── test_llm_scoring.py            # LLM评分测试
│   ├── test_llm_scoring_quick.py      # 快速评分测试
│   ├── test_overconfident_improved.py # 过度自信候选人测试
│   ├── test_personality_generator.py  # 性格生成器测试
│   ├── test_random_demo_mode.py       # 随机Demo模式测试
│   ├── test_random_full_mode.py       # 随机完整模式测试
│   ├── test_react_followup_manual.py  # React知识盲区手动测试
│   └── test_score_normalization.py    # 评分标准化测试
│
├── frontend（暂时不用）/               # 🎨 前端界面（未启用）
│
├── main_v2.py                         # 🚀 主程序入口（v2.0版本）
├── requirements.txt                   # 📦 Python依赖
├── .env                               # 🔐 环境变量配置
├── .gitignore                         # Git忽略规则
└── README.md                          # 📖 本文件
```

### 📂 核心模块说明

| 模块 | 说明 | 关键功能 |
|------|------|----------|
| **agents/** | Agent实现 | 面试官/候选人双Agent架构，支持知识盲区、追问机制 |
| **config/** | 配置管理 | 候选人模板、公司/职位配置 |
| **core/** | 核心引擎 | 面试流程控制、LLM调用、评分标准化 |
| **domains/** | 领域配置 | 支持tech/marketing/healthcare等跨行业面试 |
| **Docs/** | 项目文档 | 功能说明、实施报告、使用指南 |
| **test/** | 测试套件 | 16个测试文件，覆盖核心功能 |

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

复制 `.env.example` 为 `.env`，然后配置你的 iflow API：

```bash
# .env 文件配置示例
QWEN_API_KEY=your_api_key_here
QWEN_API_URL=https://apis.iflow.cn/v1
QWEN_MODEL=qwen3-max
```

**API说明**：
- 本项目使用 iflow API 访问 qwen3-max 模型
- iflow 提供 OpenAI 兼容的 API 接口
- 请在 [iflow](https://apis.iflow.cn) 注册并获取你的 API Key
- 将 `your_api_key_here` 替换为你的真实 API Key

### 3. 运行主程序

#### 📋 快速参考

| 命令 | 说明 | 执行时间 | 适合场景 |
|------|------|---------|---------|
| `python main_v2.py` | Demo模式（默认） | ~3分钟 | 快速体验 |
| `python main_v2.py --mode full` | 完整面试 | ~5-10分钟 | 深度测试 |
| `python main_v2.py --mode random` | 随机性格 | ~3-5分钟 | 性格研究 |
| `python main_v2.py --mode domain` | 跨领域演示 | ~3-5分钟 | 跨行业展示 |
| `python main_v2.py --help` | 查看帮助 | 即时 | 查看文档 |

#### 📋 命令行使用（推荐）

**查看帮助**：
```bash
python main_v2.py --help
```

**四种运行模式**：

```bash
# 1. Demo模式 - 快速演示（默认）
python main_v2.py --mode demo
# 特点：使用Tech领域，理想候选人，只问3个问题，快速体验系统

# 2. 完整模式 - 支持知识盲区测试
python main_v2.py --mode full
# 特点：可选择6种候选人模板，完整面试流程，详细评估报告

# 3. 随机性格模式 - 性格生成器
python main_v2.py --mode random
# 特点：每次生成不同性格特质，4种策略+6种原型可选

# 4. 跨领域演示 - 领域通用化 🆕
python main_v2.py --mode domain
# 特点：支持Tech/Marketing/Healthcare三大领域选择
```

#### 🎯 各模式详细说明

**模式1: Demo模式**
- 用途：快速体验系统功能
- 配置：Tech领域 + 理想候选人模板
- 问题数：3个
- 执行时间：~3分钟
- 适合场景：首次使用、功能演示

**模式2: 完整模式**
- 用途：完整面试流程，测试知识盲区和追问机制
- 候选人模板：
  - `ideal_candidate` - 理想候选人
  - `junior_candidate` - 初级候选人
  - `nervous_candidate` - 紧张型候选人
  - `overconfident_candidate` - 过度自信（不懂装懂）
  - `underconfident_candidate` - 过度谦虚（低估能力）
  - `test_react_blind_spot` - React知识盲区测试 ⭐推荐
- 问题数：6-10个（含智能追问）
- 执行时间：~5-10分钟
- 适合场景：深度测试、追问机制验证

**模式3: 随机性格模式**
- 用途：生成不同性格特质的候选人
- 策略选择：
  - `normal` - 正态分布（推荐，更真实）
  - `balanced` - 平衡型（中等值）
  - `extreme` - 极端型（有趣的边界情况）
  - `uniform` - 完全随机
- 原型选择：
  - `confident` - 自信型
  - `nervous` - 紧张型
  - `technical` - 技术型
  - `storyteller` - 叙事型
  - `enthusiastic` - 热情型
  - `reserved` - 保守型
- 适合场景：性格研究、多样性测试

**模式4: 跨领域演示** 🆕
- 用途：展示系统跨行业通用化能力
- 领域选择：
  - `tech` - 技术/互联网（39个技能）
  - `marketing` - 营销/传媒（34个技能）
  - `healthcare` - 医疗/护理（35个技能）
- 自动功能：
  - 显示领域信息（名称、描述、适用行业）
  - 为非tech领域自动生成随机候选人
  - 使用领域专属的信号词汇检测
  - 展示领域特定的技能评估
- 适合场景：跨行业应用展示、领域配置验证

#### 💡 使用示例

**示例1: 快速体验**
```bash
# 最简单的使用方式
python main_v2.py
```

**示例2: 测试知识盲区和追问**
```bash
python main_v2.py --mode full
# 在提示时选择: 6 (test_react_blind_spot)
# 系统会检测候选人在React上的"不懂装懂"并智能追问
```

**示例3: 体验营销领域面试**
```bash
python main_v2.py --mode domain
# 在提示时选择: 2 (marketing)
# 系统会生成营销领域候选人并进行营销技能评估
```

**示例4: 生成极端性格候选人**
```bash
python main_v2.py --mode random
# 选择策略: 3 (extreme)
# 生成具有极端性格特质的候选人进行面试
```

#### 方式2：Python脚本

**基础使用（Tech领域）：**

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
    mode="demo",
    domain_id="tech"  # 默认为tech，可选
)

print(f"面试评分: {result.recommendation_score}/100")
```

**跨领域使用（Marketing领域）：**

```python
from core.interview_engine import InterviewEngine
from core.random_generator import RandomCandidateGenerator

# 生成marketing领域候选人
generator = RandomCandidateGenerator(domain_id="marketing")
skills = generator.generate_skills(level="mid")

candidate_config = {
    "profile": {
        "name": "张晓薇",
        "skills": skills,
        "experience": {"years": 5},
        "personality": {"confidence": 70}
    }
}

# 运行marketing领域面试
engine = InterviewEngine()
result = engine.run_interview(
    job_file="marketing_manager",
    company_file="marketing_agency",
    candidate_config=candidate_config,
    domain_id="marketing"  # 使用marketing领域
)
```

**知识盲区测试：**

```python
# 测试React知识盲区（过度自信）
candidate_config = load_candidate_template("test_react_blind_spot")

result = engine.run_interview(
    job_file="senior_backend",
    company_file="tech_startup",
    candidate_config=candidate_config,
    mode="full"
)

# 查看追问效果
for qa in result.conversation_log:
    if "追问" in qa.get("note", ""):
        print(f"追问: {qa['question']}")
        print(f"回答: {qa['answer']}")
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

系统包含完整的功能文档和使用指南：

| 文档 | 说明 | 链接 |
|------|------|------|
| **领域通用化使用指南** | 如何添加新领域、跨行业使用 | [查看](Docs/领域通用化使用指南.md) |
| **知识盲区机制文档** | 知识误判功能说明 | [查看](Docs/知识误判功能说明.md) |
| **知识盲区追问防圆场方案** | Few-Shot Negative Examples实施 | [查看](Docs/知识盲区追问防圆场解决方案.md) |
| **评分标准化方案** | 0-100分多维度评分系统 | [查看](Docs/评分标准化实施方案.md) |
| **追问机制说明** | 智能追问触发逻辑 | [查看](Docs/追问机制说明.md) |
| **随机性格系统指南** | 性格生成器使用方法 | [查看](Docs/随机性格系统使用指南.md) |
| **Phase1实施报告** | 多维度评分优化总结 | [查看](Docs/Phase1_实施完成报告.md) |

---

## 🛠️ 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **编程语言** | Python 3.10+ | 核心开发语言 |
| **LLM模型** | qwen3-max | 通过iflow API访问 |
| **API接口** | OpenAI Compatible | 兼容OpenAI接口格式 |
| **数据存储** | JSON | 面试记录和配置文件 |
| **日志系统** | loguru | 结构化日志输出 |
| **测试框架** | pytest | 16个测试文件 |
| **代码风格** | Python标准 | PEP 8规范 |

---

## 📈 开发路线图

### ✅ Phase 1 - 基础系统（已完成）
- [x] 双Agent架构实现
- [x] LLM客户端封装
- [x] 面试流程引擎
- [x] 配置系统（候选人/公司/职位）
- [x] 面试记录保存

### ✅ Phase 2 - 评分系统（已完成）
- [x] 多维度评分（深度/完整性/准确性/沟通）
- [x] 0-100分标准化映射
- [x] 权重可配置
- [x] LLM驱动评分（替代规则评估）

### ✅ Phase 3 - 知识盲区系统（已完成）
- [x] actual_level vs perceived_level机制
- [x] 自知之明参数
- [x] 过度自信/过度谦虚模拟
- [x] 知识盲区配置（overconfident_areas/underconfident_areas）

### ✅ Phase 4 - 智能追问系统（已完成）
- [x] 浅层回答检测
- [x] 多信号综合判断（术语/模糊词/露怯关键词）
- [x] 动态追问生成
- [x] Few-Shot Negative Examples防圆场

### ✅ Phase 5 - 领域通用化（已完成）
- [x] 领域配置系统（domains/）
- [x] 技能分类体系
- [x] 评估信号词汇
- [x] 问题模板
- [x] 内置3个领域（tech/marketing/healthcare）
- [x] DomainLoader加载器
- [x] 支持自定义扩展

### ✅ Phase 6 - 性格系统（已完成）
- [x] 性格特质参数化（紧张度/自信心/沟通风格/认真程度）
- [x] 随机性格生成器（4种策略 + 6种原型）
- [x] 性格驱动回答生成
- [x] 候选人模板库

### 🔄 Phase 7 - 批量测试（进行中）
- [ ] 批量配置管理
- [ ] 并行面试执行
- [ ] 多候选人对比分析
- [ ] 批量结果导出

### 📋 Phase 8 - 数据分析（计划中）
- [ ] 特质影响分析
- [ ] 可视化报表
- [ ] 统计分析工具
- [ ] 导出功能增强（CSV/Excel/PDF）

---

## � 测试

系统包含完整的测试套件（16个测试文件）：

```bash
# 运行所有测试
python test/run_all_tests.py

# 运行特定测试
python test/test_domain_loader.py          # 领域加载测试
python test/test_blind_spot_followup.py    # 知识盲区追问测试
python test/test_score_normalization.py    # 评分标准化测试
python test/test_personality_generator.py   # 性格生成器测试
```

**测试覆盖**：
- ✅ 领域配置加载
- ✅ 知识盲区行为
- ✅ 追问机制触发
- ✅ Few-Shot Negative Examples效果
- ✅ 评分标准化
- ✅ 性格生成器
- ✅ LLM API连接
- ✅ 综合面试流程

---

## �🤝 贡献指南

欢迎贡献代码和提出建议！

### 如何贡献

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 添加新领域

参考 [领域通用化使用指南](Docs/领域通用化使用指南.md) 添加新的行业领域配置。

---

## 📄 许可证

本项目仅供**学习和研究**使用。

---

## 📮 联系方式

如有问题或建议，请提交 Issue。

---

## 🙏 致谢

- **LLM模型**：qwen3-max (通过iflow API)
- **提示词工程**：参考PromptHub Blog的Few-Shot Negative Examples方案
- **评分系统**：多维度评分参考学术研究和行业实践

---

## 📊 项目统计

- **代码行数**：~8000+ 行Python代码
- **测试文件**：16个测试文件
- **文档数量**：14个Markdown文档
- **支持领域**：3个内置领域（可无限扩展）
- **候选人模板**：6个预设模板
- **技能总数**：108个技能（跨3个领域）

---

**创建日期**：2024年11月  
**最后更新**：2025年11月26日  
**版本**：v2.0 (领域通用化版本)
