import React from 'react';
import { Database, Terminal, FolderSync, Settings, Shield, Zap, BookOpen, FileText, Cog } from 'lucide-react';

export const APP_CONTENT = {
  en: {
    title: "ContextBridge",
    badgeText: "Open Source · MIT License",
    heroTitle: "Give AI Agents",
    heroHighlight: "",
    heroSuffix: <>Effortless Access<br />to Your Local Documents</>,
    subtitle: "Local knowledge base for OpenClaw, Cursor and AI assistants. Read your documents instantly—Word, Excel, PDF. No uploads. Privacy first.",
    docsSection: "Documentation",
    docCards: [
      {
        icon: BookOpen,
        title: "User Guide",
        desc: "Complete setup and usage instructions for ContextBridge"
      },
      {
        icon: Zap,
        title: "OpenClaw Integration",
        desc: "Install and use ContextBridge as an OpenClaw Skill"
      }
    ],
    openclawCta: {
      badge: "OpenClaw Integration",
      title: "Use with OpenClaw in Seconds",
      desc: "ContextBridge is available as an OpenClaw Skill. Install it once and let your AI agent search your local documents instantly.",
      steps: [
        { label: "Install", cmd: "pip install cbridge-agent" },
        { label: "Init", cmd: "cbridge init && cbridge start" },
      ],
      cta: "View Integration Guide",
    },
    features: [
      {
        icon: Settings,
        title: "Interactive Setup",
        desc: <>Run <code className="text-indigo-300">cbridge init</code> for a guided setup. Choose between embedded mode or connect to external instances instantly.</>
      },
      {
        icon: FolderSync,
        title: "Smart Folder Watcher",
        desc: <>Effortlessly track project directories with <code className="text-indigo-300">cbridge watch</code>. Add or remove context sources instantly without restarts.</>
      },
      {
        icon: Shield,
        title: "100% Local Privacy",
        desc: "All data stays on your machine. No cloud APIs, no uploads, no tracking. Your documents never leave your hard drive—complete data sovereignty."
      },
      {
        icon: Terminal,
        title: "Visual Indexing",
        desc: <>Run <code className="text-indigo-300">cbridge index</code> to batch process your documents with a beautiful, real-time progress bar powered by tqdm.</>
      },
      {
        icon: Database,
        title: "Batteries Included",
        desc: "Comes with an embedded ChromaDB search runtime. No need to manually install external databases or initialize indexes."
      },
      {
        icon: FileText,
        title: "Multi-Format Support",
        desc: "Seamlessly handles Word, Excel, PDF, and Markdown. ContextBridge automatically parses your diverse local documents into high-fidelity context for your agents."
      }
    ],
    quickStart: "Quick Start",
    steps: [
      { comment: "# 1. Install ContextBridge globally", cmd: "pip install cbridge-agent" },
      { comment: "# 2. Interactive Initialization", cmd: "cbridge init" },
      { comment: "# 3. Add folders to monitor", cmd: "cbridge watch add ~/Documents/MyProjects" },
      { comment: "# 4. Build initial index with progress bar", cmd: "cbridge index" },
      { comment: "# 5. Start the real-time watcher & MCP Server", cmd: "cbridge start" },
      { comment: "# 6. Test with the demo document", cmd: 'cbridge search "ContextBridge"' }
    ]
  },
  zh: {
    title: "ContextBridge",
    badgeText: "开源 · MIT 协议",
    heroTitle: "让 AI 智能体",
    heroHighlight: "",
    heroSuffix: <>轻松读懂<br />你的本地文档</>,
    subtitle: "专为 Openclaw、Cursor 等智能体设计的知识库插件。让你的 AI 助手轻松读取、理解本地的 Word、Excel 和 PDF 文件，无需上传，隐私安全。",
    docsSection: "文档中心",
    docCards: [
      {
        icon: BookOpen,
        title: "使用指南",
        desc: "ContextBridge 的完整设置和使用说明"
      },
      {
        icon: Zap,
        title: "OpenClaw 集成",
        desc: "将 ContextBridge 作为 OpenClaw Skill 安装和使用"
      }
    ],
    openclawCta: {
      badge: "OpenClaw 集成",
      title: "秒级接入 OpenClaw",
      desc: "ContextBridge 已作为 OpenClaw Skill 发布。一次安装，即可让你的 AI 智能体即时检索本地文档。",
      steps: [
        { label: "安装", cmd: "pip install cbridge-agent" },
        { label: "启动", cmd: "cbridge init && cbridge start" },
      ],
      cta: "查看集成指南",
    },
    features: [
      {
        icon: Settings,
        title: "交互式配置",
        desc: <>运行 <code className="text-indigo-300">cbridge init</code> 进行引导式设置。可选择内嵌模式或一键接入外部服务。</>
      },
      {
        icon: FolderSync,
        title: "智能目录监控",
        desc: <>使用 <code className="text-indigo-300">cbridge watch</code> 命令轻松追踪项目目录。无需重启，即可实时动态增减上下文来源。</>
      },
      {
        icon: Shield,
        title: "隐私保护",
        desc: "所有数据完全保留在本地。无需云端 API，无需上传，无任何追踪。你的文档永远不会离开你的硬盘——数据主权完全掌握在你手中。"
      },
      {
        icon: Terminal,
        title: "可视化索引",
        desc: <>运行 <code className="text-indigo-300">cbridge index</code> 批量处理文档，内置基于 tqdm 的美观实时进度条。</>
      },
      {
        icon: Database,
        title: "开箱即用",
        desc: "内置 ChromaDB 检索运行时。无需手动安装外部数据库或初始化索引。"
      },
      {
        icon: FileText,
        title: "多格式支持",
        desc: "完美支持 Word、Excel、PDF 及 Markdown。ContextBridge 会自动将多种格式的本地文档解析为高保真 Markdown，为智能体提供精准上下文。"
      }
    ],
    quickStart: "快速开始",
    steps: [
      { comment: "# 1. 全局安装 ContextBridge", cmd: "pip install cbridge-agent" },
      { comment: "# 2. 交互式初始化", cmd: "cbridge init" },
      { comment: "# 3. 添加监控目录", cmd: "cbridge watch add ~/Documents/MyProjects" },
      { comment: "# 4. 构建初始索引（带进度条）", cmd: "cbridge index" },
      { comment: "# 5. 启动实时监控与 MCP 服务", cmd: "cbridge start" },
      { comment: "# 6. 使用内置 Demo 文档进行测试", cmd: 'cbridge search "ContextBridge"' }
    ]
  }
};
