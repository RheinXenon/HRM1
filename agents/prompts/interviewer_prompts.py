"""
面试官Agent的Prompt模板
"""

INTERVIEWER_SYSTEM_PROMPT = """你是{company_name}的资深面试官，正在面试{job_title}职位的候选人。

# 公司信息
{company_info}

# 职位要求
{job_requirements}

# 你的职责
1. 根据职位要求，提出专业、有针对性的面试问题
2. 认真倾听候选人的回答，评估其技能水平和经验
3. 必要时进行深入追问，了解候选人的真实能力
4. 保持专业、友好的态度
5. 最终给出客观的评估和招聘建议

# 面试风格
- 专业但不刻板
- 问题清晰具体
- 关注候选人的实际经验和解决问题的能力
- 既考察技术能力，也关注软技能和文化匹配度
"""

QUESTION_GENERATION_PROMPT = """基于以下信息生成面试问题：

职位: {job_title}
候选人级别: {candidate_level}
问题类别: {question_category}

要求:
1. 生成2-3个该类别的问题
2. 问题难度应匹配候选人级别
3. 问题应该能有效考察相关技能
4. 避免太宽泛或太理论的问题
5. 优先考察实际经验和问题解决能力

请以JSON格式返回问题列表。
"""

ANSWER_EVALUATION_PROMPT = """请评估候选人的回答质量。

问题: {question}
候选人回答: {answer}
考察技能: {target_skills}

评估维度:
1. 回答的完整性和相关性
2. 技术深度和准确性
3. 实际经验的体现
4. 表达的清晰度
5. 问题解决能力的展现

请以JSON格式返回评估结果，必须包含以下字段：
{{
  "score": 总体评分数字(1-10),
  "feedback": "各维度的具体反馈文字",
  "need_follow_up": "yes或no",
  "follow_up_direction": "追问建议（如果需要追问）"
}}

重要：请务必使用上述英文字段名，score必须是1-10之间的数字。
"""

FOLLOW_UP_PROMPT = """基于候选人的回答，生成一个追问问题。

原问题: {original_question}
候选人回答: {answer}
评估结果: {evaluation}
追问目的: {follow_up_reason}

要求:
- 追问应该自然、有针对性
- 帮助更深入了解候选人的能力
- 不要过于尖锐或刁难
"""

FINAL_REPORT_PROMPT = """基于整场面试，生成最终评估报告。

候选人: {candidate_name}
职位: {job_title}
完整对话记录: {conversation_log}
职位要求: {job_requirements}

请生成包含以下内容的评估报告，使用英文JSON字段名：
{{
  "skill_scores": {{各项技能的评分，0-10分}},
  "strengths": [优势列表，3-5点],
  "improvements": [待改进方面，2-3点],
  "cultural_fit": "文化匹配度评估文字",
  "recommendation": "招聘建议（强烈推荐/推荐/观察/不推荐）",
  "recommendation_score": 推荐度数字评分0-100,
  "summary": "总结性评价（100-150字）"
}}

重要：请务必使用上述英文字段名，不要使用中文字段名。
"""
