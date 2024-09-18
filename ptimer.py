import tkinter as tk
from enum import Enum
import math

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
        self.window.config(padx=20, pady=20, bg="#FFF8E1")  # 背景色を暖かい色に設定

        # 初期状態の設定
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

        self.session_label = tk.Label(self.info_frame, text="セッション: 1/4", fg=ACCENT_COLOR, bg="#FFF8E1", font=LABEL_FONT)
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
            self.time_left = 25 * 60  # 25分
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
            if self.current_session % 4 == 0:
                self.current_phase = Phase.LONG_BREAK
                self.time_left = 15 * 60  # 15分
            else:
                self.current_phase = Phase.SHORT_BREAK
                self.time_left = 5 * 60  # 5分
        else:
            self.current_phase = Phase.WORK
            self.time_left = 25 * 60  # 25分
            self.current_session += 1
        
        self.update_phase_display()
        self.update_timer_display()
        self.state = State.IDLE
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.skip_button.config(state=tk.DISABLED)

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
        self.session_label.config(text=f"セッション: {self.current_session}/4")

    def update_pomodoro_count(self):
        self.pomodoro_label.config(text=f"完了したポモドーロ: {self.pomodoros_completed}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    timer = PomodoroTimer()
    timer.run()

