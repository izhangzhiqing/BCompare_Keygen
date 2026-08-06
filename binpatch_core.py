import os


def _hex_to_bytes(s):
    s = s.strip().replace(" ", "").replace("\n", "").replace("\t", "")
    if len(s) == 0:
        return b""
    if len(s) % 2 != 0:
        raise ValueError("十六进制长度必须为偶数（每两个字符表示一个字节）")
    return bytes.fromhex(s)


def parse_find_replace(find_str, replace_str, encoding="utf-8", mode="text"):
    """将查找/替换内容转换为字节序列，返回 (find_bytes, replace_bytes)。

    mode="text"：按 encoding 把字符串转为字节；
    mode="hex"：按十六进制解析（空格可省略），与 Web 版一致。
    """
    if mode == "hex":
        return _hex_to_bytes(find_str), _hex_to_bytes(replace_str)
    return find_str.encode(encoding), replace_str.encode(encoding)


def compute_patch(data, find_b, repl_b, first_only=False, last_only=False):
    """在内存中对字节数据做查找替换，返回 (new_data, 实际替换次数)。

    与 GUI / Web 共用同一套替换规则：
    - first_only：只替换首个匹配；
    - last_only：只替换最后一个匹配；
    - 两者均为 False：替换全部匹配。
    若 find_b 为空或 data 中无匹配，返回 (data, 0)。
    """
    if not find_b:
        raise ValueError("查找内容不能为空")

    count = data.count(find_b)
    if count == 0:
        return (data, 0)

    if first_only:
        new_data = data.replace(find_b, repl_b, 1)
        done = 1
    elif last_only:
        idx = data.rfind(find_b)
        new_data = data[:idx] + repl_b + data[idx + len(find_b):]
        done = 1
    else:
        new_data = data.replace(find_b, repl_b)
        done = count

    return (new_data, done)


def patch_file(path, find_str, replace_str, encoding="utf-8", mode="text",
               first_only=False, last_only=False):
    """对二进制文件做查找替换。

    mode="text"：按 encoding 把查找/替换字符串转为字节；
    mode="hex"：把查找/替换按十六进制字节解析（空格可省略）。

    原文件重命名为 <原名>.bak，替换结果写回原路径 <原名>。
    返回 (实际替换次数, .bak 备份路径)；若未找到匹配返回 (0, None)。
    """
    try:
        find_b, repl_b = parse_find_replace(find_str, replace_str, encoding, mode)
    except UnicodeEncodeError as e:
        raise ValueError(f"字符串无法用编码 {encoding} 表示：{e}")
    except ValueError as e:
        raise ValueError(f"十六进制解析失败：{e}")

    with open(path, "rb") as f:
        data = f.read()

    new_data, done = compute_patch(data, find_b, repl_b, first_only, last_only)
    if done == 0:
        return (0, None)

    bak_path = path + ".bak"
    # 原文件备份为 .bak（若已存在则覆盖）
    os.replace(path, bak_path)
    # 替换结果写回原路径
    with open(path, "wb") as f:
        f.write(new_data)

    return (done, bak_path)
