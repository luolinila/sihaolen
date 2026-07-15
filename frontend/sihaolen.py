"""
嘶好冷 — 冷笑话桌面小窗
可爱圆润风格 · Canvas 绘制圆角 · Windows 圆角窗口 · 白亮冰蓝色系
包含与 Web 版一致的灵动动画效果：雪花飘落、渐入、脉冲、按钮弹性等
"""

import tkinter as tk
import threading
import json
import ctypes
import math
import random
from urllib import request

API_URL = "http://8.134.62.33:8000/api/joke/random"

# ========== 配色（白亮冰蓝系）==========
BG_MAIN      = "#F5F9FC"
BG_CARD      = "#FFFFFF"
COLOR_TEXT   = "#3D4A5C"
COLOR_BTN    = "#8ECAE6"
COLOR_BTN_H  = "#6BB3D9"
COLOR_TITLE  = "#AED4E6"
COLOR_SUB    = "#8FA4B8"
COLOR_BORDER = "#D6E4F0"
COLOR_SHADOW = "#E8F0F8"
COLOR_SNOW   = "#C8DFF0"


# ========== 缓动函数 ==========
def ease_out_cubic(t):
    """ease-out cubic: 开始快，结束慢"""
    return 1 - (1 - t) ** 3

def ease_out_back(t):
    """ease-out back: 带一点回弹"""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out_elastic(t):
    """弹性缓出"""
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * 2 * math.pi / 3) + 1

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1_hex, c2_hex, t):
    """在两个 hex 颜色间插值"""
    r1, g1, b1 = int(c1_hex[1:3], 16), int(c1_hex[3:5], 16), int(c1_hex[5:7], 16)
    r2, g2, b2 = int(c2_hex[1:3], 16), int(c2_hex[3:5], 16), int(c2_hex[5:7], 16)
    r = int(lerp(r1, r2, t))
    g = int(lerp(g1, g2, t))
    b = int(lerp(b1, b2, t))
    return f"#{r:02x}{g:02x}{b:02x}"


# ========== 工具：圆角矩形 ==========
def draw_round_rect(canvas, x1, y1, x2, y2, r, fill, outline="", width=1, tags=()):
    ids = []
    d = 2 * r
    ids.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="", tags=tags))
    ids.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline="", tags=tags))
    ids.append(canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, fill=fill, outline="", tags=tags))
    ids.append(canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, fill=fill, outline="", tags=tags))
    ids.append(canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, fill=fill, outline="", tags=tags))
    ids.append(canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, fill=fill, outline="", tags=tags))
    if outline:
        canvas.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90, style="arc", outline=outline, width=width, tags=tags)
        canvas.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90, style="arc", outline=outline, width=width, tags=tags)
        canvas.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90, style="arc", outline=outline, width=width, tags=tags)
        canvas.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width, tags=tags)
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width, tags=tags)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width, tags=tags)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width, tags=tags)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width, tags=tags)
    return ids


# ========== 雪花类 ==========
class Snowflake:
    """单朵雪花的动画状态"""
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.w = w
        self.h = h
        self.chars = ['❄', '❅', '❆', '✦', '✧', '•']
        self.char = random.choice(self.chars)
        self.size = random.randint(10, 26)
        self.x = random.uniform(0, w)
        self.y = random.uniform(-40, -10)
        self.speed = random.uniform(0.4, 1.6)
        self.drift_amp = random.uniform(0.3, 1.2)
        self.drift_speed = random.uniform(0.01, 0.04)
        self.drift_offset = random.uniform(0, 2 * math.pi)
        self.opacity = random.uniform(0.25, 0.7)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.5, 1.5)
        self.canvas_id = canvas.create_text(
            self.x, self.y, text=self.char,
            font=("Microsoft YaHei UI", self.size),
            fill=COLOR_SNOW, anchor="center"
        )

    def update(self):
        self.y += self.speed
        self.drift_offset += self.drift_speed
        self.x += math.sin(self.drift_offset) * self.drift_amp
        self.rotation += self.rot_speed
        if self.y > self.h + 40:
            self.y = random.uniform(-40, -10)
            self.x = random.uniform(0, self.w)
        self.canvas.coords(self.canvas_id, self.x, self.y)


# ========== 动画管理器 ==========
class AnimationManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.animations = []  # [(fn, duration_ms, start_ms, easing, "name")]
        self.running = False
        self._start_time = None

    def add(self, fn, duration, easing=ease_out_cubic, name=""):
        """添加动画：fn(progress, t) 每帧调用，progress 0~1 (eased)，t 0~1 (raw)"""
        self.animations.append({
            "fn": fn, "duration": duration, "easing": easing, "name": name,
            "start": None
        })
        if not self.running:
            self._start()

    def remove_by_name(self, name):
        self.animations = [a for a in self.animations if a["name"] != name]

    def _start(self):
        self.running = True
        self._start_time = None
        self._tick()

    def _tick(self):
        import time
        now = time.time() * 1000
        if self._start_time is None:
            self._start_time = now
        elapsed = now - self._start_time

        to_remove = []
        for i, anim in enumerate(self.animations):
            if anim["start"] is None:
                anim["start"] = now
            local_t = (now - anim["start"]) / anim["duration"]
            if local_t >= 1.0:
                local_t = 1.0
                to_remove.append(i)
            eased = anim["easing"](local_t)
            try:
                anim["fn"](eased, local_t)
            except Exception:
                pass

        # 从后往前删除
        for i in reversed(to_remove):
            del self.animations[i]

        if self.animations:
            self.canvas.after(16, self._tick)
        else:
            self.running = False


# ========== 主应用 ==========
class SiHaoLengApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("嘶好冷 ❄")
        self.W, self.H = 400, 300
        self.R = 16

        self.root.geometry(f"{self.W}x{self.H}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - self.W) // 2
        y = (hs - self.H) // 2
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self.root.overrideredirect(True)
        self.root.configure(bg="#E8F4FA")

        # 主 Canvas
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg="#E8F4FA", highlightthickness=0)
        self.canvas.pack()

        # 动画管理器
        self.anim = AnimationManager(self.canvas)

        # 窗口圆角
        self._round_window_corners(22)

        # 绘制 UI（先绘制静态部分，动画部分随后启动）
        self._build_ui()

        # 雪花
        self.snowflakes = []
        self._create_snowflakes()

        # 播放入场动画
        self._play_entrance()

        # 雪花动画循环
        self._animate_snow()

        self.joke_data = None
        self.root.mainloop()

    # ========== 窗口圆角 ==========
    def _round_window_corners(self, r):
        self.root.after(50, lambda: self._apply_round(r))

    def _apply_round(self, r):
        try:
            self.root.update_idletasks()
            hwnd = int(self.root.frame(), 16)
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x00080000)
            hrgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, self.W + 1, self.H + 1, r * 2, r * 2)
            ctypes.windll.user32.SetWindowRgn(hwnd, hrgn, True)
        except Exception:
            pass

    # ========== 构建 UI ==========
    def _build_ui(self):
        # 窗口背景
        draw_round_rect(self.canvas, 2, 2, self.W - 2, self.H - 2, 18,
                        fill=BG_MAIN, outline=COLOR_BORDER, width=2, tags=("bg",))

        # ---- 标题栏 ----
        self._build_title_bar()

        # ---- 卡片 ----
        self.card_x1, self.card_y1 = 16, 52
        self.card_x2, self.card_y2 = self.W - 16, self.H - 68
        self.card_ids = draw_round_rect(
            self.canvas, self.card_x1, self.card_y1, self.card_x2, self.card_y2, 14,
            fill=BG_CARD, outline=COLOR_SHADOW, width=2, tags=("card",)
        )
        # 初始隐藏卡片（入场动画用）
        for cid in self.card_ids:
            self.canvas.itemconfigure(cid, state="hidden")

        # ---- 卡片内元素 ----
        self.cat_text = self.canvas.create_text(
            self.W // 2, 74, text="", fill=COLOR_SUB,
            font=("Microsoft YaHei UI", 10),
            state="hidden", tags=("card",)
        )
        self.joke_text = self.canvas.create_text(
            self.W // 2, 138, text="", fill=COLOR_TEXT,
            font=("Microsoft YaHei UI", 12),
            width=330, justify="center",
            state="hidden", tags=("card",)
        )
        self.load_text = self.canvas.create_text(
            self.W // 2, 138, text="❄", fill=COLOR_SUB,
            font=("Microsoft YaHei UI", 28),
            state="hidden", tags=("loader",)
        )

        # ---- 按钮 ----
        self._build_button()

        # ---- 底部文字 ----
        self.footer_text = self.canvas.create_text(
            self.W // 2, self.H - 14, text="— ❄ 嘶好冷 · 每日一冷 —",
            fill=COLOR_SUB, font=("Microsoft YaHei UI", 7),
            state="hidden", tags=("card",)
        )

        # ---- 绑定事件 ----
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.tag_bind("btn", "<Enter>", self._on_btn_enter)
        self.canvas.tag_bind("btn", "<Leave>", self._on_btn_leave)
        self._drag_x = 0
        self._drag_y = 0

        # 按钮 hover 状态
        self.btn_hovered = False

    def _build_title_bar(self):
        draw_round_rect(self.canvas, 6, 6, self.W - 6, 44, 16,
                        fill=COLOR_TITLE, tags=("titlebar",))
        self.canvas.create_text(
            22, 25, text="❄ 嘶 好 冷", anchor="w",
            fill="white", font=("Microsoft YaHei UI", 12, "bold"),
            tags=("titlebar",)
        )
        # 关闭按钮
        cx, cy = self.W - 18, 25
        draw_round_rect(self.canvas, cx - 12, cy - 10, cx + 12, cy + 10, 8,
                        fill="#8FB8D4", tags=("close_btn",))
        self.canvas.create_text(cx, cy, text="✕", fill="white",
                                font=("Microsoft YaHei UI", 11),
                                tags=("close_btn",))

    def _build_button(self):
        bx1, by1 = 100, self.H - 56
        bx2, by2 = self.W - 100, self.H - 24
        self.btn_ids = draw_round_rect(
            self.canvas, bx1, by1, bx2, by2, 20,
            fill=COLOR_BTN, tags=("btn",)
        )
        self.btn_text = self.canvas.create_text(
            (bx1 + bx2) // 2, (by1 + by2) // 2,
            text="🌸 再来一条", fill="white",
            font=("Microsoft YaHei UI", 12, "bold"),
            tags=("btn",)
        )
        self.btn_coords = (bx1, by1, bx2, by2)
        self.btn_bounds = (bx1, by1, bx2, by2)

    # ========== 雪花系统 ==========
    def _create_snowflakes(self):
        for _ in range(16):
            sf = Snowflake(self.canvas, self.W, self.H)
            self.snowflakes.append(sf)

    def _animate_snow(self):
        for sf in self.snowflakes:
            sf.update()
        self.root.after(33, self._animate_snow)  # ~30fps for snow

    # ========== 入场动画 ==========
    def _play_entrance(self):
        """播放卡片从下方渐入的动画"""
        # 保存原始坐标，避免累积偏移
        self._orig_card_coords = {}
        self._orig_cat_pos = self.canvas.coords(self.cat_text)
        self._orig_joke_pos = self.canvas.coords(self.joke_text)
        self._orig_footer_pos = self.canvas.coords(self.footer_text)

        # 先让所有隐藏元素可见
        for cid in self.card_ids:
            self.canvas.itemconfigure(cid, state="normal")
            self._orig_card_coords[cid] = tuple(self.canvas.coords(cid))
        self.canvas.itemconfigure(self.cat_text, state="normal")
        self.canvas.itemconfigure(self.joke_text, state="normal")
        self.canvas.itemconfigure(self.footer_text, state="normal")

        def fade_up(progress, t):
            offset_y = 35 * (1 - progress)
            # 恢复原始位置 + 偏移
            for cid, orig in self._orig_card_coords.items():
                new_coords = []
                for i, v in enumerate(orig):
                    if i % 2 == 1:
                        new_coords.append(v + offset_y)
                    else:
                        new_coords.append(v)
                self.canvas.coords(cid, *new_coords)

            self.canvas.coords(self.cat_text,
                self._orig_cat_pos[0], self._orig_cat_pos[1] + offset_y)
            self.canvas.coords(self.joke_text,
                self._orig_joke_pos[0], self._orig_joke_pos[1] + offset_y)
            self.canvas.coords(self.footer_text,
                self._orig_footer_pos[0], self._orig_footer_pos[1] + offset_y)

            # 模拟透明度：从半透明到不透明
            alpha_color = lerp_color("#E0E8F5", COLOR_SHADOW, progress)
            for cid in self.card_ids:
                self.canvas.itemconfigure(cid, outline=alpha_color)

        self.anim.add(fade_up, 650, easing=ease_out_back, name="entrance")

        # 500ms 后自动加载笑话
        self.root.after(500, self.fetch_joke)

    # ========== 加载动画 ==========
    def _start_loader_pulse(self):
        """启动加载图标的脉冲动画"""
        self.canvas.itemconfigure(self.load_text, state="normal")
        self.canvas.tag_raise(self.load_text)

        # 使用周期性缩放模拟脉冲
        import time

        def pulse_loop():
            if not self._loading:
                return
            now = time.time() * 1000
            elapsed = now - self._pulse_start
            period = 1200  # 一个周期 1.2 秒
            raw = (elapsed % period) / period

            # 脉冲：先胀后缩
            scale = 1.0 + 0.3 * math.sin(raw * 2 * math.pi)
            opacity = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(raw * 2 * math.pi - math.pi / 2))

            self.canvas.itemconfigure(self.load_text, font=("Microsoft YaHei UI", int(28 * scale)))

            # 颜色从浅到深
            c = lerp_color("#B0C8DD", COLOR_BTN, opacity)
            self.canvas.itemconfigure(self.load_text, fill=c)

            self._pulse_id = self.root.after(33, pulse_loop)

        self._pulse_start = time.time() * 1000
        pulse_loop()

    def _stop_loader_pulse(self):
        self._loading = False
        if hasattr(self, '_pulse_id') and self._pulse_id:
            self.root.after_cancel(self._pulse_id)
            self._pulse_id = None
        self.canvas.itemconfigure(self.load_text, state="hidden")

    # ========== 内容切换动画 ==========
    def _crossfade_content(self, category, joke):
        """内容切换弹性缩放效果"""
        self._stop_loader_pulse()

        # 先设置新内容
        self.canvas.itemconfigure(self.joke_text, text=joke, font=("Microsoft YaHei UI", 10))
        if category:
            self.canvas.itemconfigure(self.cat_text, text=f"「{category}」")
        else:
            self.canvas.itemconfigure(self.cat_text, text="")

        # 从缩放弹入
        def scale_in(progress, t):
            fs = int(10 + 2 * progress)
            self.canvas.itemconfigure(self.joke_text, font=("Microsoft YaHei UI", fs))

        def on_complete(progress, t):
            if t >= 1.0:
                self.canvas.itemconfigure(self.joke_text, font=("Microsoft YaHei UI", 12))

        self.anim.remove_by_name("content_transition")
        self.anim.add(scale_in, 300, name="content_transition")
        self.anim.add(on_complete, 300, name="content_transition_final")

    # ========== 按钮交互动画 ==========
    def _on_btn_enter(self, event):
        self.btn_hovered = True
        # 颜色渐变
        def btn_hover_in(progress, t):
            c = lerp_color(COLOR_BTN, COLOR_BTN_H, progress)
            for bid in self.btn_ids:
                self.canvas.itemconfigure(bid, fill=c)
        self.anim.remove_by_name("btn_hover")
        self.anim.add(btn_hover_in, 200, name="btn_hover")

    def _on_btn_leave(self, event):
        self.btn_hovered = False
        def btn_hover_out(progress, t):
            c = lerp_color(COLOR_BTN_H, COLOR_BTN, progress)
            for bid in self.btn_ids:
                self.canvas.itemconfigure(bid, fill=c)
        self.anim.remove_by_name("btn_hover")
        self.anim.add(btn_hover_out, 200, name="btn_hover")

    def _btn_press_anim(self):
        """按钮按下时的缩放弹性效果"""
        bx1, by1, bx2, by2 = self.btn_bounds
        cx, cy = (bx1 + bx2) / 2, (by1 + by2) / 2

        # 对 btn 组做中心缩放（tx, ty 相对于组内坐标偏移）
        def press(progress, t):
            s = 1.0 - 0.08 * ease_out_cubic(t) if t < 0.5 else 0.92 + 0.08 * ((t - 0.5) / 0.5)
            # 用 canvas 的 scale + move 方式不好做，简化：对文字缩放
            fs = int(12 * (0.92 + 0.08 * progress))
            self.canvas.itemconfigure(self.btn_text, font=("Microsoft YaHei UI", fs))

        def on_done(progress, t):
            if t >= 1.0:
                self.canvas.itemconfigure(self.btn_text, font=("Microsoft YaHei UI", 12))

        self.anim.add(press, 250, easing=ease_out_back, name="btn_press")
        self.anim.add(on_done, 250, name="btn_press_done")

    # ========== 交互事件 ==========
    def _on_click(self, event):
        cx, cy = event.x, event.y
        # 关闭按钮
        if self.W - 35 < cx < self.W - 5 and 14 < cy < 36:
            self._close_dialog()
            return
        # 按钮区域
        bx1, by1, bx2, by2 = self.btn_bounds
        if bx1 <= cx <= bx2 and by1 <= cy <= by2:
            self._btn_press_anim()
            self.fetch_joke()
            return
        # 拖拽
        self._drag_x = event.x
        self._drag_y = event.y

    def _close_dialog(self):
        """关闭动画"""
        def shrink(progress, t):
            s = 1.0 - 0.3 * ease_out_cubic(t)
            self.canvas.scale("all", self.W // 2, self.H // 2, s, s)
        self.anim.add(shrink, 200, name="close")
        self.root.after(200, self.root.destroy)

    def _on_drag(self, event):
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        self.root.geometry(f"+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}")

    # ========== 数据请求 ==========
    def fetch_joke(self):
        self._loading = True
        self.canvas.itemconfigure(self.joke_text, text="")
        self.canvas.itemconfigure(self.cat_text, text="")
        self._start_loader_pulse()
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
        cat = data.get("category", "")
        content = data.get("content", "暂无冷笑话")
        self._crossfade_content(cat, content)

    def _show_error(self):
        self._stop_loader_pulse()
        self.canvas.itemconfigure(self.cat_text, text="")
        self.canvas.itemconfigure(self.joke_text,
                                   text="网络开小差了～\n再试一次吧 ❄",
                                   font=("Microsoft YaHei UI", 12))


if __name__ == "__main__":
    SiHaoLengApp()
