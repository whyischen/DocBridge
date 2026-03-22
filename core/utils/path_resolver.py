"""
Path resolver for search results.

This module provides the PathResolver class that resolves file paths for search results,
returning original paths for text files and converted Markdown paths for binary files.
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PathResolver:
    """Resolves file paths for search results based on file type."""
    
    # Supported file extensions
    TEXT_EXTENSIONS = {'.md', '.txt'}
    BINARY_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.pptx'}
    
    def __init__(self, config: dict):
        """
        Initialize PathResolver with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - watch_dirs: List of watched directories (Path objects)
                - parsed_docs_dir: Path to converted documents directory
        """
        self.watch_dirs = config.get('watch_dirs', [])
        self.parsed_docs_dir = config.get('parsed_docs_dir')
        
        # Ensure parsed_docs_dir is a Path object
        if self.parsed_docs_dir and not isinstance(self.parsed_docs_dir, Path):
            self.parsed_docs_dir = Path(self.parsed_docs_dir)
    
    def resolve_path(self, filename: str, uri: str) -> str:
        """
        Resolve the full file path for a given filename.
        
        Args:
            filename: Name of the file (e.g., "document.pdf")
            uri: Original URI from search result (for logging)
            
        Returns:
            Absolute file path as string, or empty string if not found
        """
        try:
            # Validate filename
            if not filename or not self._is_valid_filename(filename):
                logger.warning(f"Invalid filename: {filename}")
                return ""
            
            # Extract extension
            extension = Path(filename).suffix.lower()
            
            # Determine file type and resolve path
            if extension in self.TEXT_EXTENSIONS:
                path = self._find_in_watch_dirs(filename)
            elif extension in self.BINARY_EXTENSIONS:
                path = self._resolve_binary_file(filename)
            else:
                # Unknown extension, try to find in watch dirs
                logger.debug(f"Unknown extension {extension} for {filename}, searching in watch dirs")
                path = self._find_in_watch_dirs(filename)
            
            # Verify access and return
            if path and self._verify_file_access(path):
                # Expand home directory and return absolute path
                resolved = path.expanduser().resolve()
                return str(resolved)
            else:
                if path:
                    logger.warning(f"File not accessible: {path}")
                else:
                    logger.debug(f"File not found: {filename}")
                return ""
                
        except PermissionError as e:
            logger.warning(f"Permission denied for {filename}: {e}")
            return ""
        except OSError as e:
            logger.error(f"OS error resolving path for {filename}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error resolving path for {filename}: {e}", exc_info=True)
            return ""
    
    def _is_valid_filename(self, filename: str) -> bool:
        """
        Validate filename for security and correctness.
        
        Args:
            filename: Filename to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not filename:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
            return False
        
        # Check for null bytes
        if '\x00' in filename:
            return False
        
        return True
    
    def _find_in_watch_dirs(self, filename: str) -> Optional[Path]:
        """
        Search for file in all watch directories.
        
        Args:
            filename: Name of the file to find
            
        Returns:
            Path object if found, None otherwise
        """
        for watch_dir in self.watch_dirs:
            if not isinstance(watch_dir, Path):
                watch_dir = Path(watch_dir)
            
            candidate = watch_dir / filename
            if candidate.exists() and candidate.is_file():
                return candidate
        
        return None
    
    def _get_converted_path(self, filename: str) -> Optional[Path]:
        """
        Get path to converted Markdown file in parsed_docs.
        
        Args:
            filename: Original filename (e.g., "document.pdf")
            
        Returns:
            Path object if converted file exists, None otherwise
        """
        if not self.parsed_docs_dir:
            return None
        
        # Replace extension with .md
        stem = Path(filename).stem
        converted_filename = f"{stem}.md"
        converted_path = self.parsed_docs_dir / converted_filename
        
        if converted_path.exists() and converted_path.is_file():
            return converted_path
        
        return None
    
    def _resolve_binary_file(self, filename: str) -> Optional[Path]:
        """
        Resolve path for binary files (PDF, Office formats).
        
        Strategy: Try converted Markdown first, fallback to original file.
        
        Args:
            filename: Name of the binary file
            
        Returns:
            Path object if found, None otherwise
        """
        # Try converted Markdown first (better for AI agents)
        converted_path = self._get_converted_path(filename)
        if converted_path:
            return converted_path
        
        # Fallback to original file
        original_path = self._find_in_watch_dirs(filename)
        if original_path:
            return original_path
        
        return None
    
    def _verify_file_access(self, path: Path) -> bool:
        """
        Verify file exists and is readable.
        
        Args:
            path: Path to verify
            
        Returns:
            True if file exists and is accessible, False otherwise
        """
        try:
            if not path.exists():
                return False
            
            if not path.is_file():
                return False
            
            # Try to stat the file to check permissions
            path.stat()
            return True
            
        except PermissionError:
            return False
        except OSError:
            return False
