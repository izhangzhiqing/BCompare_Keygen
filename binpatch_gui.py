import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar

from binpatch_core import patch_file, parse_find_replace


# ---- 现代扁平配色（向 Web 版靠拢） ----
BG = "#ffffff"          # 页面背景
CARD = "#f5f5f5"        # 卡片背景（Web 版表单灰）
BORDER = "#d1d5db"      # 卡片/输入框边框
TEXT = "#111827"        # 主文字
MUTED = "#6b7280"       # 辅助文字
ACCENT = "#10b981"      # 主色 emerald
ACCENT_HOVER = "#059669"
ACCENT_ACTIVE = "#047857"
BLUE = "#2196F3"        # Web 版统计按钮蓝
BLUE_HOVER = "#1e88e5"
SECONDARY = "#e5e7eb"   # 未选中胶囊背景（在灰卡片上仍可见）
SECONDARY_HOVER = "#d1d5db"

FONT = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)


class ModernButton(tk.Button):
    """扁平主按钮，带 hover 效果。"""
    def __init__(self, master, **kwargs):
        self._bg = kwargs.pop("bg", ACCENT)
        self._fg = kwargs.pop("fg", "white")
        self._hover = kwargs.pop("hover_bg", ACCENT_HOVER)
        self._active = kwargs.pop("active_bg", ACCENT_ACTIVE)
        super().__init__(
            master, bg=self._bg, fg=self._fg,
            activebackground=self._active, activeforeground=self._fg,
            relief="flat", borderwidth=0, cursor="hand2",
            font=FONT_BOLD, padx=16, pady=8, **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))


class SecondaryButton(tk.Button):
    """次要按钮（灰底）。"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master, bg="white", fg=TEXT,
            activebackground=SECONDARY_HOVER, activeforeground=TEXT,
            relief="flat", borderwidth=0, cursor="hand2",
            highlightbackground=BORDER, highlightthickness=1,
            font=FONT, padx=16, pady=8, **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=SECONDARY))
        self.bind("<Leave>", lambda e: self.config(bg="white"))


class SegmentedControl(tk.Frame):
    """胶囊分段选择器（单选）。"""
    def __init__(self, master, options, variable, command=None, **kwargs):
        super().__init__(master, bg=CARD, **kwargs)
        self.variable = variable
        self.command = command
        self.buttons = []
        for value, text in options:
            btn = tk.Radiobutton(
                self, text=text, variable=variable, value=value,
                indicatoron=0, bg=SECONDARY, fg=TEXT,
                selectcolor=ACCENT, activebackground=SECONDARY_HOVER,
                activeforeground=TEXT, relief="flat", borderwidth=0,
                cursor="hand2", font=FONT, command=self._on_click
            )
            btn.pack(side="left", padx=(0, 4))
            self.buttons.append((value, btn))
        self._refresh()
        variable.trace_add("write", lambda *args: self._refresh())

    def _refresh(self):
        val = self.variable.get()
        for value, btn in self.buttons:
            if value == val:
                btn.config(bg=ACCENT, fg="white", activebackground=ACCENT_HOVER)
            else:
                btn.config(bg=SECONDARY, fg=TEXT, activebackground=SECONDARY_HOVER)

    def _on_click(self):
        self._refresh()
        if self.command:
            self.command()


class FlatDropdown(tk.Frame):
    """自定义扁平下拉框（白底 + 细边框 + 下箭头 + 菜单）。"""
    def __init__(self, master, variable, values, width=12, **kwargs):
        super().__init__(master, bg="white", highlightbackground=BORDER,
                         highlightthickness=1, **kwargs)
        self.variable = variable
        self.values = values
        self.label = tk.Label(self, textvariable=variable, bg="white", fg=TEXT,
                              font=FONT, anchor="w", padx=8, pady=5, width=width)
        self.label.pack(side="left", fill="x", expand=True)
        self.arrow = tk.Label(self, text="▼", bg="white", fg=MUTED,
                              font=(FONT[0], 8), padx=6, pady=5)
        self.arrow.pack(side="right")

        self.menu = tk.Menu(self, tearoff=0, bg="white", fg=TEXT,
                            activebackground=ACCENT, activeforeground="white",
                            relief="flat", borderwidth=0)
        for v in values:
            self.menu.add_command(label=v, command=lambda val=v: self._select(val))

        for w in (self, self.label, self.arrow):
            w.bind("<Button-1>", self._show)
            w.bind("<Enter>", lambda e: self.config(highlightcolor=ACCENT))
            w.bind("<Leave>", lambda e: self.config(highlightcolor=BORDER))

    def _show(self, event=None):
        self.menu.post(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())

    def _select(self, value):
        self.variable.set(value)


class ModernEntry(tk.Entry):
    """扁平输入框，聚焦时显示主色边框。"""
    def __init__(self, master, textvariable, **kwargs):
        kwargs.setdefault("width", 60)
        super().__init__(
            master, textvariable=textvariable,
            bg="white", fg=TEXT, insertbackground=TEXT,
            relief="flat", borderwidth=5,
            highlightbackground=BORDER, highlightcolor=ACCENT,
            highlightthickness=1, font=FONT, **kwargs
        )


def build_card(parent, title):
    """构建带标题和左侧标识线的白色卡片。"""
    card = tk.Frame(parent, bg=CARD, bd=0, highlightbackground=BORDER,
                    highlightthickness=1)
    header = tk.Frame(card, bg=CARD)
    header.pack(fill="x", padx=12, pady=(8, 4))
    tk.Frame(header, bg=ACCENT, width=3, height=12).pack(side="left", padx=(0, 6))
    tk.Label(header, text=title, bg=CARD, fg=TEXT, font=FONT_SECTION).pack(
        side="left")
    body = tk.Frame(card, bg=CARD)
    body.pack(fill="x", padx=12, pady=(0, 10))
    return card, body


class BinPatchApp:
    def __init__(self, root):
        self.root = root
        root.title("二进制文件查找 / 替换（Windows）")
        root.geometry("640x760")
        root.minsize(640, 700)
        root.resizable(False, True)
        root.configure(bg=BG)

        self.file_path = StringVar()
        self.mode = StringVar(value="text")
        self.encoding = StringVar(value="utf-8")
        self.scope = StringVar(value="all")   # all / first / last
        self.find_var = StringVar(value="p1+wk")
        self.repl_var = StringVar(value="pn+wk")
        self.status = StringVar(value="请选择文件后开始操作。")

        self._build_header()
        self._build_file_card()
        self._build_mode_card()
        self._build_find_card()
        self._build_option_card()
        self._build_action_area()
        self._build_status_bar()

        self._on_mode_change()

    # ---------- 界面构建 ----------
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=18, pady=(12, 4))
        tk.Label(header, text="二进制文件查找 / 替换", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(anchor="w")
        tk.Label(header, text="通用字节级查找替换 · 替换后原文件自动备份为 .bak",
                 bg=BG, fg=MUTED, font=FONT_SUB).pack(anchor="w", pady=(2, 0))

    def _build_file_card(self):
        card, body = build_card(self.root, "文件")
        card.pack(fill="x", padx=18, pady=4)
        row = tk.Frame(body, bg=CARD)
        row.pack(fill="x")
        ModernEntry(row, self.file_path, width=52, state="readonly",
                    readonlybackground="#f9fafb").pack(
            side="left", fill="x", expand=True, padx=(0, 10))
        SecondaryButton(row, text="选择文件…", command=self.choose_file).pack(
            side="left")

    def _build_mode_card(self):
        card, body = build_card(self.root, "匹配模式")
        card.pack(fill="x", padx=18, pady=4)

        SegmentedControl(body, [("text", "文本字符串"), ("hex", "十六进制字节")],
                         self.mode, command=self._on_mode_change).pack(anchor="w")

        self.enc_row = tk.Frame(body, bg=CARD)
        tk.Label(self.enc_row, text="编码：", bg=CARD, fg=TEXT,
                 font=FONT).pack(side="left")
        FlatDropdown(self.enc_row, self.encoding,
                     ["utf-8", "gbk", "ascii", "latin-1"], width=10).pack(
            side="left", padx=(4, 0))
        tk.Label(self.enc_row, text="（十六进制模式无需编码）", bg=CARD,
                 fg=MUTED, font=FONT_SMALL).pack(side="left", padx=(8, 0))

    def _build_find_card(self):
        card, body = build_card(self.root, "查找 / 替换")
        card.pack(fill="x", padx=18, pady=4)

        tk.Label(body, text="查找", bg=CARD, fg=TEXT, font=FONT).pack(anchor="w")
        ModernEntry(body, self.find_var).pack(fill="x", pady=(2, 2))
        tk.Label(body, text="十六进制：每两字符一字节，空格可省略；文本：按所选编码转字节",
                 bg=CARD, fg=MUTED, font=FONT_SMALL).pack(anchor="w")

        tk.Label(body, text="替换", bg=CARD, fg=TEXT,
                 font=FONT).pack(anchor="w", pady=(6, 0))
        ModernEntry(body, self.repl_var).pack(fill="x", pady=(2, 2))
        tk.Label(body, text="替换为留空表示删除匹配内容",
                 bg=CARD, fg=MUTED, font=FONT_SMALL).pack(anchor="w")

    def _build_option_card(self):
        card, body = build_card(self.root, "替换范围")
        card.pack(fill="x", padx=18, pady=4)
        SegmentedControl(
            body,
            [("all", "替换全部"), ("first", "仅替换第一处"), ("last", "仅替换最后一处")],
            self.scope,
        ).pack(anchor="w")
        tk.Label(body, text="默认替换全部匹配；选择其一可缩小范围",
                 bg=CARD, fg=MUTED, font=FONT_SMALL).pack(anchor="w", pady=(6, 0))

    def _build_action_area(self):
        f = tk.Frame(self.root, bg=BG)
        f.pack(fill="x", padx=18, pady=(6, 8))
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)
        ModernButton(f, text="统计匹配次数", command=self.count_only,
                     bg=BLUE, hover_bg=BLUE_HOVER).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        ModernButton(f, text="查找并替换（生成 .bak）", command=self.do_patch).grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

    def _build_status_bar(self):
        bar = tk.Label(self.root, textvariable=self.status, bg=CARD,
                       fg=TEXT, font=FONT, anchor="w", padx=16, pady=14)
        bar.pack(side="bottom", fill="x")

    # ---------- 交互逻辑 ----------
    def _on_mode_change(self):
        if self.mode.get() == "text":
            self.enc_row.pack(fill="x", pady=(10, 0))
        else:
            self.enc_row.pack_forget()

    def choose_file(self):
        p = filedialog.askopenfilename(title="选择要处理的文件")
        if p:
            self.file_path.set(p)
            self.status.set(f"已选择文件：{p}")

    def _resolve(self):
        """校验并返回 (find, repl, kw)。"""
        if not self.file_path.get():
            raise ValueError("请先选择文件")
        find = self.find_var.get()
        repl = self.repl_var.get()
        mode = self.mode.get()
        if mode == "hex":
            if not find:
                raise ValueError("查找内容不能为空")
            return find, repl, dict(mode="hex")
        return find, repl, dict(encoding=self.encoding.get(), mode="text")

    def count_only(self):
        try:
            find, repl, kw = self._resolve()
            find_b, _ = parse_find_replace(
                find, repl, kw.get("encoding", "utf-8"), kw.get("mode", "text"))
        except (ValueError, UnicodeEncodeError) as e:
            messagebox.showerror("错误", str(e))
            return
        data = open(self.file_path.get(), "rb").read()
        n = data.count(find_b)
        self.status.set(f"匹配到 {n} 处。")
        messagebox.showinfo("统计结果", f"匹配到 {n} 处。")

    def do_patch(self):
        try:
            find, repl, kw = self._resolve()
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        try:
            scope = self.scope.get()
            done, bak = patch_file(
                self.file_path.get(), find, repl,
                encoding=kw.get("encoding", "utf-8"),
                mode=kw.get("mode", "text"),
                first_only=(scope == "first"),
                last_only=(scope == "last"),
            )
        except (ValueError, UnicodeEncodeError) as e:
            messagebox.showerror("错误", str(e))
            return
        if done == 0:
            self.status.set("未找到匹配内容，未修改文件。")
            messagebox.showinfo("完成", "未找到匹配内容，未修改文件。")
            return
        msg = f"已替换 {done} 处。\n原文件已备份为：{bak}\n替换结果已写回原文件。"
        self.status.set(msg)
        messagebox.showinfo("完成", msg)


if __name__ == "__main__":
    root = tk.Tk()
    BinPatchApp(root)
    root.mainloop()
