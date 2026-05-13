# SKA-NEXT

## 介绍
瞎写的泛用型自律机器人

## 致谢与参考

旧 `main`（现 `legacy-main`）与当前实现都参考了社区中关于聊天机器人、LLM Agent、OpenAI-compatible API、MCP 工具调用和异步服务编排的方案。已知来源与依赖生态见 [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)。

## 软件架构
软件架构计划说明
技术：
1. llonebot
2. 自定义模拟操作
3. uvicorn 
4. MCP 
5. ……

## 安装教程

1.  配置python3.12 +环境，暂时没有requirements可供参考
2.  可以选择安装llonebot进行调试，但存在相当大的风险，如有意外概不负责

3.  配置 Node.js 和 uvx 环境,用于运行工具

    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
4.  暂时只支持Qwen-agent实现,作为替代需要安装此库

    pip install -U "qwen-agent[gui,rag,code_interpreter,mcp]"


## 使用说明

1.  只能部署在服务端

## 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

## 特技

1.  使用 Readme_XXX.md 来支持不同的语言，例如 Readme_en.md, Readme_zh.md
2.  在 ./solutions中查阅优秀案例以供参考
