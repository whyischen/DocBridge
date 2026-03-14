[**🇨🇳 中文**](README_zh-CN.md) |[**🇬🇧 English**](README.md)

# 📄 DocBridge (Beta)

> **The missing Office document bridge for your local AI Agents.**  
> A seamless bridge that breaks the Word/Excel memory barrier for your local AI Agents (like OpenClaw, Claude Code, and Cursor).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

## 💡 Why build this?

[QMD](https://github.com/tobi/qmd) is currently one of the most powerful, fully local, and low-RAM AI knowledge retrieval engines. However, by design, it is a "text-purist" tool and cannot directly read complex office formats like `.docx` and `.xlsx`.

**DocBridge** is the ultimate sidecar tool built to solve this. Through fully automated background monitoring, the moment you drop a Word or Excel file into a folder, it converts it into high-fidelity Markdown and automatically triggers QMD to update its vector index. 

**Drop your Office files in, and your local AI Agent can instantly "read" and "remember" them. 100% local, zero cloud uploads, and absolute privacy.**

---

## ✨ Core Features

- 👁️ **Millisecond Monitoring**: System-level background file monitoring powered by `watchdog` for zero-latency awareness.
- 🪄 **High-Fidelity Conversion**: Under the hood, it leverages Microsoft's open-source `MarkItDown` engine to accurately parse complex tables and layouts.
- ⚡ **Automated QMD Sync**: Built-in debounce mechanism to smartly trigger `qmd embed` without overloading your system.
- 🔒 **100% Privacy**: No cloud APIs required. Everything is parsed and embedded entirely on your local machine.
- 🤖 **Perfect Agent Companion**: The ideal plugin for MCP-supported local AI frameworks like OpenClaw, Cursor, and Claude Code.

---

## 🏗️ How it works

```mermaid
graph LR
    A[Drop Word/Excel] -->|Background Watch| B(DocBridge)
    B -->|MarkItDown Engine| C[High-Fidelity Markdown]
    C -->|Write to Watch Dir| D(QMD Knowledge Base)
    B -->|Auto Debounce Trigger| E[qmd embed]
    E --> F((AI Agent Fast Search))
