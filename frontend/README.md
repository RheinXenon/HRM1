# Frontend 前端模块说明

本目录包含HRM1智能面试系统的前端工具模块。

## 📁 文件结构

```
frontend/
├── __init__.py                 # 模块导出
├── interview_controller.py    # 面试流程控制器
├── data_loader.py             # 历史数据加载器
├── visualizations.py          # 可视化图表工具
└── README.md                  # 本文件
```

## 🔧 核心模块

### InterviewController

面试流程控制器，负责：
- 启动、暂停、继续、中止面试
- 多线程异步执行
- 消息队列通信
- 实时状态管理

**使用示例**:
```python
from frontend import InterviewController

controller = InterviewController()
controller.start_interview(
    domain_id="tech",
    candidate_config=candidate_config,
    mode="demo"
)

# 控制面试
controller.pause_interview()
controller.resume_interview()
controller.stop_interview()

# 获取消息
while True:
    msg = controller.get_message()
    if msg is None:
        break
    print(msg)
```

### DataLoader

历史数据加载和处理，提供：
- 面试记录加载
- DataFrame转换
- 统计分析
- 搜索过滤
- 数据导出

**使用示例**:
```python
from frontend import DataLoader

loader = DataLoader()

# 加载所有面试
interviews = loader.load_all_interviews()

# 转换为DataFrame
df = loader.get_interviews_dataframe()

# 获取统计数据
stats = loader.get_statistics()

# 搜索
results = loader.search_interviews(
    candidate_name="张三",
    min_score=60
)

# 导出
loader.export_to_csv("output.csv")
```

### Visualizations

数据可视化工具集，包含：
- 评分仪表盘
- 维度雷达图
- 时间线图表
- 对比柱状图
- 分布饼图
- 技能柱状图

**使用示例**:
```python
from frontend import (
    create_score_chart,
    create_dimension_radar_chart,
    create_timeline_chart
)

# 创建评分仪表盘
fig = create_score_chart(score=75, title="综合评分")

# 创建雷达图
dimension_scores = {
    "technical_depth": 3,
    "practical_experience": 3,
    "answer_specificity": 2,
    "logical_clarity": 3,
    "honesty": 4,
    "communication": 3
}
fig = create_dimension_radar_chart(dimension_scores)

# 在Streamlit中显示
import streamlit as st
st.plotly_chart(fig)
```

## 🎨 设计理念

### 模块化设计
- 每个模块职责单一
- 低耦合高内聚
- 易于测试和维护

### 异步处理
- 面试流程在独立线程运行
- 消息队列实现进程通信
- 避免UI阻塞

### 数据驱动
- 统一的数据加载接口
- 标准化的数据格式
- 灵活的数据转换

### 可视化优先
- 丰富的图表类型
- 统一的配色方案
- 交互式展示

## 🔌 集成方式

### 在Streamlit页面中使用

```python
import streamlit as st
from frontend import InterviewController, DataLoader

# 初始化控制器
if 'controller' not in st.session_state:
    st.session_state.controller = InterviewController()

# 启动面试按钮
if st.button("开始面试"):
    st.session_state.controller.start_interview(...)

# 加载历史数据
loader = DataLoader()
interviews = loader.load_all_interviews()
for interview in interviews:
    st.write(interview)
```

### 在命令行脚本中使用

```python
from frontend import DataLoader

# 分析历史数据
loader = DataLoader()
stats = loader.get_statistics()
print(f"总面试次数: {stats['total_interviews']}")
print(f"平均评分: {stats['avg_score']:.1f}")

# 导出报告
loader.export_to_csv("report.csv")
```

## 📊 数据流

```
用户操作 → Streamlit UI → InterviewController
                              ↓
                         面试线程启动
                              ↓
                         消息队列传递
                              ↓
                    Streamlit Session State
                              ↓
                         UI实时更新
                              ↓
                    数据保存到JSON文件
                              ↓
                       DataLoader加载
                              ↓
                    Visualizations展示
```

## 🧪 测试建议

### 单元测试
```python
def test_data_loader():
    loader = DataLoader()
    interviews = loader.load_all_interviews()
    assert isinstance(interviews, list)

def test_statistics():
    loader = DataLoader()
    stats = loader.get_statistics()
    assert 'total_interviews' in stats
    assert 'avg_score' in stats
```

### 集成测试
```python
def test_interview_flow():
    controller = InterviewController()
    controller.start_interview(...)
    time.sleep(5)
    controller.pause_interview()
    time.sleep(1)
    controller.resume_interview()
    # 验证面试完成
```

## 🐛 常见问题

### Q: 面试控制器线程安全吗？
A: 是的。使用了 `threading.Event` 和 `queue.Queue` 确保线程安全。

### Q: 如何添加新的图表类型？
A: 在 `visualizations.py` 中添加新的函数，返回 `plotly.graph_objects.Figure` 对象。

### Q: DataLoader支持哪些数据格式？
A: 目前支持JSON文件读取和CSV导出。未来可扩展支持Excel、数据库等。

### Q: 如何自定义数据存储路径？
A: 在创建DataLoader时传入 `data_root` 参数：
```python
loader = DataLoader(data_root="custom/path")
```

## 🔄 版本历史

- **v1.0** (2024-11-26): 初始版本
  - 面试控制器
  - 数据加载器
  - 7种可视化图表

## 📝 贡献指南

如需添加新功能：

1. 保持模块独立性
2. 添加完整的docstring
3. 遵循现有代码风格
4. 更新本README

## 📚 相关文档

- [前端页面实现.md](../Docs/前端页面实现.md) - 详细的实现文档
- [前端快速启动指南.md](../前端快速启动指南.md) - 用户使用指南
- [README.md](../README.md) - 项目总体说明

---

**维护者**: HRM1 Team  
**最后更新**: 2024-11-26
