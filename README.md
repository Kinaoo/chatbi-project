# ChatBI - 对话式数据分析平台

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](http://159.75.111.169:8501)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介
ChatBI 是一个基于大模型（智谱 GLM-4-Flash）的自然语言查询系统，能够将业务问题自动转换为 SQL，并返回数据表格和图表。支持多种图表类型（柱状图、折线图、饼图），并具备缓存、只读数据库、密码保护等生产级特性。

## 功能特点
- 🔍 **自然语言转 SQL**：用户用中文提问，自动生成可执行的 SQL 语句。
- 📊 **自动图表生成**：根据数据特征和用户意图，自动选择柱状图、折线图或饼图。
- 🗃️ **特殊字段支持**：正确处理包含连字符、斜杠的字段名（如 `sub-category`）。
- ⚡ **缓存机制**：相同问题 1 小时内直接返回结果，节省 API 调用。
- 🔒 **安全加固**：数据库只读模式，防止误操作；可选密码认证。
- 🐳 **容器化部署**：提供 Dockerfile，一键启动。
- ⚙️ **系统服务**：支持 systemd，开机自启，异常自动重启。

## 技术栈
- **Python 3.10**
- **Streamlit** – 快速构建 Web 界面
- **OpenAI API**（兼容智谱 GLM-4-Flash）
- **SQLite** – 轻量级数据库
- **Matplotlib / Seaborn** – 数据可视化

## 快速开始

### 环境要求
- Python 3.10+
- 智谱 AI API Key（[免费申请](https://open.bigmodel.cn/)）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/kinao-python/chatbi-project.git
   cd chatbi-project
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   python3 -m venv chatbi_env
   source chatbi_env/bin/activate
   pip install -r requirements.txt
   ```

3. **配置 API Key**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的智谱 API Key
   nano .env
   ```

4. **准备数据**  
   执行以下脚本自动下载 Superstore 数据集并导入 SQLite（约 3MB）：
   ```bash
   python prepare_data.py
   ```
   确保 `superstore.db` 文件出现在项目根目录。

5. **运行应用**
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```
   访问 `http://localhost:8501` 或 `http://你的服务器IP:8501`。

### Docker 部署
```bash
# 构建镜像
docker build -t chatbi .

# 运行容器（挂载数据库文件和环境变量）
docker run -d -p 8501:8501 \
  -v $(pwd)/superstore.db:/app/superstore.db \
  -v $(pwd)/.env:/app/.env \
  --name chatbi chatbi
```

### systemd 服务（Linux）
1. 将 `chatbi.service.example` 复制为 `/etc/systemd/system/chatbi.service` 并修改路径。
2. 重新加载 systemd：`sudo systemctl daemon-reload`
3. 启动服务并设置开机自启：
   ```bash
   sudo systemctl enable chatbi
   sudo systemctl start chatbi
   ```
4. 查看状态：`sudo systemctl status chatbi`

## 项目结构
```
chatbi-project/
├── app.py                  # Streamlit 前端界面
├── chatbi_core.py          # 核心逻辑（LLM 调用、SQL 执行、图表生成）
├── schema_info.txt         # 数据库表结构描述
├── prompt_template.txt     # LLM 提示词模板
├── prepare_data.py         # 数据预处理脚本
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像构建文件
├── .env.example            # 环境变量示例
├── chatbi.service.example  # systemd 服务示例文件
├── CONTRIBUTING.md         # 贡献指南
├── LICENSE                 # MIT 许可证
├── .gitignore              # Git 忽略文件
├── README.md               # 项目说明
└── superstore.db           # SQLite 数据库（需自行生成）
```

## 常见问题

### 1. API 调用失败，提示余额不足或认证错误
- 检查 `.env` 中的 API Key 是否正确。
- 确认智谱账户有足够余额（免费额度通常够用）。

### 2. 生成的 SQL 执行失败或返回空结果
- 查看日志文件 `chatbi.log` 中的错误信息。
- 检查 `schema_info.txt` 是否与实际数据库字段一致。
- 尝试修改 `prompt_template.txt`，增加更明确的字段说明。

### 3. 图表未生成
- 确认问题中包含“画图”、“柱状图”、“折线图”、“饼图”等关键词。
- 检查查询结果数据格式是否适合绘制图表（如柱状图需要两列，一列类别一列数值）。
- 查看 `charts/` 目录是否有图片生成。

### 4. 服务无法访问（外部）
- 确保服务器防火墙开放了 8501 端口。
- 如果在云服务器上，检查安全组规则。

## 贡献
欢迎提交 Issue 和 Pull Request。详细请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证
本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式
- 作者：kinao-python
- GitHub：[https://github.com/kinao-python/chatbi-project](https://github.com/kinao-python/chatbi-project)
```

---

## 2. 更新 `.env.example`（增加密码说明）

将 `.env.example` 内容替换为：

```
ZHIPU_API_KEY=your_key_here
# 可选：若启用 Streamlit 密码认证，请在 .streamlit/secrets.toml 中设置 ACCESS_PASSWORD
# 并参考 README 中的说明配置。
```

---

## 3. 创建 `chatbi.service.example`（systemd 服务模板）

新建文件 `chatbi.service.example`，内容如下：

```ini
[Unit]
Description=ChatBI Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/chatbi_project
ExecStart=/root/chatbi_project/chatbi_env/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> 用户需根据实际路径修改 `WorkingDirectory` 和 `ExecStart`。

---

## 4. 创建 `CONTRIBUTING.md`（贡献指南）

新建文件 `CONTRIBUTING.md`，内容如下：

```markdown
# 贡献指南

感谢你对 ChatBI 项目的关注！欢迎通过 Issue 或 Pull Request 参与贡献。

## 报告问题
- 请先搜索已有 Issue 避免重复。
- 描述清晰，包括复现步骤、错误日志、环境信息。

## 提交代码
1. Fork 本仓库。
2. 创建你的特性分支：`git checkout -b feature/your-feature`。
3. 提交更改：`git commit -m 'Add some feature'`。
4. 推送到分支：`git push origin feature/your-feature`。
5. 打开 Pull Request。

## 代码风格
- 遵循 PEP 8。
- 为新增功能添加注释或文档。

## 本地开发环境
参考 README 中的“快速开始”搭建本地环境。
```

---

## 5. 更新 `LICENSE`（添加 MIT 协议全文）

如果仓库中没有 `LICENSE` 文件，或内容不完整，请创建 `LICENSE` 文件并粘贴：

```
MIT License

Copyright (c) 2026 kinao-python

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 6. 更新 `.gitignore`（可选，忽略 `superstore.csv`）

如果希望将原始数据文件排除在版本控制之外，可以在 `.gitignore` 中添加：

```
superstore.csv
```

---

## 7. GitHub 仓库元信息（需在网页操作）

### 添加 About 描述
在仓库首页右上角点击齿轮图标 ⚙️，编辑：
- **Description**：基于大模型（智谱 GLM-4-Flash）的自然语言数据分析平台，支持自动生成 SQL、图表和对话式交互。
- **Website**：可留空或填入 `http://159.75.111.169:8501`。
- **Topics**：添加 `chatbi`、`streamlit`、`llm`、`sql`、`data-analysis`。

---

### 下一步操作
1. 将上述文件内容分别替换或创建。
2. 执行 Git 提交并推送：
   ```bash
   git add .
   git commit -m "Docs: Improve README, add service example, CONTRIBUTING, LICENSE"
   git push origin master
   ```

完成这些后，你的 GitHub 仓库将更加专业和完善。如果还有任何需要调整的地方，随时告诉我。
