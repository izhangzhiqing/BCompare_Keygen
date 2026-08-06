# Beyond Compare 5 Keygen
基于 Python3 编写，用于生成 Beyond Compare 5.x （截至 5.1 ver 31016）版本注册密钥

## 功能一览

- **生成注册密钥** — 支持 Web 页面与命令行两种方式，生成 Beyond Compare 5 注册密钥（[Web 页面](#基于-web-页面生成注册密钥) / [命令行](#基于命令行生成注册密钥)）
- **二进制文件查找 / 替换工具** — 通用的字节级查找替换，支持十六进制与文本两种模式（[详情](#二进制文件查找--替换工具)）
- **Windows 本地查找替换工具** — 本机文件就地替换并生成 `.bak` 备份（[详情](#windows-本地查找替换工具)）
- **运行** — 安装依赖并启动 Web 服务（[详情](#运行)）
- **使用密钥进行注册** — 将密钥填入 Beyond Compare 完成激活（[详情](#使用密钥进行注册)）
- **注意事项** — 各平台修改 RSA 密钥的说明（[详情](#注意事项)）

## 前置工作
使用 010Editor 等二进制工具，修改 Beyond Compare 可执行文件中内置的 RSA 密钥

修改前：
```
++11Ik:7EFlNLs6Yqc3p-LtUOXBElimekQm8e3BTSeGhxhlpmVDeVVrrUAkLTXpZ7mK6jAPAOhyHiokPtYfmokklPELfOxt1s5HJmAnl-5r8YEvsQXY8-dm6EFwYJlXgWOCutNn2+FsvA7EXvM-2xZ1MW8LiGeYuXCA6Yt2wTuU4YWM+ZUBkIGEs1QRNRYIeGB9GB9YsS8U2-Z3uunZPgnA5pF+E8BRwYz9ZE--VFeKCPamspG7tdvjA3AJNRNrCVmJvwq5SqgEQwINdcmwwjmc4JetVK76og5A5sPOIXSwOjlYK+Sm8rvlJZoxh0XFfyioHz48JV3vXbBKjgAlPAc7Np1+wk
```
修改后（修改字符串末尾的 `p1+wk` 为 `pn+wk` ）：
```
++11Ik:7EFlNLs6Yqc3p-LtUOXBElimekQm8e3BTSeGhxhlpmVDeVVrrUAkLTXpZ7mK6jAPAOhyHiokPtYfmokklPELfOxt1s5HJmAnl-5r8YEvsQXY8-dm6EFwYJlXgWOCutNn2+FsvA7EXvM-2xZ1MW8LiGeYuXCA6Yt2wTuU4YWM+ZUBkIGEs1QRNRYIeGB9GB9YsS8U2-Z3uunZPgnA5pF+E8BRwYz9ZE--VFeKCPamspG7tdvjA3AJNRNrCVmJvwq5SqgEQwINdcmwwjmc4JetVK76og5A5sPOIXSwOjlYK+Sm8rvlJZoxh0XFfyioHz48JV3vXbBKjgAlPAc7Npn+wk
```
<img src="asserts/01.png" alt="image-20240902170702727" style="zoom:50%;" /> 

## 运行

```shell
pip3 install -r requirements.txt
# 启动 Web 服务（默认 http://localhost:8000/）
python3 app.py
```

启动后访问 http://localhost:8000/ 为密钥生成器主页，http://localhost:8000/binpatch 为二进制文件查找 / 替换工具（主页顶部导航也可跳转）。

## 生成注册密钥

```shell
git clone https://github.com/garfield-ts/BCompare_Keygen.git
cd BCompare_Keygen
pip3 install -r requirements.txt
# 对于 Python 3.7 及更早版本，需要手动安装 typing_extensions 模块
pip3 install typing_extensions==4.7.1
```
### 基于 Web 页面生成注册密钥
```shell
python3 app.py
```
<img src="./asserts/08.png" alt="image-20250707160150740" /> 

启动服务后访问 http://localhost:8000/ 即可看到相应页面，该页面由 AI 自动生成。

<img src="./asserts/09.png" alt="image-20250707160652595" style="zoom:67%;" /> 

点击 `生成密钥` 即可按照填写的参数生成注册密钥，点击 `复制` 按钮可将生成的密钥复制到剪贴板中。

<img src="./asserts/10.png" alt="image-20250707160933288" style="zoom:67%;" /> 

在页面底部还会展示注册密钥对应的详细参数，供研究学习使用。

<img src="./asserts/11.png" alt="image-20250707161229638" style="zoom:67%;" /> 

### 基于命令行生成注册密钥

```shell
python3 keygen.py
```
得到可用的注册密钥：
```
--- BEGIN LICENSE KEY ---
7uo7UY8gVANuMyCkDtSZRnNBkDXr1o4msYwtu7GFPaZ9B6naWXfsqEBgD5hM8jm3Sw2L4oFHY53VchaHv4j3q4QNiNxPgcv3qz89nKu3VSgQDVpPrAUWKgkjko5Gvck7BBBJmnKbGZJtDTi21WnJ5AMm7upD6QXgbf2BUS7toxB7jzhFLyotDj59KMGkgXMBXeUoa6T7Yt76MZN6UcHqYG5fMLuBp1JfGxpMXE7AMeUXXLwvAxsJGMkC5oS93WoVLopUoBW4SYNpS7YzzirkqZdRt58TbQpqcvwFeD32X2ZamVAv9SjeQUQhyEwktExFwTc541HrJeDV2xqfr4EgbUprSWEu8p
--- END LICENSE KEY -----
```
默认生成的注册密钥使用以下信息：
```
Version: 0x3d
Serial: Abcd-Efgh
Username: Test
Company: Home
Max users: 1
```
可以通过传入相关参数，自定义注册密钥的信息

<img src="asserts/06.png" alt="image-20240903162908919" style="zoom:50%;" /> 

## 使用密钥进行注册
打开 Beyond Compare 5，此时会弹出 `评估模式错误` 的提示，点击 `输入密钥` 按钮进入注册页面：

<img src="asserts/03.png" alt="image-20240902172200651" style="zoom:50%;" /> 

将脚本生成的注册密钥粘贴到输入框中，点击 `确定` 即可激活。

<img src="asserts/04.png" alt="image-20240902172404873" style="zoom:40%;" /> 

<img src="asserts/05.png" alt="image-20240902172829613" style="zoom:50%;" /> 

## 二进制文件查找 / 替换工具

一个**通用的字节级**查找替换工具（与授权无关），可对任意二进制文件进行内容替换，支持两种匹配模式：

- **十六进制字节**：按字节精确匹配，例如查找 `DEADBEEF`、替换为 `CAFEBABE`（空格可省略），适合修改二进制特征串。
- **文本字符串**：按指定编码（UTF-8 / GBK / ASCII / Latin-1）将文本转为字节后匹配，例如把 `用户` 替换为 `账号`。

启动服务后访问 http://localhost:8000/binpatch （也可从密钥生成器主页顶部的「二进制文件查找 / 替换工具」导航链接直接进入）：

1. 选择要处理的文件；
2. 选择匹配模式并填写「查找内容」与「替换为」（替换为留空即可删除匹配内容）；
3. 在「替换范围」中选择：替换全部 / 仅替换第一处 / 仅替换最后一处（与 Windows 桌面端一致）；
4. 点击 `统计匹配次数` 先确认命中数量；
5. 点击 `替换并下载` 生成 `<原名>` 结果文件（保持原文件名）。

> 默认替换全部匹配；可单选「仅替换第一处」或「仅替换最后一处」。

该工具通过表单上传文件，依赖 `python-multipart`（已包含在 `requirements.txt` 中，随 `pip install -r requirements.txt` 一并安装）。

> Web 版与 Windows 桌面端共用 `binpatch_core.py` 的替换逻辑，匹配模式、编码、替换范围的行为完全一致。

## Windows 本地查找替换工具

除 Web 版本外，项目还提供一个 **Windows 桌面端**本地工具 `binpatch_gui.py`，直接在本机文件系统上操作，适合需要就地修改文件的场景：

- 通过系统文件选择框选取文件；
- 支持两种匹配模式（与 Web 版一致）：
  - **文本字符串**：按 UTF-8 / GBK / ASCII / Latin-1 编码将文本转为字节匹配；
  - **十六进制字节**：按字节精确匹配（空格可省略），适合修改二进制特征串；
- 替换为留空可删除匹配内容；
- 点击 `查找并替换` 后，原文件被重命名为 `<原名>.bak`，替换结果写回原文件名 `<原名>`；
- 提供 `统计匹配次数`；「替换范围」为单选：**替换全部** / **仅替换第一处** / **仅替换最后一处**（默认替换全部，与 Web 版一致）。

运行（需本机 Windows Python，标准库自带 tkinter，无需额外依赖）：

```shell
python binpatch_gui.py
```

> 核心逻辑位于 `binpatch_core.py`，与界面解耦，便于复用与测试。

## 注意事项

1. 在 `macOS` 版中，RSA 密钥位于 `/Applications/Beyond Compare.app/Contents/MacOS/BCompare` 文件中；在 `Windows` 版中，RSA 密钥位于 `BCompare.exe` 文件中

2. `macOS` 版修改密钥后，需要关闭操作系统的 `SIP（System Integrity Protection，系统完整性保护）` 功能，否则会报错「**“Beyond Compare”意外退出**」且无法运行，详见 [少数派的这篇文章](https://sspai.com/post/55066) 。

3. 在 `macOS` 版中，`BCompare` 文件里可以搜到 2 个 RSA 密钥，实际要修改的是第二处密钥。`Windows` 版只有 1 处密钥，直接修改即可。

   <img src="asserts/07.png" alt="image-20250707104436903" style="zoom:100%;" /> 

## TODO

- 集成二进制文件 patch 功能
- ……
