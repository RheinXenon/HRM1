"""
真人面试页面
真实用户通过语音或文字输入参与面试
面试官Agent通过RAG提升水平，提供专业评估
"""

import streamlit as st
from pathlib import Path
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.llm_client import LLMClient
from agents.interviewer_agent import InterviewerAgent, InterviewQuestion
from core.resume_generator import ResumeGenerator
from core.memory_system import MemorySystem
from core.audio_video_tools import SpeechRecognizer, VideoRecorder, check_dependencies
from config import generate_domain_config
from domains import list_available_domains
from frontend.visualizations import (
    create_score_chart,
    create_dimension_radar_chart,
    create_skills_bar_chart
)
from loguru import logger

# 页面配置
st.set_page_config(
    page_title="真人面试 - HRM1",
    page_icon="🎤",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .message-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .interviewer-msg {
        background: #eff6ff;
        border-left-color: #3b82f6;
    }
    .user-msg {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    .system-msg {
        background: #fef3c7;
        border-left-color: #f59e0b;
    }
    .eval-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-recording {
        background-color: #ef4444;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .resume-editor {
        background: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    .device-status {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    .device-ok {
        background: #d1fae5;
        color: #065f46;
    }
    .device-error {
        background: #fee2e2;
        color: #991b1b;
    }
    .input-button-container {
        display: flex;
        gap: 10px;
        align-items: stretch;
        margin-top: 10px;
    }
    .submit-btn-wrapper {
        flex: 1;
    }
    .mic-btn-wrapper {
        width: 60px;
    }
    /* 提交按钮样式 */
    div[data-testid="column"]:first-child .stButton button {
        height: 50px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
    }
    /* 麦克风按钮样式 */
    div[data-testid="column"]:last-child .stButton button {
        width: 60px !important;
        height: 60px !important;
        min-width: 60px !important;
        border-radius: 50% !important;
        font-size: 28px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ef4444 !important;
        border: none !important;
    }
    div[data-testid="column"]:last-child .stButton button:hover {
        background-color: #dc2626 !important;
    }
    div[data-testid="column"]:last-child .stButton button:disabled {
        background-color: #9ca3af !important;
        cursor: not-allowed !important;
    }
    /* 录音中的按钮样式（闪烁效果） */
    .recording-button {
        animation: pulse-red 1.5s infinite;
    }
    @keyframes pulse-red {
        0%, 100% { background-color: #ef4444 !important; }
        50% { background-color: #dc2626 !important; }
    }
</style>
""", unsafe_allow_html=True)

# 初始化session_state
if 'interview_session_id' not in st.session_state:
    st.session_state.interview_session_id = None
if 'interview_stage' not in st.session_state:
    st.session_state.interview_stage = 'setup'  # setup, interviewing, completed
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'interviewer' not in st.session_state:
    st.session_state.interviewer = None
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'is_in_followup' not in st.session_state:
    st.session_state.is_in_followup = False  # 是否处于追问状态
if 'final_report' not in st.session_state:
    st.session_state.final_report = None
if 'video_recording' not in st.session_state:
    st.session_state.video_recording = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = "候选人"
if 'domain_id' not in st.session_state:
    st.session_state.domain_id = None
if 'job_config' not in st.session_state:
    st.session_state.job_config = None
if 'company_config' not in st.session_state:
    st.session_state.company_config = None
if 'llm_client' not in st.session_state:
    st.session_state.llm_client = None
if 'memory_system' not in st.session_state:
    st.session_state.memory_system = None
if 'video_recorder' not in st.session_state:
    st.session_state.video_recorder = None
if 'all_evaluations' not in st.session_state:
    st.session_state.all_evaluations = []
if 'current_answer_text' not in st.session_state:
    st.session_state.current_answer_text = ""
if 'pending_voice_text' not in st.session_state:
    st.session_state.pending_voice_text = None  # 待追加的语音文本
if 'should_clear_input' not in st.session_state:
    st.session_state.should_clear_input = False  # 是否需要清空输入框
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'recording_thread' not in st.session_state:
    st.session_state.recording_thread = None
if 'speech_recognizer' not in st.session_state:
    st.session_state.speech_recognizer = None


def check_audio_video_status():
    """检查音视频设备状态（仅检查库，不访问硬件以避免崩溃）"""
    # 默认不检查硬件，避免页面加载时访问麦克风/摄像头导致崩溃
    status = check_dependencies(check_hardware=False)
    
    with st.sidebar.expander("🔧 功能状态", expanded=False):
        # 语音识别
        if status['speech_recognition']:
            st.markdown('<div class="device-status device-ok">✅ 语音识别功能可用</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="device-status device-error">❌ 语音识别库未安装</div>', unsafe_allow_html=True)
            st.caption("安装：pip install SpeechRecognition pyaudio")
        
        # 麦克风（基于库可用性推断）
        if status['microphone']:
            st.markdown('<div class="device-status device-ok">✅ 麦克风功能就绪</div>', unsafe_allow_html=True)
            st.caption("首次使用时会请求权限")
        else:
            st.markdown('<div class="device-status device-error">❌ 麦克风功能不可用</div>', unsafe_allow_html=True)
        
        # 摄像头（基于库可用性推断）
        if status['camera']:
            st.markdown('<div class="device-status device-ok">✅ 摄像头功能就绪</div>', unsafe_allow_html=True)
            st.caption("首次使用时会请求权限")
        else:
            st.markdown('<div class="device-status device-error">❌ 视频录制功能不可用</div>', unsafe_allow_html=True)
        
        # OpenCV
        if status['opencv']:
            st.markdown('<div class="device-status device-ok">✅ 视频处理库已安装</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="device-status device-error">❌ 视频处理库未安装</div>', unsafe_allow_html=True)
            st.caption("安装：pip install opencv-python")
        
        st.markdown("---")
        st.caption("💡 实际设备状态将在使用时检测")
    
    return status


def generate_resume_from_description(description: str, domain_id: str) -> Dict:
    """
    根据用户描述生成简历
    
    Args:
        description: 用户描述
        domain_id: 领域ID
        
    Returns:
        生成的简历数据
    """
    try:
        llm_client = st.session_state.llm_client
        
        # 获取领域信息
        company_config, job_config = generate_domain_config(domain_id)
        
        prompt = f"""
你是一位HR助手，需要根据用户的简短描述生成一份正式的简历。

用户描述：
{description}

应聘职位：{job_config.get('title', '')}
职位要求：{json.dumps(job_config.get('requirements', {}), ensure_ascii=False, indent=2)}

请生成一份结构化的简历JSON，包含以下字段：
1. basic_info: 基本信息（name, years_of_experience, current_level, email, phone）
2. summary: 个人简介
3. skills: 专业技能（技能名: 掌握程度，如"精通"、"熟练"等）
4. work_experience: 工作经历列表，每项包含：
   - company: 公司名称
   - position: 职位
   - duration: 时长
   - description: 描述
   - achievements: 成就
5. education: 教育背景（可选）
6. certifications: 证书（可选）

请直接返回JSON格式，不要包含其他文字。
"""
        
        resume_json = llm_client.chat_with_json_response(
            messages=[
                {"role": "system", "content": "你是一位专业的HR助手，擅长根据描述生成结构化简历。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # 添加元数据
        resume_json['generated_at'] = datetime.now().isoformat()
        resume_json['generated_from'] = 'user_description'
        
        logger.success("✅ 简历生成成功")
        return resume_json
        
    except Exception as e:
        logger.error(f"❌ 简历生成失败: {e}")
        st.error(f"简历生成失败: {e}")
        return None


def initialize_interview(domain_id: str, resume_data: Dict, enable_memory: bool = True):
    """
    初始化面试
    
    Args:
        domain_id: 领域ID
        resume_data: 简历数据
        enable_memory: 是否启用记忆系统
    """
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())[:8]
        st.session_state.interview_session_id = session_id
        
        # 创建LLM客户端
        if not st.session_state.llm_client:
            st.session_state.llm_client = LLMClient()
        
        # 加载领域配置
        company_config, job_config = generate_domain_config(domain_id)
        st.session_state.company_config = company_config
        st.session_state.job_config = job_config
        st.session_state.domain_id = domain_id
        
        # 初始化记忆系统
        if enable_memory:
            st.session_state.memory_system = MemorySystem()
            logger.info("💭 记忆系统已启用")
        
        # 创建面试官Agent
        st.session_state.interviewer = InterviewerAgent(
            llm_client=st.session_state.llm_client,
            job_config=job_config,
            company_config=company_config,
            domain_id=domain_id,
            resume_data=resume_data,
            memory_system=st.session_state.memory_system
        )
        
        # 获取用户姓名
        st.session_state.user_name = resume_data.get('basic_info', {}).get('name', '候选人')
        
        # 生成面试问题
        with st.spinner("正在生成面试问题..."):
            # 生成基于简历的问题
            resume_questions = st.session_state.interviewer.generate_resume_based_questions()
            # 生成常规问题
            level = resume_data.get('basic_info', {}).get('current_level', 'mid')
            regular_questions = st.session_state.interviewer.generate_interview_script(level)
            
            # 合并问题
            all_questions = resume_questions + regular_questions
            st.session_state.questions = all_questions[:8]  # 最多8个问题
        
        # 开场白
        greeting = f"你好{st.session_state.user_name}，欢迎来到{company_config.get('name', '')}面试{job_config.get('title', '')}职位。我已经看过你的简历了，我们现在开始吧。"
        
        st.session_state.messages = [
            {"role": "interviewer", "content": greeting}
        ]
        
        st.session_state.interview_stage = 'interviewing'
        st.session_state.current_question_index = 0
        
        logger.success(f"✅ 面试初始化成功，会话ID: {session_id}")
        
    except Exception as e:
        logger.error(f"❌ 面试初始化失败: {e}")
        st.error(f"面试初始化失败: {e}")


def ask_next_question():
    """提出下一个问题"""
    question_index = int(st.session_state.current_question_index)  # 确保是整数
    
    if question_index >= len(st.session_state.questions):
        # 所有问题已完成，生成最终报告
        generate_final_report()
        return
    
    question = st.session_state.questions[question_index]
    question_text = st.session_state.interviewer.ask_question(question)
    
    st.session_state.messages.append({
        "role": "interviewer",
        "content": question_text,
        "metadata": {
            "category": question.category,
            "is_followup": False
        }
    })


def process_user_answer(answer: str):
    """
    处理用户回答
    
    Args:
        answer: 用户回答文本
    """
    if not answer or not answer.strip():
        st.warning("请输入您的回答")
        return
    
    # 添加用户回答到消息列表
    st.session_state.messages.append({
        "role": "user",
        "content": answer
    })
    
    # 获取当前问题
    # 如果是追问状态，索引不变；否则使用当前索引
    question_index = int(st.session_state.current_question_index)  # 确保是整数
    current_question = st.session_state.questions[question_index]
    
    # 评估回答
    with st.spinner("正在评估您的回答..."):
        evaluation = st.session_state.interviewer.evaluate_answer(
            question=current_question.question,
            answer=answer,
            target_skills=current_question.expected_skills
        )
    
    # 保存评估结果
    st.session_state.all_evaluations.append(evaluation)
    
    # 显示评分
    normalized_score = evaluation.get("normalized_score", 50.0)
    score_interpretation = evaluation.get("score_interpretation", {})
    recommendation = score_interpretation.get("recommendation", "观察")
    
    st.session_state.messages.append({
        "role": "system",
        "type": "evaluation",
        "content": {
            "score": normalized_score,
            "recommendation": recommendation,
            "feedback": evaluation.get("feedback", "")
        }
    })
    
    # 检查是否需要追问
    confidence_level = evaluation.get("confidence_level", "genuine")
    need_followup = evaluation.get("need_follow_up", "no").lower() == "yes"
    
    # 简化追问逻辑：只有在明确需要且不在追问状态时才追问
    if need_followup and confidence_level == "overconfident" and not st.session_state.is_in_followup:
        # 生成追问
        followup_skill = current_question.expected_skills[0] if current_question.expected_skills else "细节"
        followup_question = st.session_state.interviewer.generate_followup_question(
            skill=followup_skill,
            original_question=current_question.question,
            original_answer=answer,
            evaluation=evaluation
        )
        
        st.session_state.messages.append({
            "role": "interviewer",
            "content": followup_question,
            "metadata": {
                "is_followup": True
            }
        })
        
        # 标记为追问状态，但索引不变
        st.session_state.is_in_followup = True
    else:
        # 如果是追问后的回答，或者不需要追问，进入下一个问题
        st.session_state.is_in_followup = False
        st.session_state.current_question_index += 1
        
        # 如果还有问题，继续提问
        if st.session_state.current_question_index < len(st.session_state.questions):
            time.sleep(0.5)  # 短暂延迟
            ask_next_question()
        else:
            # 所有问题完成
            generate_final_report()


def generate_final_report():
    """生成最终评估报告"""
    st.session_state.interview_stage = 'completed'
    
    with st.spinner("正在生成最终评估报告..."):
        final_report = st.session_state.interviewer.generate_final_report(
            st.session_state.user_name
        )
        st.session_state.final_report = final_report
        
        # 保存面试记录
        save_interview_record(final_report)
    
    st.session_state.messages.append({
        "role": "system",
        "type": "completion",
        "content": "面试已完成，正在生成评估报告..."
    })
    
    # 停止视频录制
    if st.session_state.video_recording and st.session_state.video_recorder:
        st.session_state.video_recorder.stop_recording()
        st.session_state.video_recording = False


def save_interview_record(final_report: Dict):
    """
    保存面试记录
    
    Args:
        final_report: 最终评估报告
    """
    try:
        data_dir = Path("data/interviews")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{st.session_state.interview_session_id}_real.json"
        filepath = data_dir / filename
        
        record = {
            "interview_id": st.session_state.interview_session_id,
            "interview_type": "real_human",
            "candidate_name": st.session_state.user_name,
            "job_title": st.session_state.job_config.get('title', ''),
            "domain_id": st.session_state.domain_id,
            "start_time": datetime.now().isoformat(),
            "resume": st.session_state.resume_data,
            "conversation_log": st.session_state.messages,
            "evaluation": final_report,
            "recommendation_score": final_report.get("recommendation_score", 0),
            "summary": final_report.get("summary", "")
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        logger.success(f"💾 面试记录已保存: {filepath}")
        
    except Exception as e:
        logger.error(f"❌ 保存面试记录失败: {e}")


def main():
    st.title("🎤 真人面试")
    st.markdown("真实面试体验 | 语音/文字输入 | AI面试官 | 专业评估")
    st.markdown("---")
    
    # 检查设备状态
    device_status = check_audio_video_status()
    
    # ===== 阶段1: 面试设置 =====
    if st.session_state.interview_stage == 'setup':
        st.header("📋 面试准备")
        
        # 侧边栏配置
        with st.sidebar:
            st.header("⚙️ 面试配置")
            
            # 领域选择
            domains = list_available_domains()
            domain_id = st.selectbox(
                "🏢 选择面试领域",
                options=domains,
                format_func=lambda x: {
                    'tech': '💻 技术领域',
                    'marketing': '📢 营销领域',
                    'healthcare': '🏥 医疗领域',
                    'supply_chain_scm_saas': '📦 供应链/SCM/SaaS领域'
                }.get(x, x)
            )
            
            # 显示领域信息
            try:
                from domains import get_domain_info
                domain_info = get_domain_info(domain_id)
                if domain_info:
                    st.info(f"**{domain_info.get('domain_name', domain_id)}**\n\n{domain_info.get('description', '')}")
            except:
                pass
            
            st.markdown("---")
            
            # Agent增强功能
            st.subheader("🧠 Agent增强功能")
            enable_memory = st.checkbox(
                "💭 启用记忆系统",
                value=True,
                help="面试官会利用历史面试经验提供更专业的评估"
            )
            
            st.markdown("---")
            
            # 视频录制选项
            st.subheader("📹 视频录制")
            enable_video = st.checkbox(
                "启用摄像头录制",
                value=False,
                help="录制面试过程，为后续测谎模型和人格识别模型预留接口"
            )
            
            if enable_video and not device_status['camera']:
                st.warning("⚠️ 摄像头不可用，将无法录制")
        
        # 主区域 - 简历输入/生成
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📄 简历准备")
            
            resume_mode = st.radio(
                "选择简历提供方式",
                options=["手动输入JSON", "描述让AI生成"],
                horizontal=True
            )
            
            if resume_mode == "手动输入JSON":
                st.markdown("**请输入您的简历（JSON格式）：**")
                st.caption("提示：可以参考模拟系统中的简历格式")
                
                default_resume = {
                    "basic_info": {
                        "name": "张三",
                        "years_of_experience": "5年",
                        "current_level": "senior",
                        "email": "zhangsan@example.com",
                        "phone": "138****8888"
                    },
                    "summary": "5年工作经验，精通多项技术...",
                    "skills": {
                        "Python": "精通",
                        "Java": "熟练"
                    },
                    "work_experience": [
                        {
                            "company": "XX科技公司",
                            "position": "高级工程师",
                            "duration": "2020-2024",
                            "description": "负责核心系统开发",
                            "achievements": "提升系统性能50%"
                        }
                    ]
                }
                
                resume_text = st.text_area(
                    "简历JSON",
                    value=json.dumps(default_resume, ensure_ascii=False, indent=2),
                    height=400,
                    key="resume_input"
                )
                
                if st.button("✅ 确认简历", type="primary", use_container_width=True):
                    try:
                        resume_data = json.loads(resume_text)
                        st.session_state.resume_data = resume_data
                        
                        # 初始化面试
                        initialize_interview(domain_id, resume_data, enable_memory)
                        
                        # 启动视频录制
                        if enable_video and device_status['camera']:
                            try:
                                from core.audio_video_tools import VideoRecorder
                                st.session_state.video_recorder = VideoRecorder()
                                st.session_state.video_recorder.start_recording(
                                    st.session_state.interview_session_id
                                )
                                st.session_state.video_recording = True
                                logger.info("📹 视频录制已启动")
                            except Exception as e:
                                logger.warning(f"⚠️ 视频录制启动失败: {e}")
                        
                        st.success("✅ 简历已确认，面试即将开始！")
                        time.sleep(1)
                        
                        # 提出第一个问题
                        ask_next_question()
                        
                        st.rerun()
                        
                    except json.JSONDecodeError as e:
                        st.error(f"JSON格式错误: {e}")
                    except Exception as e:
                        st.error(f"初始化失败: {e}")
            
            else:  # AI生成
                st.markdown("**简单描述您的背景，AI将帮您生成简历：**")
                st.caption("例如：我有5年Python开发经验，熟悉Django和Flask，做过电商系统...")
                
                description = st.text_area(
                    "您的背景描述",
                    height=150,
                    placeholder="请输入您的工作经验、技能、项目经历等...",
                    key="resume_desc"
                )
                
                col_gen, col_edit = st.columns(2)
                
                with col_gen:
                    if st.button("🤖 生成简历", type="secondary", use_container_width=True):
                        if description.strip():
                            # 先创建LLM客户端
                            if not st.session_state.llm_client:
                                st.session_state.llm_client = LLMClient()
                            
                            with st.spinner("正在生成简历..."):
                                resume_data = generate_resume_from_description(description, domain_id)
                                if resume_data:
                                    st.session_state.resume_data = resume_data
                                    st.success("✅ 简历生成成功！请在下方查看和编辑")
                                    st.rerun()
                        else:
                            st.warning("请先输入背景描述")
                
                # 显示生成的简历供编辑
                if st.session_state.resume_data:
                    st.markdown("---")
                    st.markdown("**生成的简历（可编辑）：**")
                    
                    resume_text_edit = st.text_area(
                        "编辑简历",
                        value=json.dumps(st.session_state.resume_data, ensure_ascii=False, indent=2),
                        height=400,
                        key="resume_edit"
                    )
                    
                    if st.button("✅ 确认并开始面试", type="primary", use_container_width=True):
                        try:
                            resume_data = json.loads(resume_text_edit)
                            st.session_state.resume_data = resume_data
                            
                            # 初始化面试
                            initialize_interview(domain_id, resume_data, enable_memory)
                            
                            # 启动视频录制
                            if enable_video and device_status['camera']:
                                try:
                                    from core.audio_video_tools import VideoRecorder
                                    st.session_state.video_recorder = VideoRecorder()
                                    st.session_state.video_recorder.start_recording(
                                        st.session_state.interview_session_id
                                    )
                                    st.session_state.video_recording = True
                                    logger.info("📹 视频录制已启动")
                                except Exception as e:
                                    logger.warning(f"⚠️ 视频录制启动失败: {e}")
                            
                            st.success("✅ 面试即将开始！")
                            time.sleep(1)
                            
                            # 提出第一个问题
                            ask_next_question()
                            
                            st.rerun()
                            
                        except json.JSONDecodeError as e:
                            st.error(f"JSON格式错误: {e}")
                        except Exception as e:
                            st.error(f"初始化失败: {e}")
        
        with col2:
            st.subheader("💡 提示")
            st.info("""
**面试流程：**
1. 准备您的简历
2. 开始面试
3. 回答面试官问题
4. 获得专业评估

**输入方式：**
- 📝 文字输入
- 🎤 语音输入
  - 点击🎤开始→说话→停顿→点击⏹️识别
- 混合使用更灵活

**评估标准：**
- 技术深度
- 实践经验
- 回答具体性
- 逻辑清晰度
- 诚实度
- 沟通能力
            """)
    
    # ===== 阶段2: 面试进行中 =====
    elif st.session_state.interview_stage == 'interviewing':
        # 侧边栏 - 面试信息
        with st.sidebar:
            st.header("📊 面试信息")
            
            if st.session_state.company_config and st.session_state.job_config:
                st.markdown(f"**公司：** {st.session_state.company_config.get('name', '')}")
                st.markdown(f"**职位：** {st.session_state.job_config.get('title', '')}")
                st.markdown(f"**候选人：** {st.session_state.user_name}")
            
            st.markdown("---")
            
            # 进度
            total_questions = len(st.session_state.questions)
            current_q = int(st.session_state.current_question_index)
            st.markdown(f"**问题进度：** {current_q}/{total_questions}")
            if total_questions > 0:
                progress = current_q / total_questions
                st.progress(progress)
            
            st.markdown("---")
            
            # 录制状态
            if st.session_state.video_recording:
                st.markdown('<div class="status-indicator status-recording"></div> 正在录制', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 中止按钮
            if st.button("⏹️ 中止面试", type="secondary", use_container_width=True):
                if st.session_state.video_recording and st.session_state.video_recorder:
                    st.session_state.video_recorder.stop_recording()
                st.session_state.interview_stage = 'setup'
                st.session_state.messages = []
                st.session_state.questions = []
                st.session_state.current_question_index = 0
                st.rerun()
        
        # 主区域 - 对话显示
        col_chat, col_input = st.columns([2, 1])
        
        with col_chat:
            st.subheader("💬 面试对话")
            
            # 显示所有消息
            message_container = st.container()
            with message_container:
                for msg in st.session_state.messages:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    msg_type = msg.get('type', '')
                    metadata = msg.get('metadata', {})
                    
                    if role == 'interviewer':
                        icon = "🔍" if metadata.get('is_followup') else "👔"
                        st.markdown(f"""
                        <div class="message-box interviewer-msg">
                            <strong>{icon} 面试官:</strong><br>
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif role == 'user':
                        st.markdown(f"""
                        <div class="message-box user-msg">
                            <strong>👤 您:</strong><br>
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif role == 'system':
                        if msg_type == 'evaluation':
                            eval_data = content
                            score = eval_data.get('score', 0)
                            recommendation = eval_data.get('recommendation', '')
                            
                            if score >= 80:
                                color = "#10b981"
                            elif score >= 60:
                                color = "#f59e0b"
                            else:
                                color = "#ef4444"
                            
                            st.markdown(f"""
                            <div class="eval-box">
                                <strong>📊 评分:</strong> 
                                <span style="color: {color}; font-size: 1.5rem; font-weight: bold;">{score:.1f}/100</span>
                                <span style="color: {color};">({recommendation})</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="message-box system-msg">
                                <strong>📢 系统:</strong> {content}
                            </div>
                            """, unsafe_allow_html=True)
        
        with col_input:
            st.subheader("💬 您的回答")
            
            # 如果需要清空输入框
            if st.session_state.should_clear_input:
                st.session_state.current_answer_text = ""
                st.session_state.should_clear_input = False
            
            # 如果有待追加的语音文本，先追加
            if st.session_state.pending_voice_text:
                if st.session_state.current_answer_text:
                    st.session_state.current_answer_text += " " + st.session_state.pending_voice_text
                else:
                    st.session_state.current_answer_text = st.session_state.pending_voice_text
                st.session_state.pending_voice_text = None  # 清除待追加文本
            
            # 文本输入框 - 直接绑定到session_state
            st.text_area(
                "请输入您的回答",
                height=200,
                placeholder="在此输入您的回答...",
                key="current_answer_text",
                label_visibility="collapsed"
            )
            
            # 按钮容器：提交按钮 + 麦克风按钮
            col_submit, col_mic = st.columns([5, 1])
            
            with col_submit:
                if st.button("📤 提交回答", type="primary", use_container_width=True, key="submit_answer"):
                    if st.session_state.current_answer_text.strip():
                        final_answer = st.session_state.current_answer_text
                        # 设置标志，在下次渲染时清空输入框
                        st.session_state.should_clear_input = True
                        st.session_state.is_recording = False  # 重置录音状态
                        process_user_answer(final_answer)
                        st.rerun()
                    else:
                        st.warning("请输入回答内容")
            
            with col_mic:
                # 检查语音功能是否可用
                mic_disabled = not (device_status.get('speech_recognition', False) and device_status.get('microphone', False))
                
                # 根据录音状态显示不同按钮
                if st.session_state.is_recording:
                    # 录音中 - 显示停止按钮
                    button_icon = "⏹️"
                    button_help = "点击停止录音并识别"
                else:
                    # 未录音 - 显示麦克风按钮
                    button_icon = "🎤"
                    button_help = "点击开始语音输入"
                
                if st.button(button_icon, key="mic_button", disabled=mic_disabled, help=button_help):
                    if not st.session_state.is_recording:
                        # 开始录音
                        try:
                            # 创建或重用语音识别器
                            if st.session_state.speech_recognizer is None:
                                st.session_state.speech_recognizer = SpeechRecognizer(language="zh-CN")
                            
                            success = st.session_state.speech_recognizer.start_recording()
                            if success:
                                st.session_state.is_recording = True
                                st.info("🎤 录音中... 请说话，完成后点击⏹️停止")
                                st.rerun()
                            else:
                                st.error("❌ 无法启动录音")
                        except ImportError:
                            st.error("⚠️ 语音识别库未正确安装，请运行：pip install SpeechRecognition pyaudio")
                        except Exception as e:
                            st.error(f"❌ 启动录音失败：{e}")
                            logger.error(f"启动录音错误: {e}", exc_info=True)
                    else:
                        # 停止录音并识别
                        with st.spinner("🔄 正在识别..."):
                            try:
                                voice_text = st.session_state.speech_recognizer.stop_recording_and_recognize()
                                st.session_state.is_recording = False
                                
                                if voice_text:
                                    # 将识别结果存入pending，在下次渲染时应用
                                    st.session_state.pending_voice_text = voice_text
                                    st.success(f"✅ 识别成功：{voice_text}")
                                    st.rerun()
                                else:
                                    st.warning("未识别到语音，请重试")
                                    st.rerun()
                            except Exception as e:
                                st.session_state.is_recording = False
                                st.error(f"❌ 语音识别失败：{e}")
                                logger.error(f"语音识别错误: {e}", exc_info=True)
                                st.rerun()
            
            # 提示信息
            if mic_disabled:
                st.caption("⚠️ 语音功能不可用，请安装依赖或检查麦克风")
            elif st.session_state.is_recording:
                st.caption("🔴 录音中... 点击⏹️停止并识别")
            else:
                st.caption("💡 提示：点击🎤开始录音，点击⏹️停止")
            
            st.markdown("---")
            st.caption("💡 回答要具体、真实，避免泛泛而谈")
    
    # ===== 阶段3: 面试完成 =====
    elif st.session_state.interview_stage == 'completed':
        st.header("🎉 面试完成")
        
        if st.session_state.final_report:
            report = st.session_state.final_report
            
            st.markdown("---")
            st.subheader("📊 最终评估报告")
            
            # 推荐度评分
            score = report.get('recommendation_score', 0)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # 评分仪表盘
                fig = create_score_chart(score, "综合推荐度")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 维度雷达图
                if 'dimension_scores_summary' in report:
                    fig = create_dimension_radar_chart(report['dimension_scores_summary'])
                    st.plotly_chart(fig, use_container_width=True)
            
            # 技能评分
            if 'skill_scores' in report:
                st.markdown("#### 💪 技能评分")
                fig = create_skills_bar_chart(report['skill_scores'])
                st.plotly_chart(fig, use_container_width=True)
            
            # 文字报告
            col1, col2 = st.columns(2)
            
            with col1:
                if 'strengths' in report:
                    st.markdown("#### ✨ 优势")
                    for strength in report['strengths']:
                        st.success(f"✓ {strength}")
            
            with col2:
                if 'improvements' in report:
                    st.markdown("#### 📈 改进建议")
                    for improvement in report['improvements']:
                        st.warning(f"• {improvement}")
            
            # 总结
            if 'summary' in report:
                st.markdown("#### 📝 总结")
                st.info(report['summary'])
            
            # 招聘建议
            if 'recommendation' in report:
                st.markdown("#### 🎯 招聘建议")
                st.markdown(f"**{report['recommendation']}**")
            
            st.markdown("---")
            
            # 重新开始按钮
            if st.button("🔄 开始新面试", type="primary", use_container_width=True):
                # 清空状态
                st.session_state.interview_stage = 'setup'
                st.session_state.messages = []
                st.session_state.questions = []
                st.session_state.current_question_index = 0
                st.session_state.final_report = None
                st.session_state.resume_data = None
                st.session_state.interviewer = None
                st.session_state.all_evaluations = []
                st.rerun()


if __name__ == "__main__":
    main()
