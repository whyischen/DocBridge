"""
文本提取器
用于从文档中提取结构化信息（L0摘要、L1大纲等）
"""
import re
from core.i18n import t


class HeuristicExtractor:
    """启发式文本提取器"""
    
    @staticmethod
    def extract_l0_abstract(filename: str, content: str) -> str:
        """
        利用启发式规则提取文档的 L0 结构化摘要
        
        Args:
            filename: 文件名
            content: 文档内容
            
        Returns:
            L0 摘要字符串
        """
        # 提取第一个 H1 或是 H2 作为真实标题
        title_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename
        
        # 提取第一个有效正文段落（过滤掉标题、代码块、列表等格式文字）
        lines = content.split('\n')
        first_p = ""
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if in_code_block or not stripped:
                continue
                
            # 过滤掉标题、列表、引用或图片、链接的格式开头
            if re.match(r'^([#*>+\-]|!\[|\[)', stripped):
                continue
                
            # 找到一个大于 50 个字符的段落（通常才是人话）
            if len(stripped) > 50:
                first_p = stripped
                break
                
        # 兜底：如果没有长段落，就取第一行不是格式的非空文本
        if not first_p:
            for line in lines:
                if line.strip() and not re.match(r'^([#*>+\-```])', line.strip()):
                    first_p = line.strip()
                    break
                    
        # 防止摘要过度冗长
        if len(first_p) > 200:
            first_p = first_p[:197] + "..."
            
        return f"{t('abstract_title')}: {title}\n{t('abstract_summary')}: {first_p}"

    @staticmethod
    def extract_l1_outline(content: str) -> str:
        """
        利用正则提取文档所有大纲标题，生成 L1 总览
        
        Args:
            content: 文档内容
            
        Returns:
            L1 大纲字符串
        """
        # 提取从 H1 到 H3 的标题
        headers = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
        if not headers:
            return "【文档大纲】: 无明确结构"
            
        outline = ["【文档大纲】:"]
        for hashes, text in headers:
            indent = "  " * (len(hashes) - 1)
            outline.append(f"{indent}- {text.strip()}")
            
        full_outline = "\n".join(outline)
        if len(full_outline) > 1000:
            return full_outline[:997] + "..."
        return full_outline


def get_enhanced_extractor():
    """
    获取增强版启发式提取器实例
    为了保持轻量级，默认不导入，只在需要时使用
    """
    from core.utils.hybrid_text_splitter import EnhancedHeuristicExtractor
    return EnhancedHeuristicExtractor
