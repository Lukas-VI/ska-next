# Acknowledgements / 致谢与参考

SKA-NEXT 是一个学习型、实验型聊天机器人服务项目。项目的早期 `main`（现保存在 `legacy-main` 分支）和当前 `master/main` 实现都参考了开源社区中关于聊天机器人、LLM Agent、OpenAI-compatible API、MCP 工具调用和异步服务编排的方案。这里集中列出已知参考、依赖生态与致谢对象。

如果你发现本项目遗漏了应署名的来源，请提交 issue 或 PR，我会补充到本文件中。

## Core References

- [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)
  - 本项目当前 Agent 实现主要围绕 Qwen-Agent 的 `Assistant`、工具调用、MCP 配置和 OpenAI-compatible 模型服务接入方式展开。
  - `SKA-main/Agent/Kynia_qwen.py`、`SKA-main/Agent/Kynia_Pssive.py` 与 `SKA-main/core/core.py` 中的 Qwen Agent 调用链路受其接口设计和示例用法启发。

- [LLOneBot](https://llonebot.com/)
  - 本项目的 QQ 消息接入、事件流监听和发送消息链路参考了 OneBot/LLOneBot 生态中的接口思路。
  - `SKA-main/server/L2Bot_server.py` 和事件处理模块围绕本地 bot HTTP/event 接口进行实验性封装。

- [Ollama](https://ollama.com/) / [ollama/ollama](https://github.com/ollama/ollama)
  - 本项目使用本地 OpenAI-compatible / Ollama 风格接口作为模型服务实验入口。
  - `SKA-main/server/LLM/Ollama_API.py`、`SKA-main/server/Ollama_API.py` 和若干 misc 示例保留了本地模型服务调用痕迹。

- [FastAPI](https://github.com/fastapi/fastapi) and [Uvicorn](https://github.com/encode/uvicorn)
  - 本项目中用于快速搭建本地 HTTP 服务和回调测试服务。
  - `SKA-main/misc/recive.py` 与 `SKA-main/misc/test_API.py` 包含相关实验代码。

- [Model Context Protocol](https://github.com/modelcontextprotocol) and [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
  - 本项目参考 MCP 的工具调用/外部能力接入思路。
  - Qwen-Agent 配置中曾接入或测试过 `mcp-server-time`、`mcp-server-fetch`、Playwright MCP、`bing-cn-mcp`、`12306-mcp`、`howtocook-mcp`、`mcp-calculator` 等工具服务。

## Implementation Notes

- 项目中的核心调度、事件封装、消息过滤、IO package、被动回复策略和超时机制是围绕上述生态进行的二次实验和自定义实现。
- 部分代码来自快速原型阶段，文件名、注释和结构仍保留探索痕迹；它们不应被理解为对上游项目的官方实现或官方推荐用法。
- 迁移到 GitHub 时，`ska-next` 曾因历史提交中包含 xAI API Key 被 GitHub Push Protection 拦截；迁移版已做历史脱敏。

## Branch History

- `legacy-main`：保留早期单提交 `main`，作为迁移前后历史对照。
- `master`：当前默认分支，保留从 Gitee 迁移并脱敏后的主要开发历史。
- `main`：已同步到 `master`，用于避免 GitHub/Gitee 默认分支差异造成历史不可见。

## License and Third-party Work

本仓库当前使用 LGPL-2.1 license 文件。第三方项目、工具、框架和模型服务各自遵循其原始许可证、使用条款与安全要求。本项目仅表示学习、实验和集成参考；任何复用、分发或部署都应同时遵守对应上游项目的 license。
