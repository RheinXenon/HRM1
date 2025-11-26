"""
简历生成器
基于候选人配置生成带有个人性格特征的简历（可能夸大或过度谦虚）
"""

from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

from agents.prompts.resume_prompts import RESUME_GENERATION_PROMPT
from agents.prompts.candidate_prompts import (
    get_skill_description,
    format_personality_traits
)


class ResumeGenerator:
    """简历生成器类"""
    
    def __init__(self, llm_client):
        """
        初始化简历生成器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client
    
    def generate_resume(
        self,
        candidate_profile,
        save_to_file: bool = True,
        output_dir: str = None
    ) -> Dict[str, Any]:
        """
        为候选人生成简历
        
        Args:
            candidate_profile: 候选人配置（CandidateProfile对象）
            save_to_file: 是否保存到文件
            output_dir: 输出目录路径（默认为data/resumes）
            
        Returns:
            生成的简历字典
        """
        logger.info(f"正在为候选人 {candidate_profile.name} 生成简历...")
        
        # 构建提示词
        system_prompt = self._build_resume_prompt(candidate_profile)
        
        try:
            # 调用LLM生成简历
            resume_json = self.llm_client.chat_with_json_response(
                messages=[
                    {"role": "system", "content": "你是一位求职者，正在准备面试简历。"},
                    {"role": "user", "content": system_prompt}
                ],
                temperature=0.8  # 适度创造性，体现个性差异
            )
            
            # 添加元数据
            resume_json["generated_at"] = datetime.now().isoformat()
            resume_json["candidate_name"] = candidate_profile.name
            
            # 保存到文件
            if save_to_file:
                filepath = self._save_resume(
                    resume_json, 
                    candidate_profile.name,
                    output_dir
                )
                resume_json["file_path"] = str(filepath)
            
            logger.success(f"✅ 简历生成成功")
            return resume_json
            
        except Exception as e:
            logger.error(f"❌ 简历生成失败: {e}")
            # 返回默认简历
            return self._generate_fallback_resume(candidate_profile)
    
    def _build_resume_prompt(self, profile) -> str:
        """
        构建简历生成提示词
        
        Args:
            profile: 候选人配置
            
        Returns:
            完整的提示词
        """
        # 格式化技能描述
        skill_profile = "\n".join([
            get_skill_description(skill, level)
            for skill, level in profile.skills.items()
        ])
        
        # 格式化工作经历
        exp = profile.experience
        work_experience = f"""
工作年限: {exp.get('years', 0)}年
职位级别: {exp.get('level', '未知')}
项目经历: {len(exp.get('projects', []))}个项目
"""
        
        # 如果有详细项目信息
        if 'projects' in exp and isinstance(exp['projects'], list) and len(exp['projects']) > 0:
            if isinstance(exp['projects'][0], dict):
                work_experience += "\n主要项目:\n"
                for i, proj in enumerate(exp['projects'][:3], 1):
                    work_experience += f"{i}. {proj.get('name', '项目')}: {proj.get('role', '开发者')} - {proj.get('achievement', '完成项目开发')}\n"
        
        # 格式化大五人格特质
        personality_traits = format_personality_traits(profile.personality)
        
        # 格式化知识盲区
        knowledge_blind_spots = self._format_knowledge_blind_spots(profile)
        
        # 构建完整提示词
        prompt = RESUME_GENERATION_PROMPT.format(
            candidate_name=profile.name,
            skill_profile=skill_profile,
            work_experience=work_experience,
            personality_traits=personality_traits,
            knowledge_blind_spots=knowledge_blind_spots
        )
        
        return prompt
    
    def _format_knowledge_blind_spots(self, profile) -> str:
        """格式化知识盲区描述"""
        if not profile.knowledge_blind_spots:
            return "无明显知识盲区（简历描述与实际能力一致）"
        
        blind_spots = profile.knowledge_blind_spots
        overconfident = blind_spots.get("overconfident_areas", [])
        underconfident = blind_spots.get("underconfident_areas", [])
        
        result = []
        
        if overconfident:
            result.append("**过度自信领域（简历中会夸大）:**")
            for area in overconfident:
                skill = area.get("skill", "未知")
                actual = area.get("actual_level", 0)
                perceived = area.get("perceived_level", 0)
                desc = area.get("description", "")
                result.append(f"- {skill}: 实际能力{actual}/10，自我感觉{perceived}/10")
                result.append(f"  {desc}")
                result.append(f"  → 简历中应该按照{perceived}/10的水平来描述")
        
        if underconfident:
            result.append("\n**过度谦虚领域（简历中会低调描述）:**")
            for area in underconfident:
                skill = area.get("skill", "未知")
                actual = area.get("actual_level", 0)
                perceived = area.get("perceived_level", 0)
                desc = area.get("description", "")
                result.append(f"- {skill}: 实际能力{actual}/10，自我感觉{perceived}/10")
                result.append(f"  {desc}")
                result.append(f"  → 简历中应该按照{perceived}/10的水平来描述")
        
        if not result:
            return "无明显知识盲区（简历描述与实际能力一致）"
        
        return "\n".join(result)
    
    def _save_resume(
        self,
        resume_data: Dict,
        candidate_name: str,
        output_dir: str = None
    ) -> Path:
        """
        保存简历到文件
        
        Args:
            resume_data: 简历数据
            candidate_name: 候选人姓名
            output_dir: 输出目录路径
            
        Returns:
            保存的文件路径
        """
        # 确定输出目录
        if output_dir is None:
            output_dir = Path("data/resumes")
        else:
            output_dir = Path(output_dir)
        
        # 创建目录（如果不存在）
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理候选人姓名中的特殊字符
        safe_name = "".join(c for c in candidate_name if c.isalnum() or c in ['_', '-'])
        filename = f"resume_{safe_name}_{timestamp}.json"
        filepath = output_dir / filename
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, ensure_ascii=False, indent=2)
        
        logger.success(f"💾 简历已保存: {filepath}")
        return filepath
    
    def _generate_fallback_resume(self, profile) -> Dict[str, Any]:
        """
        生成备用简历（当LLM失败时使用）
        
        Args:
            profile: 候选人配置
            
        Returns:
            基本简历字典
        """
        logger.warning("⚠️  使用备用简历生成器")
        
        # 基于技能等级决定描述词
        def get_skill_term(level):
            if level >= 8:
                return "精通"
            elif level >= 6:
                return "熟练掌握"
            elif level >= 4:
                return "熟悉"
            else:
                return "了解"
        
        skills_desc = {}
        for skill, level in profile.skills.items():
            skills_desc[skill] = get_skill_term(level)
        
        exp = profile.experience
        projects = exp.get('projects', [])
        
        work_exp = []
        for proj in projects[:3]:  # 最多3个项目
            if isinstance(proj, dict):
                work_exp.append({
                    "project_name": proj.get('name', '项目'),
                    "role": proj.get('role', '开发者'),
                    "duration": proj.get('duration', '未知'),
                    "description": f"{proj.get('name', '项目')}的开发工作",
                    "tech_stack": proj.get('tech_stack', []),
                    "achievements": proj.get('achievement', '完成项目开发')
                })
        
        return {
            "basic_info": {
                "name": profile.name,
                "years_of_experience": f"{exp.get('years', 0)}年",
                "current_level": exp.get('level', '未知')
            },
            "summary": f"{exp.get('years', 0)}年工作经验，熟悉多项技术",
            "skills": skills_desc,
            "work_experience": work_exp,
            "meta": {
                "exaggerated_areas": [],
                "underestimated_areas": [],
                "credibility_score": 80,
                "is_fallback": True
            },
            "generated_at": datetime.now().isoformat(),
            "candidate_name": profile.name
        }
    
    @staticmethod
    def format_resume_for_display(resume_data: Dict) -> str:
        """
        格式化简历为可读文本
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            格式化的简历文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📄 候选人简历")
        lines.append("=" * 60)
        
        # 基本信息
        basic = resume_data.get("basic_info", {})
        lines.append(f"\n姓名: {basic.get('name', '未知')}")
        lines.append(f"工作年限: {basic.get('years_of_experience', '未知')}")
        lines.append(f"职位级别: {basic.get('current_level', '未知')}")
        
        # 个人简介
        summary = resume_data.get("summary", "")
        if summary:
            lines.append(f"\n个人简介:\n{summary}")
        
        # 技能
        skills = resume_data.get("skills", {})
        if skills:
            lines.append("\n专业技能:")
            for skill, level in skills.items():
                lines.append(f"  • {skill}: {level}")
        
        # 工作经历
        work_exp = resume_data.get("work_experience", [])
        if work_exp:
            lines.append("\n项目经历:")
            for i, proj in enumerate(work_exp, 1):
                lines.append(f"\n  {i}. {proj.get('project_name', '项目')}")
                lines.append(f"     角色: {proj.get('role', '未知')}")
                lines.append(f"     时长: {proj.get('duration', '未知')}")
                lines.append(f"     描述: {proj.get('description', '')}")
                tech_stack = proj.get('tech_stack', [])
                if tech_stack:
                    lines.append(f"     技术栈: {', '.join(tech_stack)}")
                lines.append(f"     成就: {proj.get('achievements', '')}")
        
        # 元数据（仅供系统参考）
        meta = resume_data.get("meta", {})
        if meta:
            lines.append("\n[系统备注]")
            lines.append(f"  可信度: {meta.get('credibility_score', 'N/A')}/100")
            exaggerated = meta.get('exaggerated_areas', [])
            if exaggerated:
                lines.append(f"  可能夸大的领域: {', '.join(exaggerated)}")
            underestimated = meta.get('underestimated_areas', [])
            if underestimated:
                lines.append(f"  可能低估的领域: {', '.join(underestimated)}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
