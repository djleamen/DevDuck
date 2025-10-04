"""
DevDuck utilities and configuration management.

Provides configuration management, logging, and utility functions for the project.
"""

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import yaml

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Logging levels for the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class HardwareConfig:
    """Configuration for DevDuck hardware."""
    port: Optional[str] = None
    baudrate: int = 9600
    auto_detect: bool = True
    timeout: float = 5.0
    servo_calibration: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.servo_calibration is None:
            self.servo_calibration = {
                "head_center": 90,
                "head_left": 45,
                "head_right": 135,
            }

@dataclass
class AIConfig:
    """Configuration for AI and VAPI integration."""
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
    """Configuration for code analysis features."""
    supported_languages: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    max_file_size_mb: int = 10
    enable_git_tracking: bool = True
    analysis_timeout: float = 60.0
    complexity_threshold: float = 10.0

    def __post_init__(self):
        """Set default values if not provided."""
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
    """Configuration for the user interface."""
    window_width: int = 400
    window_height: int = 600
    always_on_top: bool = True
    auto_start_listening: bool = False
    theme: str = "dark"
    websocket_port: int = 8765
    enable_tray_icon: bool = True

@dataclass
class DevDuckConfig:
    """Main configuration class for DevDuck."""
    hardware: HardwareConfig
    ai: AIConfig
    analysis: AnalysisConfig
    ui: UIConfig
    log_level: LogLevel = LogLevel.INFO
    config_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the configuration to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevDuckConfig':
        """Deserialize the configuration from a dictionary."""
        return cls(
            hardware=HardwareConfig(**data.get('hardware', {})),
            ai=AIConfig(**data.get('ai', {})),
            analysis=AnalysisConfig(**data.get('analysis', {})),
            ui=UIConfig(**data.get('ui', {})),
            log_level=LogLevel(data.get('log_level', 'INFO'))
        )

class ConfigManager:
    """Manages loading, saving, and validating the DevDuck configuration."""
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the configuration manager."""
        self.config_dir = Path(
            config_dir) if config_dir else self._get_default_config_dir()
        self.config_file = self.config_dir / "config.yaml"
        self.config: Optional[DevDuckConfig] = None

    def _get_default_config_dir(self) -> Path:
        """Detect the default configuration directory based on the platform."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'DevDuck'
        elif os.name == 'posix':  # macOS/Linux
            if sys.platform == 'darwin':  # macOS
                config_dir = Path.home() / 'Library' / 'Application Support' / 'DevDuck'
            else:  # Linux
                config_dir = Path.home() / '.config' / 'devduck'
        else:
            config_dir = Path.cwd() / 'config'

        return config_dir

    async def load_config(self, config_path: Optional[str] = None) -> DevDuckConfig:
        """Load the configuration from a file or create a default configuration."""
        config_file = Path(config_path) if config_path else self.config_file

        try:
            if config_file.exists():
                async with aiofiles.open(config_file, mode='r', encoding='utf-8') as f:
                    if config_file.suffix in ['.yaml', '.yml']:
                        data = yaml.safe_load(await f.read())
                    elif config_file.suffix == '.json':
                        data = json.loads(await f.read())
                    else:
                        raise ValueError(f"Unsupported config file format: {config_file.suffix}")

                self.config = DevDuckConfig.from_dict(data)
                logger.info("Configuration loaded from %s", config_file)
            else:
                logger.info("No configuration file found, using defaults")
                self.config = self._create_default_config()
                await self.save_config()

        except (OSError, yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error("Failed to load configuration: %s", e)
            logger.info("Using default configuration")
            self.config = self._create_default_config()

        return self.config

    async def save_config(self, config: Optional[DevDuckConfig] = None) -> bool:
        """Save the current configuration to a file."""
        if config:
            self.config = config

        if not self.config:
            logger.error("No configuration to save")
            return False

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(self.config_file, mode='w', encoding='utf-8') as f:
                await f.write(yaml.dump(self.config.to_dict(), default_flow_style=False, indent=2))

            logger.info("Configuration saved to %s", self.config_file)
            return True

        except OSError as e:
            logger.error("Failed to save configuration: %s", e)
            return False

    def _create_default_config(self) -> DevDuckConfig:
        """Create a default configuration with sensible values."""
        return DevDuckConfig(
            hardware=HardwareConfig(),
            ai=AIConfig(vapi_api_key="", assistant_id=None, voice_model="vapi-default", language="en-US"),
            analysis=AnalysisConfig(),
            ui=UIConfig(window_width=800, window_height=600, theme="light"),
            log_level=LogLevel.INFO
        )

    def validate_config(self, config: DevDuckConfig) -> List[str]:
        """Validate the configuration and return a list of errors, if any."""
        errors = []

        if not config.ai.vapi_api_key:
            errors.append("VAPI API key is required")

        if config.hardware.baudrate <= 0:
            errors.append("Hardware baudrate must be positive")

        if config.analysis.max_file_size_mb <= 0:
            errors.append("Max file size must be positive")

        if not (1 <= config.ui.websocket_port <= 65535):
            errors.append("WebSocket port must be between 1 and 65535")

        return errors

    def get_config(self) -> Optional[DevDuckConfig]:
        """Get the current configuration."""
        return self.config

    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update the current configuration with new values."""
        if not self.config:
            logger.error("No configuration loaded to update")
            return False

        try:
            config_dict = self.config.to_dict()
            self._deep_update(config_dict, updates)

            updated_config = DevDuckConfig.from_dict(config_dict)
            errors = self.validate_config(updated_config)

            if errors:
                logger.error("Configuration validation failed: %s", errors)
                return False

            self.config = updated_config
            return True

        except Exception as e:
            logger.error("Failed to update configuration: %s", e)
            return False

    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Recursively update a dictionary with another dictionary."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

class Logger:
    """Logger setup and management for the application."""
    @staticmethod
    def setup_logging(log_level: LogLevel = LogLevel.INFO,
                      log_file: Optional[str] = None,
                      enable_console: bool = True) -> None:
        """Set up logging with the specified log level and handlers."""
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
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a named logger."""
        return logging.getLogger(name)


def get_project_root() -> Path:
    """Detect the project root by looking for setup.py or pyproject.toml."""
    current_path = Path(__file__).parent
    while current_path.parent != current_path:
        if (current_path / 'setup.py').exists() or (current_path / 'pyproject.toml').exists():
            return current_path
        current_path = current_path.parent
    return Path.cwd()


def ensure_directory_exists(directory: Path) -> bool:
    """Ensure that a directory exists, creating it if necessary."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error("Failed to create directory %s: %s", directory, e)
        return False


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with file_path.open(mode='r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to load JSON file %s: %s", file_path, e)
        return None


def save_json_file(file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
    """Save a dictionary to a JSON file."""
    try:
        with file_path.open(mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str)
        return True
    except OSError as e:
        logger.error("Failed to save JSON file %s: %s", file_path, e)
        return False


def format_duration(seconds: int) -> str:
    """Format a duration in seconds into a human-readable string."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


# Implemented format_file_size function
def format_file_size(bytes_size: int) -> str:
    """Format a file size in bytes into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size = int(bytes_size / 1024)
    return f"{bytes_size:.2f} PB"

# Global instances
Config = ConfigManager()
