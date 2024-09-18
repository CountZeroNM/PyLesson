import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum

class Time:
    SECONDS = 1
    MINUTES = 60 * SECONDS

class Phase(Enum):
    WORK = 1
    SHORT_BREAK = 2
    LONG_BREAK = 3

class State(Enum):
    IDLE = 1
    RUNNING = 2
    PAUSED = 3

class PomodoroTimer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ポモドーロタイマー")
        self.window.config(padx=20, pady=20, bg="#FFF8E1")

        self.settings = {
            "work_time": 25,
            "short_break_time": 5,
            "long_break_time": 15,
            "phases_in_session": 4
        }

        self.current_phase = Phase.WORK
        self.state = State.IDLE
        self.time_left = 0
        self.pomodoros_completed = 0
        self.current_session = 1
        self.timer = None

        self.setup_ui()
        self.reset_timer()

    def setup_ui(self):
                # フォントとカラーの設定
        TITLE_FONT = ("Helvetica", 28, "bold")
        TIMER_FONT = ("Helvetica", 64, "bold")
        LABEL_FONT = ("Helvetica", 18)
        BUTTON_FONT = ("Helvetica", 14, "bold")

        MAIN_COLOR = "#FF5722"  # オレンジ
        SECONDARY_COLOR = "#4CAF50"  # グリーン
        ACCENT_COLOR = "#2196F3"  # ブルー

        # タイトル
        self.title_label = tk.Label(text="ポモドーロタイマー", fg=MAIN_COLOR, bg="#FFF8E1", font=TITLE_FONT)
        self.title_label.grid(column=0, row=0, columnspan=4, pady=(0, 20))

        # タイマー表示
        self.timer_frame = tk.Frame(self.window, bg="#FFE0B2", bd=2, relief="raised")
        self.timer_frame.grid(column=0, row=1, columnspan=4, pady=20, padx=20, sticky="nsew")

        self.timer_label = tk.Label(self.timer_frame, text="25:00", fg=MAIN_COLOR, bg="#FFE0B2", font=TIMER_FONT)
        self.timer_label.pack(pady=20)

        # フェーズと進捗表示
        self.info_frame = tk.Frame(self.window, bg="#FFF8E1")
        self.info_frame.grid(column=0, row=2, columnspan=4, pady=10)

        self.phase_label = tk.Label(self.info_frame, text="作業", fg=SECONDARY_COLOR, bg="#FFF8E1", font=LABEL_FONT)
        self.phase_label.pack(side="left", padx=10)

        self.session_label = tk.Label(self.info_frame, text=f"セッション: 1/{self.settings['phases_in_session']}", fg=ACCENT_COLOR, bg="#FFF8E1", font=LABEL_FONT)
        self.session_label.pack(side="left", padx=10)

        # ボタン
        self.button_frame = tk.Frame(self.window, bg="#FFF8E1")
        self.button_frame.grid(column=0, row=3, columnspan=4, pady=20)

        button_width = 10
        button_height = 2

        self.start_button = tk.Button(self.button_frame, text="開始", command=self.start_timer, 
                                                      bg=SECONDARY_COLOR, fg="white", font=BUTTON_FONT, 
                                                                                            width=button_width, height=button_height)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = tk.Button(self.button_frame, text="一時停止", command=self.pause_timer, 
                                                      bg=MAIN_COLOR, fg="white", font=BUTTON_FONT, 
                                                                                            width=button_width, height=button_height, state=tk.DISABLED)
        self.pause_button.pack(side="left", padx=5)

        self.resume_button = tk.Button(self.button_frame, text="再開", command=self.resume_timer, 
                                                       bg=ACCENT_COLOR, fg="white", font=BUTTON_FONT, 
                                                                                              width=button_width, height=button_height, state=tk.DISABLED)
        self.resume_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.button_frame, text="リセット", command=self.reset_timer, 
                                                      bg="#607D8B", fg="white", font=BUTTON_FONT, 
                                                                                            width=button_width, height=button_height)
        self.reset_button.pack(side="left", padx=5)

        # スキップボタン
        self.skip_button = tk.Button(self.window, text="スキップ", command=self.skip_phase, 
                                                     bg="#9C27B0", fg="white", font=BUTTON_FONT, 
                                                                                          width=button_width, height=1, state=tk.DISABLED)
        self.skip_button.grid(column=0, row=4, columnspan=4, pady=10)

        # 完了したポモドーロ数
        self.pomodoro_label = tk.Label(text="完了したポモドーロ: 0", fg=MAIN_COLOR, bg="#FFF8E1", font=LABEL_FONT)
        self.pomodoro_label.grid(column=0, row=5, columnspan=4, pady=10)

        # 設定ボタン
        self.settings_button = tk.Button(self.window, text="設定", command=self.open_settings,
                                                         bg="#607D8B", fg="white", font=BUTTON_FONT,
                                                                                                  width=button_width, height=1)
        self.settings_button.grid(column=0, row=6, columnspan=4, pady=10)

    def open_settings(self):
        settings_window = tk.Toplevel(self.window)
        settings_window.title("タイマー設定")
        settings_window.config(padx=20, pady=20, bg="#FFF8E1")
        
        # メイン画面をモーダルにする
        settings_window.grab_set()
        settings_window.transient(self.window)
        settings_window.focus_set()

        ttk.Label(settings_window, text="作業時間 (分):").grid(column=0, row=0, padx=5, pady=5, sticky="e")
        work_time = ttk.Entry(settings_window)
        work_time.insert(0, str(self.settings["work_time"]))
        work_time.grid(column=1, row=0, padx=5, pady=5)

        ttk.Label(settings_window, text="短い休憩時間 (分):").grid(column=0, row=1, padx=5, pady=5, sticky="e")
        short_break = ttk.Entry(settings_window)
        short_break.insert(0, str(self.settings["short_break_time"]))
        short_break.grid(column=1, row=1, padx=5, pady=5)

        ttk.Label(settings_window, text="長い休憩時間 (分):").grid(column=0, row=2, padx=5, pady=5, sticky="e")
        long_break = ttk.Entry(settings_window)
        long_break.insert(0, str(self.settings["long_break_time"]))
        long_break.grid(column=1, row=2, padx=5, pady=5)

        ttk.Label(settings_window, text="セッション内のフェーズ数:").grid(column=0, row=3, padx=5, pady=5, sticky="e")
        phases = ttk.Entry(settings_window)
        phases.insert(0, str(self.settings["phases_in_session"]))
        phases.grid(column=1, row=3, padx=5, pady=5)

        def save_settings():
            try:
                self.settings["work_time"] = int(work_time.get())
                self.settings["short_break_time"] = int(short_break.get())
                self.settings["long_break_time"] = int(long_break.get())
                self.settings["phases_in_session"] = int(phases.get())
                self.reset_timer()
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("エラー", "すべての値は整数である必要があります。")

        save_button = ttk.Button(settings_window, text="保存", command=save_settings)
        save_button.grid(column=0, row=4, columnspan=2, pady=10)

        # ウィンドウが閉じられたときに、grab_release を呼び出す
        settings_window.protocol("WM_DELETE_WINDOW", lambda: [settings_window.grab_release(), settings_window.destroy()])

    def start_timer(self):
        if self.state == State.IDLE:
            self.state = State.RUNNING
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.skip_button.config(state=tk.NORMAL)
            self.countdown()

    def pause_timer(self):
            if self.state == State.RUNNING:
                self.state = State.PAUSED
                self.pause_button.config(state=tk.DISABLED)
                self.resume_button.config(state=tk.NORMAL)
                if self.timer is not None:
                    self.window.after_cancel(self.timer)
                    self.timer = None

    def resume_timer(self):
        if self.state == State.PAUSED:
            self.state = State.RUNNING
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.countdown()

    def reset_timer(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
            self.timer = None
            self.state = State.IDLE
            self.current_phase = Phase.WORK
            self.time_left = self.settings["work_time"] * Time.MINUTES
            self.current_session = 1
            self.update_timer_display()
            self.update_phase_display()
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.skip_button.config(state=tk.DISABLED)

    def skip_phase(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
            self.timer = None
            self.next_phase()

    def countdown(self):
        if self.state == State.RUNNING:
            if self.time_left > 0:
                self.time_left -= 1
                self.update_timer_display()
                self.timer = self.window.after(1000, self.countdown)
            else:
                self.next_phase()

    def next_phase(self):
        if self.current_phase == Phase.WORK:
            self.pomodoros_completed += 1
            self.update_pomodoro_count()
            self.current_session += 1
            
            if self.current_session > self.settings["phases_in_session"]:
            # すべてのセッションが終了した場合
                self.current_session = 1
                self.current_phase = Phase.LONG_BREAK
                self.time_left = self.settings["long_break_time"] * Time.MINUTES
            elif self.current_session == self.settings["phases_in_session"]:
            # 最後のセッションの場合
                self.current_phase = Phase.SHORT_BREAK
                self.time_left = self.settings["short_break_time"] * Time.MINUTES
            else:
            # 通常のセッションの場合
                self.current_phase = Phase.SHORT_BREAK
                self.time_left = self.settings["short_break_time"] * Time.MINUTES
        else:
            # 休憩フェーズが終了した場合
            self.current_phase = Phase.WORK
            self.time_left = self.settings["work_time"] * Time.MINUTES

        self.update_phase_display()
        self.update_timer_display()
        self.state = State.IDLE
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.DISABLED)

    def update_phase_display(self):
        if self.current_phase == Phase.WORK:
            self.phase_label.config(text="作業", fg="#4CAF50")
        elif self.current_phase == Phase.SHORT_BREAK:
            self.phase_label.config(text="短い休憩", fg="#2196F3")
        else:
            self.phase_label.config(text="長い休憩", fg="#F44336")
        self.session_label.config(text=f"セッション: {self.current_session}/{self.settings['phases_in_session']}")

    def update_timer_display(self):
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def update_phase_display(self):
        if self.current_phase == Phase.WORK:
            self.phase_label.config(text="作業", fg="#4CAF50")
        elif self.current_phase == Phase.SHORT_BREAK:
            self.phase_label.config(text="短い休憩", fg="#2196F3")
        else:
            self.phase_label.config(text="長い休憩", fg="#F44336")
        current_session_display = min(self.current_session, self.settings['phases_in_session'])  # セッション表示の上限を設定
        self.session_label.config(text=f"セッション: {current_session_display}/{self.settings['phases_in_session']}")

    def update_pomodoro_count(self):
        self.pomodoro_label.config(text=f"完了したポモドーロ: {self.pomodoros_completed}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    timer = PomodoroTimer()
    timer.run()
