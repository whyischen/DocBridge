# 文本分块策略架构

## 概述

ContextBridge 采用策略模式实现灵活的文本分块机制，支持多种分割策略。该架构确保 L0/L1/L2 三层结构的语义一致性。

## 架构层次

```
┌─────────────────────────────────────────────────────────────────┐
│                        架构层次                                   │
└─────────────────────────────────────────────────────────────────┘

业务层 (openviking_manager.py)
    ↓ 调用
工具层 (text_processor.py)
    ↓ 使用
管理层 (chunk_strategy_manager.py)
    ↓ 管理
策略层 (IChunkStrategy 实现)
    ↓ 依赖
提取层 (text_extractor.py)
```

## 核心组件

### 接口层 (`core/interfaces/chunk_strategy_manager.py`)

**IChunkStrategy**: 分块策略接口

```python
class IChunkStrategy(ABC):
    @abstractmethod
    def split(self, text: str, **kwargs) -> List[str]:
        """L2 细粒度分割"""
        pass
    
    def extract_l0_abstract(self, filename: str, content: str) -> str:
        """L0 摘要提取（可选重写，策略感知）"""
        # 默认使用通用启发式提取器
        pass
    
    def extract_l1_outline(self, content: str) -> str:
        """L1 大纲提取（可选重写，策略感知）"""
        # 默认使用通用启发式提取器
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """策略元数据"""
        pass
```

### 管理层 (`core/utils/chunk_strategy_manager.py`)

**ChunkStrategyManager**: 策略管理器（线程安全）

特性：
- ✅ 延迟实例化策略（按需创建）
- ✅ 支持动态参数传递
- ✅ 内置参数验证
- ✅ 双重检查锁定（线程安全）

```python
manager = get_global_strategy_manager()
strategy = manager.get_strategy("paragraph", chunk_size=800, chunk_overlap=150)
```

### 策略实现

#### 1. ParagraphChunkStrategy（默认）
- **分割方式**：按双换行符分割段落
- **适用场景**：通用文档，保持段落完整性
- **L0/L1 提取**：使用默认启发式提取器

#### 2. CharacterChunkStrategy
- **分割方式**：严格按字数分割，尽量在空格处断开
- **适用场景**：需要精确控制 chunk 大小
- **L0 提取**：重写，严格按 200 字符截断
- **L1 提取**：使用默认启发式提取器

#### 3. MarkdownHeaderChunkStrategy
- **分割方式**：按 Markdown 标题级别分割
- **适用场景**：结构化 Markdown 文档
- **L0 提取**：使用默认启发式提取器
- **L1 提取**：重写，只提取到 `max_header_level` 级别

```python
# 示例：只提取 H1-H2 标题
strategy = get_chunk_strategy(
    "markdown_header",
    chunk_size=800,
    max_header_level=2
)
```

#### 4. RegexChunkStrategy
- **分割方式**：按自定义正则表达式分割
- **适用场景**：特殊格式文档
- **L0/L1 提取**：使用默认启发式提取器

#### 5. CustomChunkStrategy
- **分割方式**：自定义函数
- **适用场景**：特殊需求
- **L0/L1 提取**：使用默认启发式提取器

### 工具层 (`core/utils/text_processor.py`)

**统一接口函数**：

```python
# 1. 只分割文本（L2）
chunks = split_text(
    text,
    strategy="paragraph",
    chunk_size=800,
    chunk_overlap=150
)

# 2. 一站式提取和分割（L0 + L1 + L2）
l0_abstract, l1_outline, chunks = extract_with_strategy(
    filename="doc.md",
    content=text,
    strategy="markdown_header",
    chunk_size=800,
    chunk_overlap=150,
    max_header_level=2
)

# 3. 获取策略实例
strategy = get_chunk_strategy("paragraph", chunk_size=800)
```

### 提取层 (`core/utils/text_extractor.py`)

**HeuristicExtractor**: 启发式文本提取器（默认实现）

```python
# L0 摘要：标题 + 首段
abstract = HeuristicExtractor.extract_l0_abstract(filename, content)

# L1 大纲：H1-H3 标题树
outline = HeuristicExtractor.extract_l1_outline(content)
```

## 三层结构说明

```
文档处理流程
    ↓
┌─────────────────────────────────────────┐
│ L0 层：文档摘要（标题 + 首段）            │
│ 生成方式：提取（extract）                │
│ 负责模块：                               │
│   - text_extractor.py (默认实现)        │
│   - 策略可选重写 (如 CharacterStrategy) │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ L1 层：文档大纲（标题树）                │
│ 生成方式：提取（extract）                │
│ 负责模块：                               │
│   - text_extractor.py (默认实现)        │
│   - 策略可选重写 (如 MarkdownStrategy)  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ L2 层：细粒度内容块（chunks）            │
│ 生成方式：分割（split）                  │
│ 负责模块：                               │
│   - chunk_strategy_manager.py (策略)    │
│   - 必须实现 split() 方法               │
└─────────────────────────────────────────┘
```

## 设计优势

- ✅ **语义一致性**：L0/L1/L2 三层结构使用相同的策略逻辑
- ✅ **策略感知**：提取逻辑可以根据分割策略调整
- ✅ **线程安全**：全局管理器使用双重检查锁定
- ✅ **延迟实例化**：按需创建策略实例，节省内存
- ✅ **参数验证**：完整的参数验证，友好的错误消息
- ✅ **易于扩展**：新增策略只需实现 IChunkStrategy 接口

## 使用示例

### 基础用法

```python
from core.utils.text_processor import split_text

# 使用默认策略（paragraph）
chunks = split_text(text, chunk_size=800, chunk_overlap=150)

# 指定策略
chunks = split_text(text, strategy="character", chunk_size=800)
```

### 策略特定提取

```python
from core.utils.text_processor import extract_with_strategy

# Markdown 文档，只提取 H1-H2 标题
l0, l1, chunks = extract_with_strategy(
    filename="doc.md",
    content=text,
    strategy="markdown_header",
    chunk_size=800,
    max_header_level=2
)

print(l1)  # 输出：【文档大纲】(H1-H2): ...
```

### 自定义策略

```python
from core.utils.chunk_strategy_manager import get_global_strategy_manager, CustomChunkStrategy

def my_split_func(text: str) -> List[str]:
    # 自定义分割逻辑
    return text.split('\n---\n')

# 注册自定义策略
manager = get_global_strategy_manager()
custom_strategy = CustomChunkStrategy(
    split_func=my_split_func,
    name="my_custom",
    version="1.0.0"
)
manager.register_strategy("my_custom", custom_strategy)

# 使用自定义策略
chunks = split_text(text, strategy="my_custom")
```

## 配置示例

在 `config.yaml` 中配置分块策略：

```yaml
chunking:
  strategy: markdown_header  # paragraph, character, markdown_header, regex
  chunk_size: 800
  chunk_overlap: 150
  max_header_level: 2  # 仅 markdown_header 策略使用
```

## 扩展新策略

1. 继承 `BaseChunkStrategy`
2. 实现 `split()` 方法
3. 可选重写 `extract_l0_abstract()` 和 `extract_l1_outline()`
4. 注册到管理器

```python
from core.utils.chunk_strategy_manager import BaseChunkStrategy

class MyCustomStrategy(BaseChunkStrategy):
    def __init__(self, chunk_size: int = 800):
        super().__init__("my_custom", "1.0.0")
        self.chunk_size = chunk_size
    
    def split(self, text: str, **kwargs) -> List[str]:
        # 实现分割逻辑
        pass
    
    def extract_l1_outline(self, content: str) -> str:
        # 可选：重写提取逻辑
        pass
```

## 性能考虑

- **延迟实例化**：策略只在首次使用时创建
- **实例缓存**：无参数调用时复用已创建的实例
- **线程安全**：使用锁保护共享状态，但不影响并发读取
- **参数验证**：在构造时和运行时都进行验证，避免后续错误

## 测试

```python
# 测试策略
from core.utils.text_processor import split_text

text = "# Title\n\nContent..."

# 测试不同策略
for strategy in ["paragraph", "character", "markdown_header"]:
    chunks = split_text(text, strategy=strategy, chunk_size=100)
    print(f"{strategy}: {len(chunks)} chunks")

# 测试参数验证
try:
    split_text(text, chunk_size=-1)
except ValueError as e:
    print(f"Validation works: {e}")
```
