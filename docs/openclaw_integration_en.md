# OpenClaw Integration Guide (Skill Mode)

ContextBridge can be seamlessly integrated into OpenClaw as a native Skill. By providing a simple `SKILL.md` file, you can grant your OpenClaw agents the ability to read and search your local documents instantly.

## Architecture Design: Why SKILL.md?

OpenClaw is a powerful Multi-channel AI Gateway that uses a unique, prompt-based Skill system. Instead of writing complex Node.js or Python plugins, OpenClaw allows you to define a Skill using a simple Markdown file (`SKILL.md`).

1. **Zero-Code Integration**: You don't need to write any integration code. The `SKILL.md` file simply tells the AI *how* to use its existing tools (like `exec` or `bash`) to talk to ContextBridge.
2. **Native Compatibility**: This approach leverages OpenClaw's built-in tool execution capabilities, ensuring maximum compatibility and stability.
3. **Extreme Token Optimization**: The AI will never stuff an entire document into the Prompt. Through the API interface, it only retrieves the most relevant text chunks, greatly saving Tokens and improving answer accuracy.

---

## Step 1: Install ContextBridge

### Important: Clean Up Old Versions

If you have previously installed ContextBridge, old versions in your user directory may override the new version, causing issues (such as i18n not working). Please clean up first:

```bash
# Remove old versions from user directory
rm -f ~/Library/Python/*/lib/python/site-packages/cbridge.py
rm -rf ~/Library/Python/*/lib/python/site-packages/cbridge_agent*
```

### Installation Methods (Choose One)

#### Method 1: pip Installation (Recommended)

```bash
pip install cbridge-agent
```

#### Method 2: Homebrew Installation

```bash
brew install cbridge-agent
```

#### Method 3: Source Installation

```bash
git clone https://github.com/whyischen/context-bridge.git
cd context-bridge
pip install -e .
```

### Language Configuration

ContextBridge supports both English and Chinese interfaces:

```bash
# Switch to Chinese
cbridge lang zh

# Switch to English
cbridge lang en
```

---

## Step 2: Initialize & Configure

### Initialize Workspace

```bash
cbridge init
```

Follow the interactive prompts to set up your workspace (defaults to `~/ContextBridge_Workspace`).

### Add Folders to Watch

Tell ContextBridge which folders contain your documents:

```bash
cbridge watch add /path/to/your/documents
```

### Performance Optimization (Low-End Devices)

If your device has limited performance, you can adjust configuration via environment variables:

```bash
# Reduce the number of files processed concurrently
export CB_MAX_CONCURRENT_FILES=2

# Use smaller embedding batches
export CB_EMBEDDING_BATCH_SIZE=4

# Disable real-time watcher (switch to manual indexing)
export CB_DISABLE_WATCHER=true
```

### Exclude Directory Configuration

Certain directories (like `node_modules`, `.git`) should not be indexed. Configure exclude patterns during `cbridge init`, or manually edit the config file:

```yaml
# ~/.config/cbridge/config.yaml
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/__pycache__/**"
  - "**/*.tmp"
  - "**/dist/**"
  - "**/build/**"
```

---

## Step 3: Start API Service

Before connecting to OpenClaw, you need to have ContextBridge running in the background and providing the API service.

```bash
# Start the API service (binds to 127.0.0.1:9790 by default)
cbridge serve
```

Or start both the watcher and API service:

```bash
# Start full service (watcher + API)
cbridge start
```

Once started, ContextBridge will do two things simultaneously:
1. Start the FastAPI server, listening on `http://127.0.0.1:9790`.
2. Start the Smart Folder Watcher in the background to monitor your local folder changes in real-time.

You can view the complete API documentation (Swagger UI) by visiting `http://127.0.0.1:9790/docs`.

---

## Step 4: Create the OpenClaw Skill

To integrate ContextBridge, you need to create a new Skill in your OpenClaw workspace.

1. Navigate to your OpenClaw skills directory (e.g., `~/.openclaw/skills/` or `<workspace>/skills/`).
2. Create a new folder named `contextbridge`.
3. Inside this folder, create a file named `SKILL.md`.

### Complete SKILL.md Example

```markdown
---
name: local-context-bridge
description: Search and retrieve information from the user's local documents, knowledge bases, policies, and historical data.
metadata: { "openclaw": { "emoji": "🌉", "requires": { "bins": ["curl"] } } }
---

# Local ContextBridge Knowledge Base

This skill allows OpenClaw to search and retrieve information from your local documents (PDF, Word, Excel, Markdown, etc.) using the ContextBridge API.

## 🛠️ PREREQUISITES & INSTALLATION

If you haven't installed the ContextBridge software on your machine yet, follow these steps first:

### 1. Install ContextBridge
Open your terminal and run:
```bash
pip install cbridge-agent
```

### 2. Initialize & Add Documents
Initialize your workspace and tell ContextBridge which folders to index:
```bash
cbridge init
cbridge watch add /path/to/your/documents
```

### 3. Start the API Service
ContextBridge must be running in the background to serve requests:
```bash
# Start both the file watcher and the API server
cbridge start
```
*The API server runs at `http://127.0.0.1:9790` by default.*

---

## 🧠 HOW IT WORKS (For New Users)

ContextBridge acts as a "Semantic Bridge" between your files and OpenClaw:

1.  **Local Indexing**: When you add a folder, ContextBridge scans your documents (PDF, Docx, etc.) and breaks them into small, manageable text chunks.
2.  **Vectorization**: Using a **local** AI embedding model, it converts these chunks into mathematical vectors that represent their *meaning*.
3.  **Semantic Search**: When OpenClaw asks a question, it doesn't just look for exact words. It uses the API to find the most *semantically relevant* chunks from your library.
4.  **100% Private**: All parsing, embedding, and searching happen **entirely on your local machine**. Your private data is never uploaded to any cloud service.

---

## WHEN TO USE THIS SKILL (Trigger Scenarios)

**DIRECTIVE**: If the user's request involves any information that is NOT general public knowledge, you MUST query ContextBridge before answering. Do NOT hallucinate or say "I don't have access" without trying a search first.

### 1. Deep Fact Retrieval (Private Knowledge)
Trigger this when the user asks for specific numbers, names, or facts buried in their local files.
- *Examples*: "What was the total budget for the 2024 marketing campaign?", "Who was the lead engineer for Project X?", "Find the summary of the meeting from last Friday."

### 2. Policy-Based Auditing & Compliance
Trigger this when you are asked to review, verify, or check a document. 
- **CRITICAL**: You must first search for local "policies", "guidelines", "SOPs", or "standards" to establish the ground truth before performing the audit.
- *Examples*: "Does this contract follow our standard procurement policy?", "Review this PR based on our internal coding standards."

### 3. Contextual Drafting (Style & Templates)
Trigger this when the user wants to write something that should match a previous style or use a specific local template.
- *Examples*: "Draft a project proposal using our standard company template", "Write a follow-up email in the same tone as my previous client communications."

### 4. Technical Support & Internal Processes
Trigger this for "How-to" questions regarding internal tools, deployment, or onboarding.
- *Examples*: "How do I set up the local development environment?", "What are the steps for the employee onboarding process?", "How do we handle database migrations?"

## SEARCH STRATEGY (Best Practices)

- **Extract Keywords**: Do NOT search using full conversational sentences. Extract core entities and keywords (e.g., search `"2024 marketing budget"` instead of `"What is the 2024 marketing budget?"`).
- **Iterative Searching**: If your first search returns empty or irrelevant results, try again using synonyms, broader terms, or different keywords.
- **Multiple Queries**: For complex tasks (like auditing), you may need to execute multiple `curl` commands to gather all necessary rules and context.

## HOW TO USE THE API

### 1. Search Documents
Send a POST request to `/api/v1/search` using `curl`.
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/search -H 'Content-Type: application/json' -d '{\"query\": \"2024 marketing budget\", \"top_k\": 3}'"
}
```
*The API returns a JSON array of text chunks. You MUST cite the `metadata.source` in your final answer (e.g., "According to `budget.xlsx`...").*

### 2. Manage Watched Folders
If the user asks to add or remove a folder to their knowledge base:
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/watch/directories -H 'Content-Type: application/json' -d '{\"path\": \"/absolute/path/to/folder\"}'"
}
```
To check currently watched folders:
```json
{
  "command": "curl -s http://127.0.0.1:9790/api/v1/watch/status"
}
```
```

---

## Step 5: Enable the Skill in OpenClaw

Once the `SKILL.md` file is in place, you need to ensure the agent is allowed to use it.

1. Open your OpenClaw configuration (e.g., `~/.openclaw/openclaw.json` or your workspace config).
2. Ensure that `contextbridge` is added to the agent's `tools.allow` list, along with the required `exec` or `bash` tools (or `group:runtime`).

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "allow": [
            "group:runtime",
            "contextbridge"
          ]
        }
      }
    ]
  }
}
```

---

## Real Workflow Demonstration

Suppose a user asks in OpenClaw: **"According to the latest Q3 financial report, what is our marketing expenditure?"**

1. **Intent Recognition**: OpenClaw's LLM analyzes the question and reads the `contextbridge` Skill instructions.
2. **Tool Calling**: The LLM decides to use the `exec` tool to run the `curl` command against the ContextBridge API.
3. **API Response**: ContextBridge instantly returns the 3 most relevant text chunks, along with the source file `Q3_Report.pdf`.
4. **Final Generation**: The LLM synthesizes this data, generates a natural language answer for the user, and attaches the citation source.

If during the conversation, the user modifies the local `Q3_Report.pdf`, ContextBridge's background Watcher will instantly reconstruct the document's vectors. The next second the user asks again, the AI can immediately give an answer based on the latest modifications, entirely without manual intervention.

---

## Troubleshooting

### API Connection Failed

```bash
# Check service status
cbridge status

# Check if API port is occupied
lsof -i :9790

# Restart service
cbridge stop
cbridge start
```

### Cannot Search Latest Content

```bash
# Check watch status
curl -s http://127.0.0.1:9790/api/v1/watch/status

# Force re-index
cbridge index
```

### Internationalization Issues (Commands Not Working)

If commands like `cbridge lang zh` are not working, it may be caused by old version remnants:

```bash
# 1. Clean up old versions
rm -f ~/Library/Python/*/lib/python/site-packages/cbridge.py
rm -rf ~/Library/Python/*/lib/python/site-packages/cbridge_agent*

# 2. Reinstall
pip uninstall cbridge-agent -y
pip install cbridge-agent

# 3. Verify version
cbridge --version
```

### Service Status Check Commands

```bash
# Check service running status
cbridge status

# Check API response
curl -s http://127.0.0.1:9790/api/v1/health

# Check watched directories
cbridge watch list

# View logs
cbridge logs
```

### Curl Command Fails

Ensure that `curl` is installed on the machine running OpenClaw (the Skill metadata specifies `"requires": { "bins": ["curl"] }`).

```bash
# Check if curl is installed
curl --version

# If not installed, install via Homebrew
brew install curl
```
