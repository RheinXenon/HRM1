# main_v2.py 更新说明

## 📋 更新概述

main_v2.py是项目v2.0版本的主程序入口，全面反映项目当前的完整功能和特性。

> **注意**: 原main.py已重命名为main_v2.py

**更新日期**: 2025年11月26日  
**版本**: v2.0 (领域通用化版本)

---

## ✨ 主要更新内容

### 1. 文档和版本信息更新

**之前**:
```python
"""
主入口文件 - 自动面试系统
"""
```

**现在**:
```python
"""
智能面试系统 v2.0 - 主入口文件

特性：
- 双Agent架构（面试官 + 候选人）
- 跨行业领域支持（tech/marketing/healthcare）
- 知识盲区检测（过度自信/过度谦虚）
- 智能追问系统（Few-Shot Negative Examples）
- 多维度评分（0-100标准化）
- 随机性格生成（4种策略 + 6种原型）
"""
```

### 2. 新增跨领域演示模式

新增 `run_cross_domain_demo()` 函数，支持Tech/Marketing/Healthcare三个领域的面试演示：

```python
def run_cross_domain_demo():
    """运行跨领域演示（展示领域通用化能力）"""
    # 选择领域
    # 显示领域信息
    # 生成对应领域候选人
    # 运行面试（使用domain_id参数）
    # 显示领域专属评估
```

**核心特性**:
- 支持3个领域选择：tech/marketing/healthcare
- 自动加载领域配置信息
- 为非tech领域自动生成随机候选人
- 使用领域专属的技能分类和评估标准

### 3. 完善知识盲区测试支持

在完整模式中新增 `test_react_blind_spot` 模板选项：

```python
print("6. test_react_blind_spot - React知识盲区测试（推荐：测试追问机制）")
```

**用途**: 专门测试智能追问系统对"不懂装懂"的检测能力。

### 4. 智能追问统计展示

所有面试模式都新增追问统计显示：

```python
# 显示追问统计
followup_count = sum(1 for qa in result.conversation_log if qa.get('is_followup', False))
if followup_count > 0:
    print(f"\n🔍 智能追问次数: {followup_count}")
    print("   (检测到浅层回答，自动深入追问验证能力)")
```

**显示内容**:
- 追问次数
- 触发原因说明
- 追问示例（最多2个）

### 5. 更新主函数参数说明

**新增模式**: `domain` - 跨领域演示

**完整帮助信息**:
```bash
python main_v2.py --help

智能面试系统 v2.0 - 支持跨行业领域、知识盲区检测、智能追问

示例:
  python main_v2.py --mode demo          # 快速演示（Tech领域）
  python main_v2.py --mode full          # 完整面试（支持知识盲区测试）
  python main_v2.py --mode random        # 随机性格生成
  python main_v2.py --mode domain        # 跨领域演示（Tech/Marketing/Healthcare）

功能特性:
  - 双Agent架构（面试官 + 候选人自动对话）
  - 跨行业支持（tech/marketing/healthcare，可扩展）
  - 知识盲区检测（过度自信/过度谦虚）
  - 智能追问机制（Few-Shot Negative Examples）
  - 多维度评分（0-100标准化）
  - 随机性格生成（4种策略 + 6种原型）
```

### 6. 优化输出显示

- 所有标题栏宽度统一为80字符
- 添加版本信息显示：`版本: v2.0`
- 添加领域信息显示：`领域: Tech`
- 优化emoji使用，更清晰的视觉层次

---

## 🎯 使用方法

### 模式1: Demo模式（默认）
快速演示Tech领域的基础面试流程

```bash
python main_v2.py
# 或
python main_v2.py --mode demo
```

**特点**:
- 使用ideal_candidate模板
- 只问3个问题
- 展示基础评分和追问功能

### 模式2: 完整模式
支持6种候选人模板，测试知识盲区和追问机制

```bash
python main_v2.py --mode full
```

**可选模板**:
1. ideal_candidate - 理想候选人
2. junior_candidate - 初级候选人
3. nervous_candidate - 紧张型候选人
4. overconfident_candidate - 过度自信（不懂装懂）
5. underconfident_candidate - 过度谦虚（低估能力）
6. test_react_blind_spot - React知识盲区测试（**推荐**）

### 模式3: 随机性格模式
每次生成不同性格特质的候选人

```bash
python main_v2.py --mode random
```

**策略选择**:
- normal - 正态分布（推荐）
- balanced - 平衡型
- extreme - 极端型
- uniform - 完全随机

**原型选择**:
- confident - 自信型
- nervous - 紧张型
- technical - 技术型
- storyteller - 叙事型
- enthusiastic - 热情型
- reserved - 保守型

### 模式4: 跨领域演示（🆕）
展示系统的跨行业通用化能力

```bash
python main_v2.py --mode domain
```

**领域选择**:
- tech - 技术/互联网（39个技能）
- marketing - 营销/传媒（34个技能）
- healthcare - 医疗/护理（35个技能）

**自动功能**:
- 显示领域信息（名称、描述、适用行业）
- 为非tech领域自动生成随机候选人
- 使用领域专属的信号词汇检测
- 展示领域特定的技能评估

---

## 🔧 技术改进

### 导入优化
新增领域相关导入：
```python
from domains import list_available_domains, get_domain_info
```

### 代码复用
跨领域模式复用了现有的：
- `RandomCandidateGenerator` - 生成领域特定候选人
- `InterviewEngine` - 面试引擎（支持domain_id参数）
- `DomainLoader` - 领域配置加载器

### 错误处理
所有模式都包含完整的异常处理和traceback输出

---

## 📊 对比总结

| 特性 | v1.0 (Phase 1 MVP) | v2.0 (领域通用化) |
|------|-------------------|------------------|
| 支持领域 | 仅Tech | Tech/Marketing/Healthcare |
| 候选人模板 | 5个 | 6个（新增知识盲区测试） |
| 运行模式 | 3个 | 4个（新增跨领域演示） |
| 追问显示 | ❌ | ✅ 详细统计 |
| 领域信息 | ❌ | ✅ 动态显示 |
| 帮助文档 | 简单 | 详细（含示例和特性说明） |
| 版本标识 | Phase 1 MVP | v2.0 |

---

## 🧪 测试验证

已创建专门的测试文件验证所有新功能：

```bash
python test/test_main_v2.py
```

**测试覆盖**:
- ✅ 领域列表功能
- ✅ 领域信息获取
- ✅ 跨领域候选人生成
- ✅ main_v2.py模式验证

---

## 📝 使用示例

### 示例1: 测试知识盲区和追问
```bash
python main_v2.py --mode full
# 选择: 6 (test_react_blind_spot)
```

**预期效果**:
- 候选人会在React相关问题上"不懂装懂"
- 系统检测到浅层回答，自动追问
- 追问使用Few-Shot Negative Examples防止圆场
- 最终评分会反映真实能力水平

### 示例2: 体验跨领域能力
```bash
python main_v2.py --mode domain
# 选择: 2 (marketing)
```

**预期效果**:
- 显示营销领域信息（品牌、内容、数字营销等）
- 自动生成营销领域候选人（如campaign_planning, SEO等技能）
- 使用营销专属的评估信号词汇
- 面试问题围绕营销技能展开

### 示例3: 快速验证系统功能
```bash
python main_v2.py --mode demo
```

**预期效果**:
- 3个问题快速演示
- 展示基础评分和追问功能
- 适合系统功能验证

---

## 🔮 未来计划

### 待完善功能
1. **领域配置完善**: 为marketing和healthcare创建专门的job和company配置
2. **批量测试**: 支持跨领域批量面试对比
3. **可视化**: 添加不同领域的评估可视化对比
4. **更多领域**: 扩展到教育、销售、金融等领域

### 可能的新模式
- `--mode benchmark`: 批量测试多个领域
- `--mode compare`: 同一候选人跨领域对比
- `--mode analyze`: 深度分析追问效果

---

## 💡 最佳实践

1. **首次使用**: 运行demo模式快速了解系统
2. **测试追问**: 使用full模式 + test_react_blind_spot模板
3. **体验领域**: 使用domain模式体验不同行业
4. **研究性格**: 使用random模式生成多样化候选人
5. **查看帮助**: 运行 `python main_v2.py --help` 获取完整说明

---

**版本**: v2.0  
**更新日期**: 2025年11月26日  
**状态**: ✅ 已测试通过，可正常使用
