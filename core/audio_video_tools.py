"""
音视频工具模块
提供语音识别、音频录制、视频录制功能
为后续测谎模型和大五人格识别模型预留接口
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import threading
import queue
from loguru import logger

# 音频处理
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("⚠️ SpeechRecognition未安装，语音识别功能不可用")

# 视频处理
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("⚠️ OpenCV未安装，视频录制功能不可用")


class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, language: str = "zh-CN"):
        """
        初始化语音识别器
        
        Args:
            language: 识别语言，默认中文
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("需要安装 SpeechRecognition 库")
        
        self.recognizer = sr.Recognizer()
        self.language = language
        self.microphone = None
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None
        
    def recognize_from_microphone(
        self,
        timeout: int = 10,
        phrase_time_limit: Optional[int] = None
    ) -> Optional[str]:
        """
        从麦克风录音并识别
        
        Args:
            timeout: 超时时间（秒）
            phrase_time_limit: 每次录音时长限制（秒）
            
        Returns:
            识别的文本，失败返回None
        """
        try:
            with sr.Microphone() as source:
                logger.info("🎤 请说话...")
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # 录音
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("🔄 正在识别...")
                
                # 识别（使用Google语音识别API）
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.success(f"✅ 识别结果: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.warning("⚠️ 录音超时")
            return None
        except sr.UnknownValueError:
            logger.warning("⚠️ 无法识别语音")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ 识别服务错误: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 语音识别失败: {e}")
            return None
    
    def recognize_from_audio_file(self, audio_file: str) -> Optional[str]:
        """
        从音频文件识别
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            识别的文本，失败返回None
        """
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.success(f"✅ 识别结果: {text}")
                return text
        except Exception as e:
            logger.error(f"❌ 从文件识别失败: {e}")
            return None
    
    def start_recording(self) -> bool:
        """
        开始手动录音（简化版：仍使用自动停顿检测，但延长时间）
        
        Returns:
            是否成功开始
        """
        if self.is_recording:
            logger.warning("⚠️ 已经在录音中")
            return False
        
        try:
            self.is_recording = True
            self.audio_data = None
            logger.info("🎤 开始录音...")
            
            # 在后台线程中录音
            def record_audio():
                try:
                    with sr.Microphone() as source:
                        # 环境噪音校准
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        logger.info("🎤 请说话...")
                        
                        # 录音 - 使用较长的phrase_time_limit，但仍依赖停顿检测
                        # 这样用户说完后停顿即可，不需要等很久
                        self.audio_data = self.recognizer.listen(
                            source,
                            timeout=None,  # 不超时等待开始
                            phrase_time_limit=None  # 无时长限制，直到用户停顿
                        )
                        logger.info("🔄 录音已捕获（检测到停顿）")
                except Exception as e:
                    logger.error(f"❌ 录音失败: {e}")
                finally:
                    # 录音完成后自动标记为非录音状态
                    # 但不清除is_recording，让用户点击停止按钮来识别
                    pass
            
            self.recording_thread = threading.Thread(target=record_audio, daemon=True)
            self.recording_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 开始录音失败: {e}")
            self.is_recording = False
            return False
    
    def stop_recording_and_recognize(self) -> Optional[str]:
        """
        停止录音并识别
        
        Returns:
            识别的文本，失败返回None
        """
        if not self.is_recording:
            logger.warning("⚠️ 未在录音中")
            return None
        
        try:
            logger.info("⏹️ 准备识别...")
            
            # 等待录音线程结束（最多等待3秒）
            if self.recording_thread and self.recording_thread.is_alive():
                logger.info("⏳ 等待录音完成...")
                self.recording_thread.join(timeout=3.0)
            
            # 识别音频
            if self.audio_data:
                logger.info("🔄 正在识别...")
                text = self.recognizer.recognize_google(self.audio_data, language=self.language)
                logger.success(f"✅ 识别结果: {text}")
                self.audio_data = None
                self.is_recording = False
                return text
            else:
                logger.warning("⚠️ 没有捕获到音频数据，可能还在录音中或未检测到语音")
                self.is_recording = False
                return None
                
        except sr.UnknownValueError:
            logger.warning("⚠️ 无法识别语音")
            self.is_recording = False
            return None
        except sr.RequestError as e:
            logger.error(f"❌ 识别服务错误: {e}")
            self.is_recording = False
            return None
        except Exception as e:
            logger.error(f"❌ 识别失败: {e}")
            self.is_recording = False
            return None
        finally:
            self.is_recording = False
            self.audio_data = None


class VideoRecorder:
    """
    视频录制器
    为后续测谎模型、大五人格识别模型预留接口
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        fps: int = 30,
        resolution: tuple = (640, 480)
    ):
        """
        初始化视频录制器
        
        Args:
            output_dir: 输出目录，默认为data/videos
            fps: 帧率
            resolution: 分辨率 (width, height)
        """
        if not CV2_AVAILABLE:
            raise ImportError("需要安装 opencv-python 库")
        
        self.output_dir = Path(output_dir) if output_dir else Path("data/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.fps = fps
        self.resolution = resolution
        
        self.is_recording = False
        self.video_writer = None
        self.capture = None
        self.recording_thread = None
        self.frame_queue = queue.Queue(maxsize=100)
        
        # 预留：测谎模型接口
        self.lie_detection_callback: Optional[Callable] = None
        # 预留：大五人格识别模型接口
        self.personality_detection_callback: Optional[Callable] = None
        
    def start_recording(self, session_id: str) -> bool:
        """
        开始录制
        
        Args:
            session_id: 会话ID，用于生成文件名
            
        Returns:
            是否成功开始
        """
        if self.is_recording:
            logger.warning("⚠️ 已在录制中")
            return False
        
        try:
            # 打开摄像头
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                logger.error("❌ 无法打开摄像头")
                return False
            
            # 设置分辨率
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interview_{session_id}_{timestamp}.avi"
            output_path = self.output_dir / filename
            
            # 初始化视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.fps,
                self.resolution
            )
            
            self.is_recording = True
            
            # 启动录制线程
            self.recording_thread = threading.Thread(
                target=self._recording_loop,
                daemon=True
            )
            self.recording_thread.start()
            
            logger.success(f"✅ 开始录制: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启动录制失败: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> Optional[str]:
        """
        停止录制
        
        Returns:
            录制文件路径，失败返回None
        """
        if not self.is_recording:
            logger.warning("⚠️ 未在录制中")
            return None
        
        self.is_recording = False
        
        # 等待录制线程结束
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        
        # 释放资源
        output_path = None
        if self.video_writer:
            output_path = self.video_writer
            self.video_writer.release()
            self.video_writer = None
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        logger.success(f"✅ 录制已停止")
        return output_path
    
    def _recording_loop(self):
        """录制循环（在独立线程中运行）"""
        frame_count = 0
        
        while self.is_recording:
            ret, frame = self.capture.read()
            if not ret:
                logger.error("❌ 读取帧失败")
                break
            
            # 写入视频文件
            if self.video_writer:
                self.video_writer.write(frame)
            
            frame_count += 1
            
            # 预留：调用测谎模型分析帧
            if self.lie_detection_callback and frame_count % 30 == 0:  # 每秒分析一次
                try:
                    self.lie_detection_callback(frame)
                except Exception as e:
                    logger.warning(f"⚠️ 测谎模型回调失败: {e}")
            
            # 预留：调用人格识别模型分析帧
            if self.personality_detection_callback and frame_count % 90 == 0:  # 每3秒分析一次
                try:
                    self.personality_detection_callback(frame)
                except Exception as e:
                    logger.warning(f"⚠️ 人格识别模型回调失败: {e}")
        
        logger.info(f"📹 录制循环结束，共录制 {frame_count} 帧")
    
    def get_current_frame(self) -> Optional[Any]:
        """
        获取当前帧（用于实时预览）
        
        Returns:
            当前帧，失败返回None
        """
        if not self.is_recording or not self.capture:
            return None
        
        ret, frame = self.capture.read()
        if ret:
            return frame
        return None
    
    def register_lie_detection_model(self, callback: Callable):
        """
        注册测谎模型回调函数
        
        Args:
            callback: 回调函数，接收frame参数，返回分析结果
        """
        self.lie_detection_callback = callback
        logger.info("🔗 测谎模型已注册")
    
    def register_personality_detection_model(self, callback: Callable):
        """
        注册大五人格识别模型回调函数
        
        Args:
            callback: 回调函数，接收frame参数，返回分析结果
        """
        self.personality_detection_callback = callback
        logger.info("🔗 人格识别模型已注册")


class AudioRecorder:
    """
    音频录制器（辅助功能）
    用于保存面试音频记录
    """
    
    def __init__(self, output_dir: Optional[str] = None, sample_rate: int = 44100):
        """
        初始化音频录制器
        
        Args:
            output_dir: 输出目录
            sample_rate: 采样率
        """
        self.output_dir = Path(output_dir) if output_dir else Path("data/audios")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = sample_rate
        
    def save_audio_from_microphone(
        self,
        session_id: str,
        duration: int = 60
    ) -> Optional[str]:
        """
        从麦克风录制音频并保存
        
        Args:
            session_id: 会话ID
            duration: 录制时长（秒）
            
        Returns:
            保存的文件路径，失败返回None
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.error("❌ SpeechRecognition未安装")
            return None
        
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                logger.info(f"🎤 开始录音 {duration} 秒...")
                audio = recognizer.listen(source, timeout=duration)
                
                # 生成文件路径
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{session_id}_{timestamp}.wav"
                output_path = self.output_dir / filename
                
                # 保存音频
                with open(output_path, "wb") as f:
                    f.write(audio.get_wav_data())
                
                logger.success(f"✅ 音频已保存: {output_path}")
                return str(output_path)
                
        except Exception as e:
            logger.error(f"❌ 音频录制失败: {e}")
            return None


# 工具函数
def check_dependencies(check_hardware: bool = False) -> Dict[str, bool]:
    """
    检查依赖是否安装
    
    Args:
        check_hardware: 是否检查硬件设备（麦克风、摄像头），默认False以避免崩溃
    
    Returns:
        依赖状态字典
    """
    status = {
        "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
        "opencv": CV2_AVAILABLE,
        "microphone": False,
        "camera": False
    }
    
    # 只在明确要求时才检查硬件
    if not check_hardware:
        # 仅检查库是否可用，不访问硬件
        # 假设如果库可用，设备也可用（用户可以在实际使用时发现问题）
        status["microphone"] = SPEECH_RECOGNITION_AVAILABLE
        status["camera"] = CV2_AVAILABLE
        return status
    
    # 检查麦克风（仅在需要时）
    if SPEECH_RECOGNITION_AVAILABLE:
        try:
            with sr.Microphone() as source:
                status["microphone"] = True
        except Exception as e:
            logger.debug(f"麦克风检查失败: {e}")
            status["microphone"] = False
    
    # 检查摄像头（仅在需要时）
    if CV2_AVAILABLE:
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                status["camera"] = True
                cap.release()
        except Exception as e:
            logger.debug(f"摄像头检查失败: {e}")
            status["camera"] = False
    
    return status
