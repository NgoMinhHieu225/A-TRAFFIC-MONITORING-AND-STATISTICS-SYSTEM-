import os
import json
import cv2
import pandas as pd
import numpy as np
import time
from datetime import datetime
import tkinter.messagebox as msgbox
import customtkinter as ctk
from PIL import Image
from ultralytics import YOLO

# --- THƯ VIỆN BIỂU ĐỒ ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CẤU HÌNH HỆ THỐNG ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ADMIN_USER = "admin"
ADMIN_PASS = "1"
CONFIG_FILE = "config_vach.json"
VIDEO_PATH = "22.mp4"
CONGESTION_THRESHOLD = 15  # Ngưỡng cảnh báo ùn tắc (Dễ dàng thay đổi)


# ==========================================
# 1. MÀN HÌNH ĐĂNG NHẬP
# ==========================================
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập Hệ thống ITS")
        self.geometry("400x500")
        self.resizable(False, False)
        self.login_success = False

        self.login_frame = ctk.CTkFrame(self, corner_radius=20)
        self.login_frame.pack(pady=40, padx=40, fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="ITS MONITOR", font=("Roboto", 24, "bold")).pack(pady=30)
        self.entry_user = ctk.CTkEntry(self.login_frame, placeholder_text="Tên đăng nhập", width=250)
        self.entry_user.pack(pady=10)
        self.entry_user.insert(0, ADMIN_USER)
        self.entry_pass = ctk.CTkEntry(self.login_frame, placeholder_text="Mật khẩu", show="*", width=250)
        self.entry_pass.pack(pady=10)
        self.entry_pass.insert(0, ADMIN_PASS)
        ctk.CTkButton(self.login_frame, text="ĐĂNG NHẬP", command=self.handle_login).pack(pady=30)

    def handle_login(self):
        if self.entry_user.get() == ADMIN_USER and self.entry_pass.get() == ADMIN_PASS:
            self.login_success = True
            self.destroy()
        else:
            msgbox.showerror("Lỗi", "Sai thông tin đăng nhập!")


# ==========================================
# 2. MÀN HÌNH CHÍNH
# ==========================================
class TrafficApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Giám sát Giao thông Thông minh (ITS Dashboard)")
        self.geometry("1400x950")
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.proc_w, self.proc_h = 540, 960
        self.is_running = True
        self.drawing = False
        self.stats = {
            'up': {'car': 0, 'motorbike': 0, 'bicycle': 0, 'bus': 0},
            'down': {'car': 0, 'motorbike': 0, 'bicycle': 0, 'bus': 0}
        }
        self.counted_ids = set()  # Dùng set để tra cứu nhanh hơn
        self.track_history = {}
        self.limits = self.load_config()
        self.temp_limits = self.limits.copy()

        if not os.path.exists("snapshots"): os.makedirs("snapshots")

        try:
            self.model = YOLO('best.pt')
        except:
            msgbox.showerror("Lỗi", "Không tìm thấy best.pt");
            self.destroy();
            return

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self, width=320, corner_radius=0, fg_color="#2b2b2b",
                                              label_text="BẢNG ĐIỀU KHIỂN")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_clock = ctk.CTkLabel(self.sidebar, text="", font=("Consolas", 20, "bold"), text_color="#00E5FF")
        self.lbl_clock.pack(pady=15)

        self.card_widgets = {}
        for v_type, v_name in [('car', 'Ô TÔ'), ('motorbike', 'XE MÁY'), ('bus', 'XE BUÝT'), ('bicycle', 'XE ĐẠP')]:
            self.create_stat_card(v_type, v_name)

        self.fig, self.ax = plt.subplots(figsize=(3, 2), dpi=80)
        self.fig.patch.set_facecolor("#2b2b2b")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.sidebar)
        self.canvas.get_tk_widget().pack(pady=10)

        ctk.CTkButton(self.sidebar, text="📸 CHỤP ẢNH", command=self.manual_snapshot).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.sidebar, text="💾 XUẤT EXCEL", fg_color="#4CAF50", command=self.save_excel).pack(fill="x",
                                                                                                           padx=20,
                                                                                                           pady=5)
        ctk.CTkButton(self.sidebar, text="🚪 THOÁT", fg_color="#D32F2F", command=self.quit_app).pack(fill="x", padx=20,
                                                                                                    pady=20)

        self.video_container = ctk.CTkFrame(self, fg_color="black")
        self.video_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_container, text="")
        self.video_label.pack(expand=True, fill="both")

        self.video_label.bind("<Button-1>", self.start_draw)
        self.video_label.bind("<B1-Motion>", self.drag_draw)
        self.video_label.bind("<ButtonRelease-1>", self.end_draw)

        self.cap = cv2.VideoCapture(VIDEO_PATH)
        self.update_clock()
        self.after(500, self.update_frame)

    def update_clock(self):
        if self.is_running:
            self.lbl_clock.configure(text=datetime.now().strftime("%H:%M:%S\n%d/%m/%Y"))
            self.after(1000, self.update_clock)

    def create_stat_card(self, v_type, v_name):
        card = ctk.CTkFrame(self.sidebar, fg_color="#3d3d3d", corner_radius=10)
        card.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(card, text=v_name, font=("Arial", 12, "bold")).pack(pady=2)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=5)
        l_up = ctk.CTkLabel(inner, text="0", font=("Arial", 16, "bold"), text_color="#4CAF50")
        l_up.pack(side="left", expand=True)
        l_down = ctk.CTkLabel(inner, text="0", font=("Arial", 16, "bold"), text_color="#FF9800")
        l_down.pack(side="right", expand=True)
        self.card_widgets[v_type] = {'up': l_up, 'down': l_down}

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: return json.load(f)["limits"]
        return [50, 800, 500, 800]  # Vị trí mặc định thấp hơn và dài hơn

    def map_coords(self, ex, ey):
        w_lbl = self.video_label.winfo_width()
        h_lbl = self.video_label.winfo_height()
        if w_lbl <= 1: return ex, ey
        return int(ex * (self.proc_w / w_lbl)), int(ey * (self.proc_h / h_lbl))

    def start_draw(self, event):
        self.drawing = True
        x, y = self.map_coords(event.x, event.y)
        self.temp_limits = [x, y, x, y]

    def drag_draw(self, event):
        if self.drawing:
            x, y = self.map_coords(event.x, event.y)
            self.temp_limits[2], self.temp_limits[3] = x, y

    def end_draw(self, event):
        self.drawing = False
        self.limits = self.temp_limits.copy()
        with open(CONFIG_FILE, "w") as f: json.dump({"limits": self.limits}, f)

    def update_frame(self):
        if not self.is_running: return
        success, frame = self.cap.read()
        if not success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.after(10, self.update_frame);
            return

        frame = cv2.resize(frame, (self.proc_w, self.proc_h))
        self.current_frame = frame.copy()
        results = self.model.track(frame, persist=True, verbose=False, conf=0.3)

        # --- HIỂN THỊ VẠCH CẤU HÌNH (MỚI) ---
        lc = self.temp_limits if self.drawing else self.limits
        line_mid_y = (lc[1] + lc[3]) // 2

        # Vẽ vùng đệm (vàng nhạt) để người dùng biết phạm vi đếm
        overlay = frame.copy()
        cv2.line(overlay, (lc[0], lc[1]), (lc[2], lc[3]), (0, 255, 255), 25)
        frame = cv2.addWeighted(overlay, 0.2, frame, 0.8, 0)

        # Vẽ vạch chính (Đỏ) và điểm neo (Xanh)
        cv2.line(frame, (lc[0], lc[1]), (lc[2], lc[3]), (0, 0, 255), 4)
        cv2.circle(frame, (lc[0], lc[1]), 6, (0, 255, 0), -1)
        cv2.circle(frame, (lc[2], lc[3]), 6, (0, 255, 0), -1)

        # --- LOGIC NHẬN DIỆN & ĐẾM ---
        vehicle_count = 0
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            vehicle_count = len(ids)

            for box, id_obj, cls in zip(boxes, ids, clss):
                x1, y1, x2, y2 = box
                cy = (y1 + y2) // 2  # Tọa độ tâm y
                cx = (x1 + x2) // 2  # Tọa độ tâm x
                name = {0: 'bicycle', 1: 'bus', 2: 'car', 3: 'motorbike'}.get(cls, "object")

                # Lưu lịch sử di chuyển
                if id_obj not in self.track_history: self.track_history[id_obj] = []
                self.track_history[id_obj].append(cy)

                # KIỂM TRA ĐIỀU KIỆN ĐẾM (Tối ưu cho xe máy)
                # 1. Xe phải nằm trong phạm vi chiều ngang của vạch (x-range)
                if min(lc[0], lc[2]) <= cx <= max(lc[0], lc[2]):
                    # 2. Xe đi qua vùng nhạy cảm của vạch (30px)
                    if abs(cy - line_mid_y) < 30 and id_obj not in self.counted_ids:
                        if len(self.track_history[id_obj]) > 1:
                            direction = "down" if cy > self.track_history[id_obj][0] else "up"
                            if name in self.stats[direction]:
                                self.stats[direction][name] += 1
                                self.counted_ids.add(id_obj)
                                self.update_ui_stats()

                # Vẽ khung xe
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID:{id_obj} {name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Cảnh báo ùn tắc (Sử dụng ngưỡng cấu hình)
        if vehicle_count > CONGESTION_THRESHOLD:
            overlay_msg = frame.copy()
            cv2.rectangle(overlay_msg, (0, 0), (self.proc_w, 80), (0, 0, 200), -1)
            frame = cv2.addWeighted(overlay_msg, 0.5, frame, 0.5, 0)
            cv2.putText(frame, f"WARNING: CONGESTION ({vehicle_count})", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Render video lên UI
        h_gui = self.video_container.winfo_height()
        if h_gui > 10:
            w_show = int(h_gui * (self.proc_w / self.proc_h))
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(w_show, h_gui))
            self.video_label.configure(image=img_tk)

        self.after(10, self.update_frame)

    def update_ui_stats(self):
        for v in self.card_widgets:
            self.card_widgets[v]['up'].configure(text=str(self.stats['up'][v]))
            self.card_widgets[v]['down'].configure(text=str(self.stats['down'][v]))

        self.ax.clear()
        labels = ['Car', 'Moto', 'Bus', 'Bike']
        up = [self.stats['up'][k] for k in ['car', 'motorbike', 'bus', 'bicycle']]
        down = [self.stats['down'][k] for k in ['car', 'motorbike', 'bus', 'bicycle']]
        x = np.arange(len(labels))
        self.ax.bar(x - 0.2, up, 0.4, color="#4CAF50", label='Up')
        self.ax.bar(x + 0.2, down, 0.4, color="#FF9800", label='Down')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, color='white', fontsize=8)
        self.ax.tick_params(axis='y', colors='white')
        self.canvas.draw()

    def manual_snapshot(self):
        if hasattr(self, 'current_frame'):
            path = f"snapshots/snap_{int(time.time())}.jpg"
            cv2.imwrite(path, self.current_frame)
            msgbox.showinfo("Thành công", f"Đã lưu ảnh tại: {path}")

    def save_excel(self):
        data = []
        for d in self.stats:
            for k, v in self.stats[d].items():
                data.append({"Thời điểm": datetime.now().strftime("%H:%M:%S"), "Hướng": d, "Loại xe": k, "Số lượng": v})
        df = pd.DataFrame(data)
        df.to_excel("Bao_Cao_Giao_Thong.xlsx", index=False)
        msgbox.showinfo("Thành công", "Đã xuất file Bao_Cao_Giao_Thong.xlsx")

    def quit_app(self):
        self.is_running = False
        if hasattr(self, 'cap') and self.cap.isOpened(): self.cap.release()
        self.destroy()


if __name__ == "__main__":
    app = None
    try:
        login = LoginWindow()
        login.mainloop()
        if login.login_success:
            app = TrafficApp()
            app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        if app: app.quit_app()