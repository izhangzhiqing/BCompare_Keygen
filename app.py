import uvicorn
from html import escape
from fastapi import FastAPI, File, UploadFile, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from lic_manager import LicenseEncoder, LicenseDecoder, check_serial
from binpatch_core import parse_find_replace, compute_patch

app = FastAPI()


class KeyRequest(BaseModel):
    username: str = "Test"
    organization: str = "Test Studio"
    serial_number: str = "Abcd-1234"
    quantity: int = 1

    def __str__(self):
        out_str = f"Company: {self.organization}\n"
        out_str += f"Username: {self.username}\n"
        out_str += f"Serial: {self.serial_number}\n"
        out_str += f"Max users: {self.quantity}"
        return out_str


@app.get("/js/bcom.js", response_class=HTMLResponse)
async def get_bcom_js():
    js_content = """
    function validateForm() {
        const quantityInput = document.getElementById('quantity');
        const quantity = quantityInput.value;
        const errorElement = document.getElementById('quantityError');

        if (quantity === "") {
            quantityInput.value = 1;
            return true;
        }

        if (quantity <= 0 || !Number.isInteger(Number(quantity))) {
            errorElement.textContent = '请输入有效的正整数';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    function getFormData() {
        return {
            username: document.getElementById('username').value || "Test",
            organization: document.getElementById('organization').value || "Test Studio",
            serial_number: document.getElementById('serial_number').value || "Abcd-1234",
            quantity: parseInt(document.getElementById('quantity').value) || 1
        };
    }

    function copyToClipboard() {
        text = document.getElementById('keyValue').innerHTML.replaceAll('<br>', '\\r\\n');
        navigator.clipboard.writeText(text).then(() => {
            alert('密钥已复制到剪贴板');
        }).catch(err => {
            console.error('复制失败: ', err);
        });
    }
    
    function displayError(error) {
        if (error != null) { console.error('Error:', error); }
        document.getElementById('result').innerHTML = '<p style="color:red;">生成密钥时出错，请重试。</p>';
    }
    
    function updateKeyDetail(data) {
        const resultDiv = document.getElementById('result');
        resultDiv.style.display = 'block';
        if (data == null) { displayError(); return; }
        if (data.code != 0) { document.getElementById('result').innerHTML = `<p style="color:red;">${data.msg}</p>`; return; }
        resultDiv.innerHTML = `
            <h3>生成结果</h3>
            <div class="key-result">
                <span id="keyValue">${data.key}</span>                
            </div>
            <button class="copy-btn" onclick="copyToClipboard()">复制</button>
            <p><strong>状态:</strong> ${data.msg}</p>
            <h4>密钥解析数据:</h4>
            <ul class="data-list">
                <li><strong>版本:</strong> ${data.key_data.version}</li>
                <li><strong>用户名:</strong> ${data.key_data.username}</li>
                <li><strong>组织名:</strong> ${data.key_data.organization}</li>
                <li><strong>序列号:</strong> ${data.key_data.serial_number}</li>
                <li><strong>数量:</strong> ${data.key_data.quantity}</li>
                <li><strong>随机值:</strong> ${data.key_data.random}</li>
            </ul>
        `;
        return;
    }

    function generateKey() {
        if (!validateForm()) {
            return;
        }

        const formData = getFormData();

        fetch('/BComKeyGen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => updateKeyDetail(data))
        .catch((error) => displayError(error));
    }
    """
    return HTMLResponse(content=js_content, media_type="application/javascript")


@app.get("/css/bcom.css", response_class=HTMLResponse)
async def get_bcom_css():
    css_content = """
    body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #333;
        text-align: center;
    }
    .container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 5px;
    }
    .form-group {
        margin-bottom: 15px;
    }
    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }
    input {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
    }
    button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        width: 100%;
    }
    button:hover {
        background-color: #45a049;
    }
    #result {
        margin-top: 20px;
        padding: 15px;
        background-color: #e8f5e9;
        border-radius: 4px;
        display: none;
    }
    .error {
        color: red;
        font-size: 14px;
        margin-top: 5px;
    }
    .default-value {
        color: #666;
        font-style: italic;
        font-size: 12px;
        margin-top: 2px;
    }
    .key-result {
        margin: 10px 0;
        padding: 10px;
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 4px;
        word-wrap: break-word;
        word-break: break-all;
        overflow-wrap: break-word;
    }
    .data-list {
        list-style-type: none;
        padding: 0;
    }
    .data-list li {
        padding: 5px 0;
        border-bottom: 1px solid #eee;
    }
    .data-list li:last-child {
        border-bottom: none;
    }
    .copy-btn {
        background-color: #2196F3;
        color: white;
        padding: 5px 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        margin-left: 10px;
    }
    .copy-btn:hover {
        background-color: #0b7dda;
    }
    .topnav {
        text-align: center;
        margin-bottom: 12px;
    }
    .topnav a {
        color: #2196F3;
        text-decoration: none;
    }
    .topnav a:hover {
        text-decoration: underline;
    }
    """
    return HTMLResponse(content=css_content, media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def get_bcom_key_generator_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Key Generator</title>
        <link rel="stylesheet" href="/css/bcom.css">
    </head>
    <body>
        <div class="topnav"><a href="/binpatch">二进制文件查找 / 替换工具 &rarr;</a></div>
        <h1>密钥生成器</h1>
        <div class="container">
            <form id="keyForm">
                <div class="form-group">
                    <label for="username">用户名:</label>
                    <input type="text" id="username" name="username" value="Test">
                    <div class="default-value">默认值: Test</div>
                </div>

                <div class="form-group">
                    <label for="organization">组织名:</label>
                    <input type="text" id="organization" name="organization" value="Test Studio">
                    <div class="default-value">默认值: Test Studio</div>
                </div>

                <div class="form-group">
                    <label for="serial_number">序列号:</label>
                    <input type="text" id="serial_number" name="serial_number" value="Abcd-1234">
                    <div class="default-value">默认值: Abcd-1234</div>
                </div>

                <div class="form-group">
                    <label for="quantity">数量 (正整数):</label>
                    <input type="number" id="quantity" name="quantity" min="1" step="1" value="1">
                    <div class="default-value">默认值: 1</div>
                    <div id="quantityError" class="error"></div>
                </div>

                <button type="button" onclick="generateKey()">生成密钥</button>
            </form>

            <div id="result"></div>
        </div>

        <script src="/js/bcom.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/BComKeyGen")
async def gen_bcom_key(req: KeyRequest):
    serial_num = req.serial_number
    if not check_serial(serial_num):
        return {
            "code": -1,
            "msg": "序列号格式错误",
            "key": "",
            "key_data": None
        }

    key = LicenseEncoder(username=req.username, atsite=req.organization, user_num=req.quantity,
                         serial_num=req.serial_number).encode()
    dec = LicenseDecoder(key)
    num, atsite = dec.dec_org()
    version = dec.dec_version()
    rand, serial_num = dec.dec_random()
    username = dec.dec_uname()
    rsp_key = escape(key).replace("\r\n", "<br>")

    return {
        "code": 0,
        "msg": "Success",
        "key": rsp_key,
        "key_data": {
            "version": version,
            "username": username,
            "organization": atsite,
            "serial_number": serial_num,
            "quantity": num,
            "random": rand
        }
    }


# ---------------------------------------------------------------------------
# 通用二进制文件查找/替换工具（与授权无关，纯字节级处理）
# ---------------------------------------------------------------------------

@app.get("/binpatch", response_class=HTMLResponse)
async def get_binpatch_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>二进制查找替换</title>
        <link rel="stylesheet" href="/css/bcom.css">
        <style>
            body { font-family: Arial, sans-serif; max-width: 820px; margin: 0 auto; padding: 20px; color: #333; }
            h1 { color: #333; text-align: center; }
            .container { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type=text], select, textarea {
                width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;
                box-sizing: border-box; font-family: Consolas, Monaco, monospace;
            }
            .row { display: flex; gap: 12px; }
            .row > div { flex: 1; }
            button {
                color: white; padding: 10px 15px; border: none; border-radius: 4px;
                cursor: pointer; font-size: 15px;
            }
            .btn-primary { background-color: #4CAF50; }
            .btn-primary:hover { background-color: #45a049; }
            .btn-secondary { background-color: #2196F3; }
            .btn-secondary:hover { background-color: #0b7dda; }
            .btn-row { display: flex; gap: 12px; margin-top: 10px; }
            #countResult { margin-top: 10px; padding: 10px; background-color: #e8f5e9; border-radius: 4px; display: none; }
            .hint { color: #666; font-size: 12px; margin-top: 2px; }
            .checkbox-row { display: flex; align-items: center; gap: 6px; }
            .checkbox-row input { width: auto; }
            .radio-row { display: flex; align-items: center; gap: 20px; margin-top: 4px; }
            .radio-item { display: flex; align-items: center; gap: 6px; font-weight: normal; margin: 0; }
            .radio-item input { width: auto; }
        </style>
    </head>
    <body>
        <div class="topnav"><a href="/">&larr; 返回密钥生成器</a></div>
        <h1>二进制文件查找 / 替换</h1>
        <div class="container">
            <form id="bpForm" method="post" action="/binpatch/process" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">选择文件：</label>
                    <input type="file" id="file" name="file" required>
                </div>

                <div class="form-group">
                    <label for="mode">匹配模式：</label>
                    <select id="mode" name="mode" onchange="onModeChange()">
                        <option value="text">文本字符串</option>
                        <option value="hex">十六进制字节</option>
                    </select>
                </div>

                <div class="form-group" id="encodingRow">
                    <label for="encoding">文本编码：</label>
                    <select id="encoding" name="encoding">
                        <option value="utf-8">UTF-8</option>
                        <option value="gbk">GBK</option>
                        <option value="ascii">ASCII</option>
                        <option value="latin-1">Latin-1</option>
                    </select>
                </div>

                <div class="row">
                    <div class="form-group">
                        <label for="find">查找内容：</label>
                        <textarea id="find" name="find" rows="3" placeholder="例如：1A2B3C（空格可省略）">p1+wk</textarea>
                        <div class="hint" id="findHint">十六进制，每两个字符一个字节</div>
                    </div>
                    <div class="form-group">
                        <label for="replace">替换为：</label>
                        <textarea id="replace" name="replace" rows="3" placeholder="例如：4D5E6F（留空表示删除）">pn+wk</textarea>
                        <div class="hint">留空可将匹配内容删除</div>
                    </div>
                </div>

                <div class="form-group">
                    <label>替换范围：</label>
                    <div class="radio-row">
                        <label class="radio-item"><input type="radio" name="scope" value="all" checked> 替换全部</label>
                        <label class="radio-item"><input type="radio" name="scope" value="first"> 仅替换第一处</label>
                        <label class="radio-item"><input type="radio" name="scope" value="last"> 仅替换最后一处</label>
                    </div>
                </div>

                <div class="btn-row">
                    <button type="button" class="btn-secondary" onclick="countMatches()">统计匹配次数</button>
                    <button type="submit" class="btn-primary">替换并下载</button>
                </div>

                <div id="countResult"></div>
            </form>
        </div>

        <script>
            function onModeChange() {
                const mode = document.getElementById('mode').value;
                const encRow = document.getElementById('encodingRow');
                const find = document.getElementById('find');
                const hint = document.getElementById('findHint');
                if (mode === 'text') {
                    encRow.style.display = '';
                    find.placeholder = '要查找的文本';
                    hint.textContent = '按所选编码转换为字节';
                } else {
                    encRow.style.display = 'none';
                    find.placeholder = '例如：1A2B3C（空格可省略）';
                    hint.textContent = '十六进制，每两个字符一个字节';
                }
            }

            function countMatches() {
                const form = document.getElementById('bpForm');
                const fd = new FormData(form);
                const resultEl = document.getElementById('countResult');
                resultEl.style.display = 'block';
                resultEl.innerHTML = '计算中...';
                fetch('/binpatch/count', { method: 'POST', body: fd })
                    .then(r => r.json())
                    .then(d => {
                        if (d.code !== 0) {
                            resultEl.innerHTML = '<span style="color:red;">' + d.msg + '</span>';
                        } else {
                            resultEl.innerHTML = '匹配到 <b>' + d.found + '</b> 处，查找内容长度 ' + d.find_len + ' 字节。'
                                + (d.found > 0 ? ' 点击「替换并下载」生成结果文件。' : '');
                        }
                    })
                    .catch(() => { resultEl.innerHTML = '<span style="color:red;">请求失败</span>'; });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/binpatch/count")
async def binpatch_count(
    file: UploadFile = File(...),
    mode: str = Form(...),
    find: str = Form(""),
    replace: str = Form(""),
    encoding: str = Form("utf-8"),
):
    try:
        find_b, _ = parse_find_replace(find, replace, encoding, mode)
    except (ValueError, UnicodeEncodeError) as e:
        return JSONResponse({"code": -1, "msg": str(e)})
    if not find_b:
        return JSONResponse({"code": -1, "msg": "查找内容不能为空"})
    data = await file.read()
    found = data.count(find_b)
    return JSONResponse({"code": 0, "found": found, "find_len": len(find_b)})


@app.post("/binpatch/process")
async def binpatch_process(
    file: UploadFile = File(...),
    mode: str = Form(...),
    find: str = Form(""),
    replace: str = Form(""),
    encoding: str = Form("utf-8"),
    scope: str = Form("all"),
):
    try:
        find_b, repl_b = parse_find_replace(find, replace, encoding, mode)
    except (ValueError, UnicodeEncodeError) as e:
        return HTMLResponse(content=f"<p style='color:red'>错误：{escape(str(e))}</p><p><a href='/binpatch'>返回</a></p>")

    data = await file.read()
    try:
        new_data, done = compute_patch(
            data, find_b, repl_b,
            first_only=(scope == "first"),
            last_only=(scope == "last"),
        )
    except ValueError as e:
        return HTMLResponse(content=f"<p style='color:red'>错误：{escape(str(e))}</p><p><a href='/binpatch'>返回</a></p>")

    if done == 0:
        return HTMLResponse(content="<p style='color:red'>未找到任何匹配内容，未生成文件。</p><p><a href='/binpatch'>返回</a></p>")

    orig_name = file.filename or "file.bin"
    out_name = orig_name
    return Response(
        content=new_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
