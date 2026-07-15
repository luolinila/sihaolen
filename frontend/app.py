"""
嘶好冷 - 冷笑话桌面小窗
可爱唯美风格，点击获取随机冷笑话
"""

import tkinter as tk
import threading
import requests
import json

API_URL = "http://8.134.62.33:8000/api/joke/random"

# ===== 配色方案：粉色系可爱唯美 =====
BG_MAIN = "#FFF0F5"       # 薰衣草白
BG_CARD = "#FFFFFF"       # 卡片白
ACCENT = "#FF8FAB"        # 珊瑚粉
ACCENT_HOVER = "#FF7099"  # 深粉
TEXT_DARK = "#4A2C3E"     # 深紫灰
TEXT_LIGHT = "#8B6B7A"    # 浅紫灰
SHADOW = "#F0D5E0"        # 阴影粉


class SihaolenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("嘶好冷")
        self.root.geometry("380x240")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        # 居中显示
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 380) // 2
        y = (sh - 240) // 2
        self.root.geometry(f"+{x}+{y}")

        # 禁止最大化
        self.root.attributes("-toolwindow", 1)

        self._build_ui()
        self._fetch_joke()

    def _build_ui(self):
        # ----- 顶部标题 -----
        title_frame = tk.Frame(self.root, bg=BG_MAIN)
        title_frame.pack(pady=(16, 4))

        tk.Label(
            title_frame,
            text="嘶好冷",
            font=("微软雅黑", 16, "bold"),
            fg=ACCENT,
            bg=BG_MAIN,
        ).pack()

        tk.Label(
            title_frame,
            text="每天一点冷，生活更清凉",
            font=("微软雅黑", 9),
            fg=TEXT_LIGHT,
            bg=BG_MAIN,
        ).pack()

        # ----- 笑话卡片 -----
        card = tk.Frame(
            self.root,
            bg=BG_CARD,
            highlightbackground=SHADOW,
            highlightthickness=2,
            padx=16,
            pady=12,
        )
        card.pack(padx=20, pady=(8, 12), fill="both", expand=True)

        self.joke_label = tk.Label(
            card,
            text="正在加载冷笑话...",
            font=("微软雅黑", 11),
            fg=TEXT_DARK,
            bg=BG_CARD,
            wraplength=310,
            justify="center",
        )
        self.joke_label.pack(expand=True)

        self.category_label = tk.Label(
            card,
            text="",
            font=("微软雅黑", 9),
            fg=TEXT_LIGHT,
            bg=BG_CARD,
        )
        self.category_label.pack(pady=(2, 0))

        # ----- 按钮 -----
        self.btn = tk.Button(
            self.root,
            text="再来一条",
            font=("微软雅黑", 11, "bold"),
            fg="white",
            bg=ACCENT,
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=28,
            pady=6,
            cursor="hand2",
            command=self._fetch_joke,
        )
        self.btn.pack(pady=(0, 16))

        # 按钮 hover 效果
        self.btn.bind("<Enter>", lambda e: self.btn.configure(bg=ACCENT_HOVER))
        self.btn.bind("<Leave>", lambda e: self.btn.configure(bg=ACCENT))

    def _fetch_joke(self):
        """异步获取笑话"""
        self.btn.configure(state="disabled", text="获取中...")
        threading.Thread(target=self._request, daemon=True).start()

    def _request(self):
        try:
            resp = requests.get(API_URL, timeout=10)
            data = resp.json()
            if "error" in data:
                self._show_error(data["error"])
                return
            content = data.get("content", "暂无冷笑话")
            category = data.get("category", "")
            self.root.after(0, self._show_joke, content, category)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_joke(self, content, category):
        self.joke_label.configure(text=content)
        self.category_label.configure(text=f"「{category}」")
        self.btn.configure(state="normal", text="再来一条")

    def _show_error(self, msg):
        self.joke_label.configure(text=f"获取失败\n{msg}", fg="#CC6666")
        self.category_label.configure(text="")
        self.btn.configure(state="normal", text="重试")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SihaolenApp().run()
