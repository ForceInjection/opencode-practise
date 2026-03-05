# OpenCode 深度解析：开源 AI 编码代理的终极形态

在 AI 辅助编程领域，**OpenCode** 正以其 100% 开源、供应商中立（Provider Agnostic）和独特的架构设计，成为 Claude Code 的强力竞争者。作为一个由 Neovim 社区和 [terminal.shop](https://terminal.shop) 创作者打造的工具，OpenCode 不仅是一个 CLI 工具，更是一个完整的 AI 编码代理平台。截至目前，其 GitHub 仓库已获得超过 11.5 万颗 Star。

## 1. 核心技术架构 (Technical Architecture)

OpenCode 的设计超越了简单的“API 包装器”，采用了更为复杂的工程架构以支持长期任务和多端协作。

### 1.1 客户端/服务器 (C/S) 架构

与大多数作为单一进程运行的 CLI 工具不同，OpenCode 采用了 **C/S 架构**。

- **Server**：负责核心逻辑、LLM 上下文管理、文件系统操作以及 LSP（语言服务器协议）交互。目前主要在本地运行，但其架构设计支持未来部署到远程高性能服务器上，允许耗时的 AI 推理和文件索引在后台运行，而不阻塞用户界面。
- **Client**：负责用户交互。目前主要有 TUI（终端界面）和 Desktop App（桌面应用）。官方愿景是未来可通过移动 App 远程驱动运行在其他设备上的 Agent 任务——TUI 前端只是众多可能的客户端之一。

### 1.2 多智能体系统 (Multi-Agent System)

OpenCode 并非单体智能，而是内置了多个专用的 Agent，每个 Agent 都有其特定的权限集 (`PermissionNext`) 和系统提示词。Agent 分为两大类：

#### 主 Agent (Primary Agents) — 通过 `Tab` 键切换

- **Build Agent (默认)**：
  - **职责**：代码实现、重构、文件读写，是日常开发的主力 Agent。
  - **权限**：默认拥有全部工具权限（`edit`、`bash`、`read`、`write` 等），可直接执行文件操作和 Shell 命令。
- **Plan Agent**：
  - **职责**：代码库分析、架构规划、安全探索。
  - **权限**：`edit` 权限被明确 `deny`（仅允许写入 `.opencode/plans/*.md` 计划文件），`bash` 命令默认需要用户确认（`ask`）。适合在接触陌生项目时使用，防止 AI 误删改文件。
  - **特点**：Plan Agent 内部会调度 Explore 子 Agent 并行探索代码库，然后给出结构化的实施方案。

#### 子 Agent (Subagents) — 由主 Agent 内部调度，或通过 `@` 手动调用

- **General Subagent (`@general`)**：
  - **职责**：处理复杂的多步搜索和综合性任务。
  - **权限**：拥有全部工具权限（除 `todoread`/`todowrite` 外），可以修改文件。
  - **特点**：可以并行执行多个工作单元，适合调研和批量操作类任务。在消息中输入 `@general` 即可手动调用。
- **Explore Subagent**：
  - **职责**：快速、只读地探索代码库。**不能修改文件**。
  - **工具**：专精于 `grep`、`glob`、`list`、`read`、`bash`、`codesearch`、`webfetch`、`websearch` 等搜索工具。
  - **特点**：主要由 Plan Agent 在内部自动调度（可同时启动最多 3 个并行探索），不直接暴露给用户切换。

此外还有 `compaction`、`title`、`summary` 三个**隐藏系统 Agent**，分别负责会话压缩、标题生成和摘要生成，由系统自动触发，用户不可见。

### 1.3 权限与安全机制 (Permissions)

OpenCode 内置了精细的权限控制系统（`PermissionNext`），将操作分为三类，确保 AI 的行为可控：

- **Allow**：允许自动执行（如读取非敏感文件、列出目录）。
- **Ask**：需要用户确认（如运行 Shell 命令、修改 `.env` 文件、访问外部目录）。
- **Deny**：明确禁止（如在 Plan 模式下修改代码、读取被忽略的文件）。

系统默认配置了安全策略，例如 `.env` 文件默认为 `ask`，防止密钥泄露；而 `plan` 模式下 `edit` 操作被硬性 `deny`。

### 1.4 技术栈

- **Runtime**：主要使用 **TypeScript** 和 **Bun** 运行时（`packageManager: bun@1.3.10`），利用 Bun 的高性能文件 IO 和原生打包能力。
- **Frontend**：
  - **桌面端（Tauri 版）**：基于 **Tauri 2**（Rust）+ **SolidJS** 构建，兼顾了性能与跨平台兼容性（macOS / Windows / Linux）。
  - **桌面端（Electron 版）**：另有一个基于 **Electron** 的桌面端实现（`packages/desktop-electron`），提供额外的平台兼容选项。
  - **TUI**：终端界面经过深度优化，支持复杂的交互和主题系统，由 Neovim 用户群体驱动设计。
  - **Web**：提供 Web 端界面（`packages/app`），基于 SolidJS + Vite 构建。
- **Database**：使用 **Drizzle ORM + SQLite** 管理 Session、权限和本地状态。

---

## 2. 高级功能深入解析 (Advanced Deep Dive)

### 2.1 Agent Skills：可扩展的技能系统

OpenCode 引入了 **Skills** 概念，这是一种轻量级的、基于 Markdown 的扩展机制。

- **定义方式**：创建名为 `SKILL.md` 的文件，包含 Frontmatter（元数据，如 `name` 和 `description`）和正文内容。
- **搜索路径**（优先级从低到高）：
  1. 全局目录：`~/.claude/skills/`、`~/.agents/skills/`（兼容 Claude Code 等工具的目录约定）
  2. 项目配置目录：`.opencode/skill/**/SKILL.md` 或 `.opencode/skills/**/SKILL.md`
  3. 配置文件中指定的额外路径（`config.skills.paths`）
  4. 远程 URL 下载（`config.skills.urls`）——支持从网络拉取共享 Skill 包
- **应用场景**：你可以创建一个 `Reviewer` skill，里面包含特定的代码审查清单；或者一个 `Database` skill，包含项目特定的 SQL 规范和常用查询。Agent 在运行时可以通过内置的 `skill` 工具加载这些 Skill，从而获得特定领域的“知识”。

### 2.2 会话压缩与上下文管理 (Session Compaction)

为了解决 LLM 上下文窗口限制，OpenCode 实现了一套复杂的**会话内**压缩机制（注意：这不是跨 Session 的持久记忆，而是单次会话内的上下文优化）：

- **自动剪枝 (Pruning)**：当会话中累积的工具调用输出超过 `PRUNE_PROTECT`（40,000 tokens）时，系统会自动触发 `SessionCompaction.prune`，将超过 `PRUNE_MINIMUM`（20,000 tokens）的旧工具输出标记为已压缩。
- **智能保留**：它会保留最近的交互（turns），但会压缩旧的工具调用输出（例如，将长长的 `ls` 或 `read` 结果替换为简短的摘要），同时明确保留关键的 `skill` 工具调用不被压缩。
- **摘要机制**：`SessionSummary` 模块会在消息完成后分析代码变更（diffs），记录增删行数和受影响的文件，确保 AI 即使在长对话后也能“记住”之前修改了哪些文件。
- **插件扩展**：通过 `experimental.session.compacting` 钩子，插件可以向压缩过程注入自定义上下文，甚至完全替换默认的压缩提示词。

### 2.3 工具系统与 MCP 集成

OpenCode 的工具系统 (`Tool`) 极其灵活，不仅支持内置工具，还全面拥抱 **MCP (Model Context Protocol)**。

- **内置工具**：包括 `bash` (执行命令)、`edit`/`multiedit`/`write`/`apply_patch` (文件修改)、`grep`/`glob` (搜索)、`ls`/`read` (文件读取)、`lsp` (语言服务器调用)、`webfetch`/`websearch` (网络检索)、`codesearch` (代码搜索)、`task` (子 Agent 调度)、`todo` (任务管理)、`question` (向用户提问) 等。
- **动态加载**：工具的定义支持动态参数（`zod` schema），并且可以根据当前 Agent 的权限动态启用或禁用，支持通配符模式批量控制。
- **MCP 支持**：OpenCode 可以作为 MCP Client 连接到任何 MCP Server（支持本地 `local` 和远程 `remote` 两种模式）。这意味着你可以通过在 `opencode.json` 中配置 MCP，让 OpenCode 访问 Sentry 错误跟踪、GitHub Issue、企业内部 API，甚至是 Mem0 记忆服务，而无需修改 OpenCode 源码。
- **OAuth 支持**：远程 MCP Server 内置了完整的 OAuth 2.0 认证流程（支持动态客户端注册 RFC 7591），并安全存储 Token。
- **插件自定义工具**：通过插件系统，开发者可以使用 `tool()` 函数自定义新工具，并与内置工具并列可用。

配置示例（添加一个本地 MCP Server）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-mcp-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "my_value"
      }
    }
  }
}
```

### 2.4 ACP 集成：IDE 内无缝使用 AI Agent

**ACP (Agent Client Protocol)** 是一个新兴的开放标准，类似于 LSP（语言服务器协议）但面向 AI Agent。OpenCode 完整实现了 ACP v1 协议，使得它可以作为后端 Agent 集成到多种 IDE 中：

- **支持的编辑器**：JetBrains IDE（IntelliJ IDEA、WebStorm 等）、Zed、Neovim、Emacs 等。
- **工作方式**：OpenCode 作为子进程运行，通过 JSON-RPC over stdio 与编辑器通信，支持 Session 管理、提示处理、文件操作等。
- **启动方式**：`opencode acp` 或 `opencode acp --cwd /path/to/project`。
- **意义**：同一套 Agent 配置可跨编辑器复用，避免厂商锁定。你在终端中使用的 OpenCode 配置和 Skill，可以无缝带入 JetBrains 等 IDE。

### 2.5 持久记忆系统：通过插件和 MCP 实现跨 Session 记忆

OpenCode **核心本身不包含跨 Session 的持久记忆功能**，但得益于其强大的插件系统和 MCP 集成能力，社区已提供了多种成熟的记忆方案：

#### Mem0 / OpenMemory MCP

[Mem0](https://mem0.ai) 提供了 **OpenMemory MCP Server**，这是一个本地优先的私有记忆层，数据存储在本地（基于 Docker + Qdrant 向量库），不依赖云服务，确保数据隐私。在 OpenCode 中集成 Mem0 非常简单：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "mem0-openmemory": {
      "type": "local",
      "command": ["npx", "-y", "mem0-openmemory-server"],
      "enabled": true,
      "environment": {
        "MEM0_API_KEY": "your-api-key"
      }
    }
  }
}
```

配置后，在提示词中输入 `use the mem0-openmemory tool` 即可存储、搜索和管理跨 Session 的记忆。

#### Supermemory 插件

[opencode-supermemory](https://github.com/supermemoryai/opencode-supermemory) 是一个专为 OpenCode 打造的原生插件，提供：

- **自动上下文注入**：每次会话开始时自动加载用户画像、项目知识和相关记忆。
- **关键词检测**：当输入“记住”、“save this”等触发词时自动保存信息。
- **代码库索引**：通过 `/supermemory-init` 命令探索并记忆项目结构和规范。
- **预防性压缩**：在内存接近上限时自动总结和保存上下文。

#### 其他方案

- **opencode-agent-memory**：受 Letta 启发的实验性插件，提供结构化的、可自编辑的记忆块（Memory Blocks），支持跨 Session 共享和自我修改。
- 社区也已在讨论[**内置双范围记忆系统**](https://github.com/anomalyco/opencode/issues/9211)（全局 + 项目级）的 Feature 请求，未来可能会成为内置功能。

---

## 3. OpenCode vs. Claude Code

尽管两者在功能上都致力于实现“自主编码代理”，但在设计哲学上有显著差异：

| 特性         | OpenCode                                            | Claude Code                |
| :----------- | :-------------------------------------------------- | :------------------------- |
| **开源属性** | **100% 开源** (MIT)                                 | 闭源 (Proprietary)         |
| **模型支持** | **供应商中立** (OpenAI, Claude, Google, Local LLMs) | 仅限 Anthropic Claude 系列 |
| **架构**     | **C/S 架构** (支持远程驱动)                         | 主要以 CLI 形式运行        |
| **交互界面** | **TUI (极致终端体验)**, Desktop, Web, IDE (ACP)     | 主要是 CLI                 |
| **代码理解** | **内置 LSP 支持** (更精准的符号分析)                | 基于文本分析               |
| **扩展性**   | MCP, ACP, 插件系统, 自定义 Skill                    | 相对受限                   |

**核心优势总结**：OpenCode 的最大优势在于**不被厂商锁定**。它支持超过 75 种模型（包括 Claude、OpenAI、Gemini、以及通过 LM Studio / Ollama 等运行的本地模型）。随着开源模型（如 Llama、DeepSeek、Qwen）的进步，OpenCode 用户可以随时切换到性价比更高的模型，而 Claude Code 用户只能绑定在 Claude 生态中。此外，OpenCode 还提供了官方托管服务 [OpenCode Zen](https://opencode.ai/zen)，提供经过团队测试和验证的精选模型列表，方便新用户快速上手。

---

## 4. 最佳实践与实战技巧 (Best Practices)

基于 OpenCode 团队的内部开发文档 (`AGENTS.md`)，以下是使用 OpenCode 的最佳实践：

### 4.1 AGENTS.md：项目的“说明书”

在项目根目录创建 `AGENTS.md` 是让 AI 快速理解项目的关键。你可以通过 `/init` 命令自动生成，也可以手动创建。

- **内容建议**：
  - **架构概览**：用自然语言描述模块划分。
  - **技术选型**：明确使用的库（如 "State management: Zustand", "Styling: Tailwind"）。
  - **开发规范**：明确代码风格（见下文）。
- **作用**：OpenCode 会在每次 Session 开始时读取此文件，相当于给 AI 注入了项目的“潜意识”。
- **多源支持**：除了项目级 `AGENTS.md`，还支持全局规则（`~/.config/opencode/AGENTS.md`）、Claude Code 兼容文件，以及通过 `opencode.json` 引用远程 URL 规则。建议将 `AGENTS.md` 提交到 Git 以确保团队一致性。

### 4.2 编码风格指南 (Coding Style)

为了让 AI 生成的代码更易维护，OpenCode 官方推荐以下风格（可写入你的 `AGENTS.md`）：

- **命名规范**：
  - 变量和函数名尽量使用**单字**（如 `pid`, `cfg`, `err`, `opts`, `dir`），除非有歧义。
  - 避免冗长的复合词（如 `inputPID` -> `pid`）。
- **代码结构**：
  - **Early Returns**：尽量使用提前返回，避免深层嵌套的 `if/else`。
  - **No Try/Catch**：除非必须处理异常，否则避免过度使用 try/catch，让错误自然冒泡或由上层处理。
  - **Functional**：优先使用 `map`, `filter`, `flatMap` 等函数式方法，而不是 `for` 循环。
- **工具库使用**：
  - 明确指定优先使用的库（例如：在 Node 环境下优先使用 `Bun.file()` 等原生 API）。

### 4.3 数据库开发规范

如果你的项目涉及数据库，建议在 `AGENTS.md` 中规定：

- **Schema 定义**：明确字段命名风格（如 `snake_case` 用于数据库列，`camelCase` 用于 TS 对象）。
- **迁移策略**：说明如何生成和运行迁移脚本（如 `drizzle-kit generate`）。

---

## 5. 安装与快速开始 (Installation)

OpenCode 提供了多种安装方式，覆盖了主流操作系统和包管理器。

### 5.1 快速安装（跨平台）

```bash
# YOLO 模式安装（macOS / Linux / WSL）
curl -fsSL https://opencode.ai/install | bash

# 通过 npm/bun/pnpm/yarn 全局安装
npm i -g opencode-ai@latest
# 或 bun install -g opencode-ai
```

### 5.2 macOS 用户 (推荐)

```bash
# 推荐：从 anomalyco/tap 安装（更新最快）
brew install anomalyco/tap/opencode

# 或使用官方 Homebrew formula（由 Homebrew 团队维护，更新较慢）
brew install opencode

# 安装桌面版 (Desktop App)
brew install --cask opencode-desktop
```

### 5.3 Windows 用户

```bash
scoop install opencode              # Scoop
choco install opencode              # Chocolatey
npm i -g opencode-ai@latest         # npm
```

### 5.4 Linux 用户

```bash
brew install anomalyco/tap/opencode # Homebrew (Linux)
sudo pacman -S opencode             # Arch Linux (稳定版)
paru -S opencode-bin                # Arch Linux (AUR 最新版)
```

### 5.5 其他安装方式

```bash
mise use -g opencode                        # mise (任意 OS)
nix run nixpkgs#opencode                    # Nix
docker run -it --rm ghcr.io/anomalyco/opencode  # Docker
```

### 5.6 桌面应用 (Desktop App, BETA)

OpenCode 提供了独立的桌面应用，可从 [Releases 页面](https://github.com/anomalyco/opencode/releases) 或 [opencode.ai/download](https://opencode.ai/download) 直接下载：

| 平台                  | 下载文件                              |
| :-------------------- | :------------------------------------ |
| macOS (Apple Silicon) | `opencode-desktop-darwin-aarch64.dmg` |
| macOS (Intel)         | `opencode-desktop-darwin-x64.dmg`     |
| Windows               | `opencode-desktop-windows-x64.exe`    |
| Linux                 | `.deb`, `.rpm`, 或 AppImage           |

### 5.7 IDE 集成

OpenCode 通过 ACP 协议支持多种 IDE 集成：

- **JetBrains IDE**：通过 ACP Agent Registry 直接安装和使用。
- **Zed / Neovim / Emacs**：通过 ACP 协议集成，配置 OpenCode 作为后端 Agent。
- **VSCode**：OpenCode 提供了 VSCode 扩展，在插件市场搜索 **"OpenCode"** 即可安装。

---

## 6. 实战使用指南 (Usage Guide)

### 6.1 初始化与配置

首次进入项目目录，启动 OpenCode 并进行初始化：

```bash
cd my-project
opencode
```

在 TUI 界面中运行 `/init` 命令，这将让 OpenCode 分析你的项目并生成 `AGENTS.md` 文件。这是一个特殊的上下文文件，你可以在其中用自然语言描述项目的架构、编码规范。**OpenCode 会在每次任务前阅读此文件，确保代码风格一致。**

如果你是新用户，首先需要配置 LLM Provider。在 TUI 中运行 `/connect` 命令，选择你的提供商（推荐新用户使用 [OpenCode Zen](https://opencode.ai/zen)）并粘贴 API Key。

### 6.2 场景一：探索陌生代码库 (Plan Mode)

当你接手一个新项目，不知道从何下手时：

1. 启动 OpenCode，按 `Tab` 切换到 **Plan** 模式（界面右下角显示 PLAN）。
2. 输入指令：
   > "分析一下 `src/auth` 目录下的认证逻辑，画一个简单的时序图说明登录流程。"
3. Agent 会读取文件、分析引用，并输出解释。Plan Agent 会内部调度 Explore 子 Agent 并行探索，期间**不会修改任何代码**（仅允许写入计划文件），你可以放心让它随意探索。

### 6.3 场景二：开发新功能 (Build Mode)

确定方案后，切换回 **Build** 模式：

1. 输入指令：
   > "在 `src/utils` 中添加一个 `date_formatter.ts`，实现一个格式化日期的函数，并在 `src/components/Header.tsx` 中使用它显示当前时间。"
2. OpenCode 会：
   - 创建新文件。
   - 编写函数代码。
   - 修改现有组件文件。
   - （可选）运行测试以验证。
3. 如果你对结果不满意，输入 `/undo` 即可瞬间撤销所有更改。

### 6.4 场景三：利用 @general 解决复杂依赖

当你需要引入一个新的库并重构大量代码时：

> "@general 我想把项目中的 axios 替换为 fetch，请先搜索所有使用 axios 的地方，然后制定一个迁移计划。"

`@general` 智能体会进行全局搜索，列出所有受影响的文件，并给出一个分步骤的迁移清单供你审批。

---

**小贴士**：

- **Plan 模式**：适合探索陌生代码库，确保理解项目架构。Plan Agent 会内部调度 Explore 子 Agent 并行搜索，然后给出结构化方案。
- **Build 模式**：适合开发新功能，确保代码质量。
- 使用 `/share` 命令可以将你与 AI 的精彩协作过程生成链接，分享给同事进行 Code Review。
- 经常更新 `AGENTS.md`，它是你“调教”专属 AI 队友的最佳方式。
- 如果需要跨 Session 记忆，可以配置 Mem0 MCP 或 Supermemory 插件（见 2.5 节）。
