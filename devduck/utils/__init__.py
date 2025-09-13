"""
DevDuck utilities and configuration management.

Provides configuration management, logging, and utility functions for the project.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class HardwareConfig:
    port: Optional[str] = None
    baudrate: int = 9600
    auto_detect: bool = True
    timeout: float = 5.0
    servo_calibration: Dict[str, int] = None

    def __post_init__(self):
        if self.servo_calibration is None:
            self.servo_calibration = {
                "head_center": 90,
                "head_left": 45,
                "head_right": 135,
                "wing_left_up": 0,
                "wing_left_down": 180,
                "wing_right_up": 180,
                "wing_right_down": 0
            }


@dataclass
class AIConfig:
    vapi_api_key: str = ""
    assistant_id: Optional[str] = None
    voice_model: str = "vapi-default"
    language: str = "en-US"
    max_conversation_history: int = 100
    response_timeout: float = 30.0
    enable_sentiment_analysis: bool = True
    sentiment_threshold: float = 0.7


@dataclass
class AnalysisConfig:
    supported_languages: List[str] = None
    exclude_patterns: List[str] = None
    max_file_size_mb: int = 10
    enable_git_tracking: bool = True
    analysis_timeout: float = 60.0
    complexity_threshold: float = 10.0

    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = [
                "python", "javascript", "typescript", "java", "cpp", "c"]
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "node_modules/**",
                ".git/**",
                "__pycache__/**",
                "*.pyc",
                ".venv/**",
                "venv/**",
                "build/**",
                "dist/**"
            ]


@dataclass
class UIConfig:
    window_width: int = 400
    window_height: int = 600
    always_on_top: bool = True
    auto_start_listening: bool = False
    theme: str = "dark"
    websocket_port: int = 8765
    enable_tray_icon: bool = True


@dataclass
class DevDuckConfig:
    hardware: HardwareConfig
    ai: AIConfig
    analysis: AnalysisConfig
    ui: UIConfig
    log_level: LogLevel = LogLevel.INFO
    config_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        # TODO: Implement configuration serialization
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevDuckConfig':
        # TODO: Implement configuration deserialization
        return cls(
            hardware=HardwareConfig(**data.get('hardware', {})),
            ai=AIConfig(**data.get('ai', {})),
            analysis=AnalysisConfig(**data.get('analysis', {})),
            ui=UIConfig(**data.get('ui', {})),
            log_level=LogLevel(data.get('log_level', 'INFO'))
        )


class ConfigManager:

    def __init__(self, config_dir: Optional[str] = None):

        self.config_dir = Path(
            config_dir) if config_dir else self._get_default_config_dir()
        self.config_file = self.config_dir / "config.yaml"
        self.config: Optional[DevDuckConfig] = None

    def _get_default_config_dir(self) -> Path:
        # TODO: Implement platform-specific config directory detection
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'DevDuck'
        elif os.name == 'posix':  # macOS/Linux
            config_dir = Path.home() / '.config' / 'devduck'
        else:
            config_dir = Path.cwd() / 'config'

        return config_dir

    async def load_config(self, config_path: Optional[str] = None) -> DevDuckConfig:
        # TODO: Implement configuration loading
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.config_file

        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    if config_file.suffix == '.yaml' or config_file.suffix == '.yml':
                        data = yaml.safe_load(f)
                    elif config_file.suffix == '.json':
                        data = json.load(f)
                    else:
                        raise ValueError(
                            f"Unsupported config file format: {config_file.suffix}")

                self.config = DevDuckConfig.from_dict(data)
                logger.info(f"Configuration loaded from {config_file}")
            else:
                logger.info("No configuration file found, using defaults")
                self.config = self._create_default_config()
                await self.save_config()

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            self.config = self._create_default_config()

        return self.config

    async def save_config(self, config: Optional[DevDuckConfig] = None) -> bool:
        # TODO: Implement configuration saving
        if config:
            self.config = config

        if not self.config:
            logger.error("No configuration to save")
            return False

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w') as f:
                yaml.dump(self.config.to_dict(), f,
                          default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def _create_default_config(self) -> DevDuckConfig:
        # TODO: Create sensible default configuration
        return DevDuckConfig(
            hardware=HardwareConfig(),
            ai=AIConfig(),
            analysis=AnalysisConfig(),
            ui=UIConfig()
        )

    def validate_config(self, config: DevDuckConfig) -> List[str]:
        # TODO: Implement configuration validation
        errors = []

        if not config.ai.vapi_api_key:
            errors.append("VAPI API key is required")

        if config.hardware.baudrate <= 0:
            errors.append("Hardware baudrate must be positive")

        if config.analysis.max_file_size_mb <= 0:
            errors.append("Max file size must be positive")

        if config.ui.websocket_port <= 0 or config.ui.websocket_port > 65535:
            errors.append("WebSocket port must be between 1 and 65535")

        return errors

    def get_config(self) -> Optional[DevDuckConfig]:
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> bool:
        # TODO: Implement configuration updates
        if not self.config:
            return False

        try:
            config_dict = self.config.to_dict()
            self._deep_update(config_dict, updates)

            updated_config = DevDuckConfig.from_dict(config_dict)
            errors = self.validate_config(updated_config)

            if errors:
                logger.error(f"Configuration validation failed: {errors}")
                return False

            self.config = updated_config
            return True

        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False

    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        # TODO: Implement deep dictionary update
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


class Logger:
    @staticmethod
    def setup_logging(log_level: LogLevel = LogLevel.INFO,
                      log_file: Optional[str] = None,
                      enable_console: bool = True) -> None:
        # TODO: Implement logging setup
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        root_logger.setLevel(getattr(logging, log_level.value))

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)


def get_project_root() -> Path:
    # TODO: Implement project root detection
    current_path = Path(__file__).parent
    while current_path.parent != current_path:
        if (current_path / 'setup.py').exists() or (current_path / 'pyproject.toml').exists():
            return current_path
        current_path = current_path.parent
    return Path.cwd()


def ensure_directory_exists(directory: Path) -> bool:
    # TODO: Implement directory creation
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    # TODO: Implement JSON file loading
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        return None


def save_json_file(file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
    # TODO: Implement JSON file saving
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        return False


def format_duration(seconds: float) -> str:
    # TODO: Implement duration formatting
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_file_size(bytes_size: int) -> str:
    # TODO: Implement file size formatting
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


# Global instances
Config = ConfigManager()
