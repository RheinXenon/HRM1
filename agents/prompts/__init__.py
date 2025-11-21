"""
Prompts模块
包含所有Agent的Prompt模板
"""

from agents.prompts.interviewer_prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FOLLOW_UP_PROMPT,
    FINAL_REPORT_PROMPT
)

from agents.prompts.candidate_prompts import (
    CANDIDATE_SYSTEM_PROMPT,
    SELF_INTRODUCTION_PROMPT,
    ANSWER_GENERATION_PROMPT,
    CANDIDATE_QUESTION_PROMPT,
    get_skill_description,
    format_personality_traits
)

__all__ = [
    'INTERVIEWER_SYSTEM_PROMPT',
    'QUESTION_GENERATION_PROMPT',
    'ANSWER_EVALUATION_PROMPT',
    'FOLLOW_UP_PROMPT',
    'FINAL_REPORT_PROMPT',
    'CANDIDATE_SYSTEM_PROMPT',
    'SELF_INTRODUCTION_PROMPT',
    'ANSWER_GENERATION_PROMPT',
    'CANDIDATE_QUESTION_PROMPT',
    'get_skill_description',
    'format_personality_traits'
]
