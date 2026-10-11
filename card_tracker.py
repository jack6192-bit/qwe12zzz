# -*- coding: utf-8 -*-
"""
카드게임 선공/후공 기록 프로그램
- 선공/후공 횟수 기록, 실수 시 -1
- 오늘 총 대전 수 및 선공/후공 비율 표시
- 날짜별 기록 누적 (JSON 파일 저장 -> 종료 후에도 유지)
실행: python card_tracker.py
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

# 저장 파일 위치 (스크립트와 같은 폴터)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card_records.json")


def load_records():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_records(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


class CardTrackerApp:
    BG = "#1e1e2e"
    PANEL = "#2a2a3c"
    FG = "#e6e6f0"
    FIRST_COLOR = "#4fc3f7"
    SECOND_COLOR = "#ffb74d"

    def __init__(self, root):
        self.root = root
        self.root.title("카드게임 선공/후공 기록")
        self.root.geometry("480x640")
        self.root.configure(bg=self.BG)

        self.records = load_records()
        self.today = date.today().isoformat()
        self._ensure_today()

        self._build_ui()
        self.refresh()

    # ---------- 데이터 ----------
    def _ensure_today(self):
        if self.today not in self.records:
            self.records[self.today] = {"first": 0, "second": 0}

    def change(self, key, delta):
        rec = self.records[self.today]
        new_val = max(0, rec[key] + delta)  # 음수 방지
        if new_val == rec[key] and delta < 0:
            return  # 이미 0
        rec[key] = new_val
        save_records(self.records)
        self.refresh()

    def delete_selected_date(self):
        sel = self.history_list.selection()
        if not sel:
            messagebox.showinfo("알림", "삭제할 날짜를 선택하세요.")
            return
        target = self.history_list.item(sel[0], "values")[0]
        if messagebox.askyesno("확인", f"{target} 기록을 삭제할까요?"):
            del self.records[target]
            save_records(self.records)
            self.refresh()

    # ---------- UI ----------
    def _build_ui(self):
        # 오늘 날짜 표시
        tk.Label(self.root, text=f"오늘: {self.today}", bg=self.BG, fg=self.FG,
                 font=("맑은 고딕", 12, "bold")).pack(pady=(10, 4))

        # 카운터 패널
        counter_frame = tk.Frame(self.root, bg=self.PANEL, bd=2, relief="ridge")
        counter_frame.pack(fill="x", padx=16, pady=6)

        # 선공
        f_frame = tk.Frame(counter_frame, bg=self.PANEL)
        f_frame.pack(side="left", expand=True, padx=10, pady=12)
        tk.Label(f_frame, text="선공", bg=self.PANEL, fg=self.FIRST_COLOR,
                 font=("맑은 고딕", 14, "bold")).pack()
        self.first_label = tk.Label(f_frame, text="0", bg=self.PANEL, fg=self.FG,
                                    font=("맑은 고딕", 28, "bold"))
        self.first_label.pack()
        btns_f = tk.Frame(f_frame, bg=self.PANEL)
        btns_f.pack()
        tk.Button(btns_f, text="+1", width=5, font=("맑은 고딕", 11, "bold"),
                  bg=self.FIRST_COLOR, command=lambda: self.change("first", 1)).pack(side="left", padx=3)
        tk.Button(btns_f, text="-1", width=5, font=("맑은 고딕", 11),
                  bg="#555566", fg="white", command=lambda: self.change("first", -1)).pack(side="left", padx=3)

        # 후공
        s_frame = tk.Frame(counter_frame, bg=self.PANEL)
        s_frame.pack(side="right", expand=True, padx=10, pady=12)
        tk.Label(s_frame, text="후공", bg=self.PANEL, fg=self.SECOND_COLOR,
                 font=("맑은 고딕", 14, "bold")).pack()
        self.second_label = tk.Label(s_frame, text="0", bg=self.PANEL, fg=self.FG,
                                     font=("맑은 고딕", 28, "bold"))
        self.second_label.pack()
        btns_s = tk.Frame(s_frame, bg=self.PANEL)
        btns_s.pack()
        tk.Button(btns_s, text="+1", width=5, font=("맑은 고딕", 11, "bold"),
                  bg=self.SECOND_COLOR, command=lambda: self.change("second", 1)).pack(side="left", padx=3)
        tk.Button(btns_s, text="-1", width=5, font=("맑은 고딕", 11),
                  bg="#555566", fg="white", command=lambda: self.change("second", -1)).pack(side="left", padx=3)

        # 요약 패널
        self.summary_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.summary_var, bg=self.BG, fg=self.FG,
                 font=("맑은 고딕", 12), justify="center").pack(pady=6)

        # 비율 바
        self.ratio_canvas = tk.Canvas(self.root, height=26, bg=self.BG, highlightthickness=0)
        self.ratio_canvas.pack(fill="x", padx=16, pady=(0, 6))

        # 날짜별 기록
        hist_frame = tk.Frame(self.root, bg=self.BG)
        hist_frame.pack(fill="both", expand=True, padx=16, pady=6)

        tk.Label(hist_frame, text="날짜별 기록", bg=self.BG, fg=self.FG,
                 font=("맑은 고딕", 11, "bold")).pack(anchor="w")

        cols = ("date", "first", "second", "total", "ratio")
        self.history_list = ttk.Treeview(hist_frame, columns=cols, show="headings", height=10)
        for c, t, w in zip(cols, ("날짜", "선공", "후공", "총 대전", "선공 비율"), (120, 60, 60, 80, 100)):
            self.history_list.heading(c, text=t)
            self.history_list.column(c, width=w, anchor="center")
        self.history_list.pack(fill="both", expand=True)

        tk.Button(hist_frame, text="선택한 날짜 기록 삭제", bg="#c62828", fg="white",
                  font=("맑은 고딕", 10), command=self.delete_selected_date).pack(pady=6)

    # ---------- 갱신 ----------
    def refresh(self):
        rec = self.records[self.today]
        first, second = rec["first"], rec["second"]
        total = first + second

        self.first_label.config(text=str(first))
        self.second_label.config(text=str(second))

        if total > 0:
            f_pct = first / total * 100
            s_pct = second / total * 100
            self.summary_var.set(
                f"오늘 총 대전: {total}판  |  선공 {f_pct:.1f}% ({first}판)  ·  후공 {s_pct:.1f}% ({second}판)"
            )
        else:
            self.summary_var.set("오늘 총 대전: 0판  |  아직 기록이 없습니다")

        # 비율 바 그리기
        self.ratio_canvas.delete("all")
        w = self.ratio_canvas.winfo_width() or 448
        if total > 0:
            fw = w * first / total
            self.ratio_canvas.create_rectangle(0, 0, fw, 26, fill=self.FIRST_COLOR, outline="")
            self.ratio_canvas.create_rectangle(fw, 0, w, 26, fill=self.SECOND_COLOR, outline="")
        else:
            self.ratio_canvas.create_rectangle(0, 0, w, 26, fill="#444455", outline="")

        # 히스토리 갱신
        self.history_list.delete(*self.history_list.get_children())
        for d in sorted(self.records.keys(), reverse=True):
            r = self.records[d]
            t = r["first"] + r["second"]
            ratio = f"{r['first'] / t * 100:.1f}%" if t > 0 else "-"
            self.history_list.insert("", "end", values=(d, r["first"], r["second"], t, ratio))


if __name__ == "__main__":
    root = tk.Tk()
    app = CardTrackerApp(root)
    root.mainloop()
