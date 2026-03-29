"""
Cross-platform compatibility layer for ContextBridge.

This module provides unified interfaces for platform-specific operations
including file system paths, process management, and system utilities.
"""

import os
import sys
import signal
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Any, Union
from enum import Enum

class Platform(Enum):
    """Supported platforms enumeration."""
    WINDOWS = "win32"
    MACOS = "darwin" 
    LINUX = "linux"
    UNKNOWN = "unknown"

class PlatformCompatibility:
    """Unified cross-platform compatibility layer."""
    
    def __init__(self):
        self.current_platform = self._detect_platform()
        
    def _detect_platform(self) -> Platform:
        """Detect current operating system platform."""
        platform_str = sys.platform.lower()
        if platform_str.startswith('win'):
            return Platform.WINDOWS
        elif platform_str == 'darwin':
            return Platform.MACOS
        elif platform_str.startswith('linux'):
            return Platform.LINUX
        else:
            return Platform.UNKNOWN
    
    # Platform detection helpers
    def is_windows(self) -> bool:
        return self.current_platform == Platform.WINDOWS
    
    def is_macos(self) -> bool:
        return self.current_platform == Platform.MACOS
    
    def is_linux(self) -> bool:
        return self.current_platform == Platform.LINUX
    
    # Log following command
    def get_follow_logs_command(self, log_path: Path, lines: int) -> List[str]:
        """Get platform-specific command for following logs."""
        if self.is_windows():
            return ['powershell', '-Command', f'Get-Content "{log_path}" -Wait -Tail {lines}']
        else:
            return ['tail', '-f', '-n', str(lines), str(log_path)]
    
    # Subprocess flags
    def get_subprocess_flags(self) -> dict:
        """Get platform-specific subprocess creation flags."""
        flags = {}
        if self.is_windows():
            flags.update({
                'creationflags': (
                    subprocess.CREATE_NO_WINDOW |
                    subprocess.DETACHED_PROCESS |
                    subprocess.CREATE_NEW_PROCESS_GROUP
                )
            })
            # Add startupinfo to hide console window
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            flags['startupinfo'] = si
        else:
            flags.update({
                'preexec_fn': lambda: __import__('os').setsid()
            })
        return flags
    
    # Config directory
    def get_config_dir(self) -> Path:
        """Get platform-appropriate config directory."""
        if self.is_windows():
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata) / '.cbridge'
        return Path.home() / '.cbridge'
    
    # Log directory  
    def get_log_dir(self) -> Path:
        """Get platform-appropriate log directory."""
        return self.get_config_dir() / 'logs'

# Global instance for easy access
platform_compat = PlatformCompatibility()