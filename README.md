> ⚠️ **特别声明 / Disclaimer**
>
> 本项目**仅供学习与技术研究使用**，**一切与本人无关**。请勿用于任何商业用途或违反所在地法律法规与目标网站（如有道）服务条款/robots 协议的行为。  
> 使用本项目造成的任何后果由使用者自行承担；如涉及版权或其他合规问题，请在第一时间联系以便及时处理与删除相关内容。


# Youdao JSONAPI Wrapper

一个用 **FastAPI** 封装的有道 `jsonapi_s` 查询服务。  
输入单词，服务会生成所需 `sign`（`MD5(word + "webdict")`），请求有道接口并解析**基础释义**（按词性 `adj./n./adv.` 等），同时保留原始字段，方便二次开发。

---

## ✨ 功能特性

- `GET /define?word=xxx`：查询单词  
  - 返回结构化 `definitions`（列表）与已拼接的 `text`（多段文本）
  - 支持 `lang` 参数（默认 `en`）
  - `raw=true` 时附带原始 JSON
- 内置 **CORS**，前端可直接调用
- 提供 **Docker** 封装，一条命令即可运行

---

## 📁 项目结构

```javascript
├── app.py              # FastAPI 应用（主逻辑）
├── requirements.txt    # Python 依赖
└── Dockerfile          # 容器构建

```

---

## 🚀 快速开始

### 1) 本地运行（Python）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（默认 http://localhost:8000）
python app.py
```
### 2) Docker 运行

```bash
# 构建镜像
docker build -t youdao-api .

# 启动容器
docker run -p 8000:8000 --name youdao youdao-api
```
### 请求示例
```bash
curl "http://localhost:8000/define?word=good"
```
### 返回示例
```json
{
  "word": "good",
  "lang": "en",
  "sign": "96eea02156f165866c59ad446fcfa7ed",
  "definitions": [
    {"pos":"adj.","tran":"优良的；能干的，擅长的；…"},
    {"pos":"n.","tran":"善，正义；好事；…"},
    {"pos":"adv.","tran":"好地；彻底地，完全地"},
    {"tran":"【名】（Good）…"}
  ],
  "text": "adj.\n优良的；能干的，擅长的；…\nn.\n善，正义；好事；…\nadv.\n好地；彻底地，完全地\n【名】（Good）…",
  "source": "https://dict.youdao.com/jsonapi_s"
}

```


## 🙏 鸣谢


<div align="center">
  <img src="./img/jetbrains.svg" alt="JetBrains" width="150"/>
  <br>
  <b>特别感谢 <a href="https://www.jetbrains.com/">JetBrains</a> 为开源项目提供免费的 IDE 授权</b>
</div>