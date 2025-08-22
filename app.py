import hashlib, json, socket, requests
import urllib3.util.connection as urllib3_cn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

# ① 强制 IPv4，规避 IPv6 线路/握手问题
urllib3_cn.allowed_gai_family = lambda: socket.AF_INET

URL = "https://dict.youdao.com/jsonapi_s"
PARAMS = {"doctype": "json", "jsonversion": "4"}
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Origin": "https://youdao.com",
    "Referer": "https://youdao.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}
SUFFIX = "webdict"

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def query_youdao(word: str, lang: str = "en") -> tuple[Dict[str, Any], Dict[str, str]]:
    form = {
        "q": word.strip(),
        "le": lang,
        "t": "1",
        "client": "web",
        "keyfrom": SUFFIX,
        "sign": md5_hex(word.strip() + SUFFIX),
    }
    # ② 用 Session，彻底忽略系统/环境代理
    s = requests.Session()
    s.trust_env = False
    s.proxies.update({"http": None, "https": None})
    r = s.post(URL, headers=HEADERS, params=PARAMS, data=form, timeout=15)
    r.raise_for_status()
    return r.json(), form

def get_trs_list(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """稳健地取到基础释义 trs 列表"""
    ec = (data or {}).get("ec") or {}
    word = ec.get("word")
    if isinstance(word, dict):
        w = word
    elif isinstance(word, list) and word:
        w = word[0]
    else:
        return []
    trs = w.get("trs")
    return trs if isinstance(trs, list) else []

def build_text_from_trs(trs_list: List[Dict[str, str]]) -> str:
    """把 [{'pos':'adj.','tran':'...'}, ...] 拼成多段文本"""
    parts: List[str] = []
    for it in trs_list:
        if not isinstance(it, dict):
            continue
        pos  = (it.get("pos")  or "").strip()
        tran = (it.get("tran") or "").strip()
        if not tran:
            # 有些条目放在 tr/l/i，简单兜底（如需更强解析可扩展）
            tr_list = it.get("tr") or []
            texts: List[str] = []
            for tr in tr_list:
                if not isinstance(tr, dict):
                    continue
                l = tr.get("l")
                if isinstance(l, dict):
                    i = l.get("i")
                    if isinstance(i, list):
                        texts += [str(x).strip() for x in i if str(x).strip()]
                    elif isinstance(i, str) and i.strip():
                        texts.append(i.strip())
                t = tr.get("tran")
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
            if texts:
                tran = "；".join(texts)
        if tran:
            parts.append(f"{pos}\n{tran}" if pos else tran)
    return "\n".join(parts)

app = FastAPI(title="Youdao JSONAPI Wrapper", version="1.0.0")

# 允许跨域（如果你在浏览器里直接调这个服务会方便很多）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/define")
def define(
    word: str = Query(..., description="要查询的词"),
    lang: str = Query("en", description="语言代码，默认 en"),
    raw: bool = Query(False, description="是否返回原始 JSON（调试用）")
):
    try:
        data, form_used = query_youdao(word, lang)
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"upstream error: {e}")

    trs_list = get_trs_list(data)
    text = build_text_from_trs(trs_list)

    payload: Dict[str, Any] = {
        "word": word,
        "lang": lang,
        "sign": form_used["sign"],
        "definitions": trs_list,
        "text": text,
        "source": "https://dict.youdao.com/jsonapi_s"
    }
    if raw:
        payload["raw"] = data
    return payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
