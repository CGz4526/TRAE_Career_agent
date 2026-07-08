"""应用配置管理"""
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置，从 .env 文件读取"""

    # LLM 配置
    llm_api_key: str = ""
    llm_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    llm_model: str = "doubao-pro-32k"
    llm_vision_model: str = ""  # 视觉模型（用于图片 OCR）

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Java 后端
    java_backend_url: str = "http://localhost:8080"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"  # 允许额外的环境变量


# 全局配置单例
settings = Settings()
