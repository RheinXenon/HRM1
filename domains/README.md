# 领域配置文件夹

本文件夹用于定义不同行业领域的面试配置，实现系统的领域通用化。

## 文件夹结构

每个领域文件夹包含以下配置文件：

```
领域名称/
├── domain_config.json          # 领域元信息
├── skills_taxonomy.json        # 技能分类体系
├── assessment_signals.json     # 评估信号词汇
└── question_templates.json     # 问题模板
```

## 已有领域

- **tech** - 技术/互联网领域（软件开发、IT、人工智能等）
- **marketing** - 营销/传媒领域（市场营销、品牌传播、内容运营等）
- **healthcare** - 医疗/护理领域（护理、医疗、健康管理等）

## 如何添加新领域

1. 在 `domains/` 下创建新文件夹（如 `education/`）
2. 参考现有领域，创建四个配置文件
3. 在代码中通过 `domain_id` 参数指定使用的领域

## 配置文件说明

### domain_config.json
领域的基本信息，包括领域ID、名称、适用行业、典型岗位等。

### skills_taxonomy.json
定义该领域的技能分类体系，包括硬技能和软技能的分类和定义。

### assessment_signals.json
定义面试官用于评估的信号词汇，包括：
- 高级专业术语（可能不懂装懂的信号）
- 具体指标词汇（有实战经验的信号）
- 具体证据类词汇
- 模糊词汇和露怯指标

### question_templates.json
定义不同难度级别的问题模板，用于生成面试问题。

## 使用方法

```python
from domains import DomainLoader

# 加载领域配置
domain = DomainLoader("marketing")

# 获取技能分类
skills = domain.get_skills_taxonomy()

# 获取评估信号
signals = domain.get_assessment_signals()

# 获取问题模板
templates = domain.get_question_templates()
```
