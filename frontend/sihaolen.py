"""
嘶好冷 — 冷笑话桌面小窗
可爱圆润风格 · Canvas 绘制圆角 · Windows 圆角窗口 · 白亮冰蓝色系
"""

import tkinter as tk
import threading
import json
import ctypes
from urllib import request

API_URL = "http://8.134.62.33:8000/api/joke/random"

# ========== 配色（白亮冰蓝系） ==========
BG_MAIN      = "#F5F9FC"   # 冰白底
BG_CARD      = "#FFFFFF"
COLOR_TEXT   = "#3D4A5C"   # 深蓝灰
COLOR_BTN    = "#8ECAE6"   # 冰湖蓝
COLOR_BTN_H  = "#6BB3D9"
COLOR_TITLE  = "#AED4E6"   # 淡蓝
COLOR_SUB    = "#8FA4B8"   # 浅蓝灰
COLOR_BORDER = "#D6E4F0"   # 边框淡蓝
COLOR_SHADOW = "#E8F0F8"


def draw_round_rect(canvas, x1, y1, x2, y2, r, fill, outline="", width=1, **kw):
    """在 Canvas 上画圆角矩形，返回绘制的 id 列表"""
    ids = []
    d = 2 * r
    # 主体
    ids.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="", **kw))
    ids.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline="", **kw))
    # 四角圆弧
    ids.append(canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, fill=fill, outline="", **kw))
    ids.append(canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, fill=fill, outline="", **kw))
    ids.append(canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, fill=fill, outline="", **kw))
    ids.append(canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, fill=fill, outline="", **kw))
    if outline:
        # 描边（画框用）
        canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width)
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width)
    return ids


class SiHaoLengApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("嘶好冷 ❄")
        self.W, self.H = 400, 280
        self.R = 16  # 全局圆角半径

        self.root.geometry(f"{self.W}x{self.H}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        # 窗口居中
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - self.W) // 2
        y = (hs - self.H) // 2
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        # 去原生标题栏
        self.root.overrideredirect(True)
        self.root.configure(bg="#E8F4FA")

        # ---- 主 Canvas ----
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#E8F4FA", highlightthickness=0)
        self.canvas.pack()

        # ---- 窗口圆角（Windows API） ----
        self._round_window_corners(22)

        # 窗口圆角背景
        draw_round_rect(self.canvas, 2, 2, self.W - 2, self.H - 2, 18,
                        fill=BG_MAIN, outline=COLOR_BORDER, width=2)

        # ---- 标题栏 ----
        self._draw_title_bar()

        # ---- 卡片 ----
        self.card_x1, self.card_y1 = 16, 48
        self.card_x2, self.card_y2 = self.W - 16, self.H - 64
        draw_round_rect(self.canvas, self.card_x1, self.card_y1,
                        self.card_x2, self.card_y2, 14,
                        fill=BG_CARD, outline=COLOR_SHADOW, width=2)

        # ---- 卡片内元素 ----
        self.cat_text = self.canvas.create_text(
            self.W // 2, 70, text="", fill=COLOR_SUB,
            font=("Microsoft YaHei UI", 10)
        )
        self.joke_text = self.canvas.create_text(
            self.W // 2, 140, text="", fill=COLOR_TEXT,
            font=("Microsoft YaHei UI", 12),
            width=330, justify="center"
        )
        self.load_text = self.canvas.create_text(
            self.W // 2, 140, text="❄", fill=COLOR_SUB,
            font=("Microsoft YaHei UI", 32)
        )

        # ---- 按钮 ----
        self._draw_button()

        # ---- 底部文字 ----
        self.canvas.create_text(
            self.W // 2, self.H - 14, text="— ❄ 嘶好冷 · 每日一冷 —",
            fill=COLOR_SUB, font=("Microsoft YaHei UI", 7)
        )

        # ---- 雪花装饰 ----
        self._draw_decorations()

        # ---- 拖拽绑定 ----
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self._drag_x = 0
        self._drag_y = 0

        self.joke_data = None
        self.fetch_joke()
        self.root.mainloop()

    # ---------------- 窗口圆角 ---------------- #

    def _round_window_corners(self, r):
        """用 Windows GDI 将窗口裁剪为圆角矩形"""
        self.root.after(50, lambda: self._apply_round(r))

    def _apply_round(self, r):
        try:
            self.root.update_idletasks()
            # 获取窗口句柄（overrideredirect 窗口用 frame 更可靠）
            hwnd = int(self.root.frame(), 16)
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00080000)
            hrgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, self.W + 1, self.H + 1, r * 2, r * 2)
            ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)
        except Exception:
            pass  # 非 Windows 环境静默跳过

    # ---------------- 绘制 ---------------- #

    def _draw_title_bar(self):
        # 标题栏背景
        draw_round_rect(self.canvas, 6, 6, self.W - 6, 42, 16,
                        fill=COLOR_TITLE)
        self.canvas.create_text(
            20, 24, text="❄ 嘶 好 冷", anchor="w",
            fill="white", font=("Microsoft YaHei UI", 11, "bold")
        )
        # 关闭按钮
        cx, cy = self.W - 18, 24
        draw_round_rect(self.canvas, cx - 12, cy - 10, cx + 12, cy + 10, 8,
                        fill="#8FB8D4")
        self.canvas.create_text(cx, cy, text="✕", fill="white",
                                font=("Microsoft YaHei UI", 11))

    def _draw_button(self):
        bx1, by1 = 100, self.H - 54
        bx2, by2 = self.W - 100, self.H - 24
        self.btn_ids = draw_round_rect(self.canvas, bx1, by1, bx2, by2, 20,
                                        fill=COLOR_BTN)
        self.btn_text = self.canvas.create_text(
            (bx1 + bx2) // 2, (by1 + by2) // 2,
            text="🌸 再来一条", fill="white",
            font=("Microsoft YaHei UI", 12, "bold")
        )
        self.btn_coords = (bx1, by1, bx2, by2)

    def _draw_decorations(self):
        # 四角小雪花装饰
        for xx, yy in [(20, 20), (self.W - 20, 20),
                       (20, self.H - 20), (self.W - 20, self.H - 20)]:
            pass  # 保留装饰位

    # ---------------- 交互 ---------------- #

    def _on_click(self, event):
        cx, cy = event.x, event.y
        # 关闭按钮
        if self.W - 35 < cx < self.W - 5 and 14 < cy < 34:
            self.root.destroy()
            return
        # 按钮区域
        bx1, by1, bx2, by2 = self.btn_coords
        if bx1 <= cx <= bx2 and by1 <= cy <= by2:
            self.fetch_joke()
            return
        # 拖拽
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")

    def _hover_btn(self, enter):
        color = COLOR_BTN_H if enter else COLOR_BTN
        for rid in self.btn_ids:
            self.canvas.itemconfigure(rid, fill=color)

    # ---------------- 数据 ---------------- #

    def fetch_joke(self):
        self.canvas.itemconfigure(self.joke_text, text="")
        self.canvas.itemconfigure(self.cat_text, text="")
        self.canvas.itemconfigure(self.load_text, text="❄")
        self.canvas.tag_raise(self.load_text)
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            req = request.Request(API_URL)
            with request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            self.root.after(0, self._show_joke, data)
        except Exception:
            self.root.after(0, self._show_error)

    def _show_joke(self, data):
        self.joke_data = data
        self.canvas.itemconfigure(self.load_text, text="")
        cat = data.get("category", "未知")
        self.canvas.itemconfigure(self.cat_text, text=f"「{cat}」")
        self.canvas.itemconfigure(self.joke_text,
                                   text=data.get("content", ""))

    def _show_error(self):
        self.canvas.itemconfigure(self.load_text, text="")
        self.canvas.itemconfigure(self.cat_text, text="")
        self.canvas.itemconfigure(self.joke_text,
                                   text="网络开小差了～再试一次吧 ❄")


if __name__ == "__main__":
    SiHaoLengApp()
