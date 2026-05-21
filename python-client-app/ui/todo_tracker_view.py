import calendar
import datetime
import threading
import tkinter as tk
import requests
import customtkinter as ctk
from core.api_client import ApiClient
from ui.theme import COLORS, FONTS, SPACING

TASK_COLUMN_WIDTH = 200
DATE_COLUMN_WIDTH = 36
DATE_ROW_HEIGHT = 36
SCROLLBAR_GUTTER = 18


class TodoTrackerView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        self.api = ApiClient()

        self.today = datetime.date.today()
        self.dates = self._build_last_three_months()
        self.tasks = {}
        self.current_row = 0
        self._today_col = self.dates.index(self.today) if self.today in self.dates else -1

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=SPACING["page_padx"], pady=(SPACING["page_pady"], 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Habit Tracker",
            font=ctk.CTkFont(family=FONTS["title"][0], size=FONTS["title"][1], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w")

        self.range_label = ctk.CTkLabel(
            header,
            text=self._range_label_text(),
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        )
        self.range_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        toolbar = ctk.CTkFrame(
            self,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        toolbar.grid(row=1, column=0, padx=SPACING["page_padx"], pady=(8, 12), sticky="ew")

        self.task_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Add a new daily habit…",
            height=40,
            border_color=COLORS["border"],
            fg_color=COLORS["bg"],
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(16, 10), pady=14)

        self.btn_add_task = ctk.CTkButton(
            toolbar,
            text="Add Habit",
            width=120,
            height=40,
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.add_task,
        )
        self.btn_add_task.pack(side="left", padx=(0, 16), pady=14)
        self.task_entry.bind("<Return>", lambda _: self.add_task())

        spreadsheet_card = ctk.CTkFrame(
            self,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        spreadsheet_card.grid(row=2, column=0, padx=SPACING["page_padx"], pady=(0, SPACING["page_pady"]), sticky="nsew")
        spreadsheet_card.grid_rowconfigure(1, weight=1)
        spreadsheet_card.grid_columnconfigure(1, weight=1)

        task_header_cell = ctk.CTkFrame(
            spreadsheet_card,
            width=TASK_COLUMN_WIDTH,
            height=DATE_ROW_HEIGHT,
            corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=1,
            border_color=COLORS["border"],
        )
        task_header_cell.grid(row=0, column=0, sticky="nsew")
        task_header_cell.grid_propagate(False)
        ctk.CTkLabel(
            task_header_cell,
            text="Habit",
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            text_color=COLORS["text"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        dates_area = ctk.CTkFrame(spreadsheet_card, fg_color="transparent")
        dates_area.grid(row=0, column=1, rowspan=2, sticky="nsew")
        dates_area.grid_rowconfigure(1, weight=1)
        dates_area.grid_rowconfigure(2, minsize=SCROLLBAR_GUTTER, weight=0)
        dates_area.grid_columnconfigure(0, weight=1)
        dates_area.grid_columnconfigure(1, minsize=SCROLLBAR_GUTTER, weight=0)
        self.dates_area = dates_area

        header_container = ctk.CTkFrame(
            dates_area,
            height=DATE_ROW_HEIGHT,
            fg_color=COLORS["sidebar"],
            corner_radius=0,
        )
        header_container.grid(row=0, column=0, sticky="nsew")
        header_container.grid_propagate(False)

        self.header_canvas = tk.Canvas(
            header_container,
            height=DATE_ROW_HEIGHT,
            highlightthickness=0,
            bg=COLORS["sidebar"],
            borderwidth=0,
        )
        self.header_canvas.pack(fill="both", expand=True)

        self.header_gutter = ctk.CTkFrame(
            dates_area,
            width=SCROLLBAR_GUTTER,
            height=DATE_ROW_HEIGHT,
            fg_color=COLORS["sidebar"],
            corner_radius=0,
        )
        self.header_gutter.grid(row=0, column=1, sticky="ns")
        self.header_gutter.grid_propagate(False)

        self.body_canvas = tk.Canvas(
            dates_area,
            highlightthickness=0,
            bg=COLORS["bg"],
            borderwidth=0,
        )
        self.body_canvas.grid(row=1, column=0, sticky="nsew")
        self.body_canvas.bind("<Button-1>", self._on_grid_click)

        self.body_v_scroll = ctk.CTkScrollbar(
            dates_area,
            width=SCROLLBAR_GUTTER,
            orientation="vertical",
            command=self._on_body_yscroll,
            button_color=COLORS["border"],
            button_hover_color=COLORS["text_dim"],
        )
        self.body_v_scroll.grid(row=1, column=1, sticky="ns")

        self.body_h_scroll = ctk.CTkScrollbar(
            dates_area,
            orientation="horizontal",
            command=self._on_body_xscroll,
            button_color=COLORS["border"],
            button_hover_color=COLORS["text_dim"],
        )
        self.body_h_scroll.grid(row=2, column=0, sticky="ew")

        self.scroll_corner = ctk.CTkFrame(
            dates_area,
            width=SCROLLBAR_GUTTER,
            height=SCROLLBAR_GUTTER,
            fg_color=COLORS["bg"],
            corner_radius=0,
        )
        self.scroll_corner.grid(row=2, column=1, sticky="nsew")
        self.scroll_corner.grid_propagate(False)

        self.body_canvas.configure(
            xscrollcommand=self._on_body_xscroll_set,
            yscrollcommand=self._on_body_yscroll_set,
        )

        task_column_wrap = ctk.CTkFrame(
            spreadsheet_card,
            width=TASK_COLUMN_WIDTH,
            fg_color=COLORS["bg"],
            corner_radius=0,
        )
        task_column_wrap.grid(row=1, column=0, sticky="nsew")
        task_column_wrap.grid_propagate(False)

        self.tasks_canvas = tk.Canvas(
            task_column_wrap,
            width=TASK_COLUMN_WIDTH,
            highlightthickness=0,
            bg=COLORS["bg"],
            borderwidth=0,
        )
        self.tasks_canvas.pack(fill="both", expand=True)
        self._bind_mousewheel_scroll()
        self._build_date_headers()
        self._show_empty_grid_message()
        self.after(200, self._scroll_to_today)
        self.after_idle(self._sync_scrollbar_gutter)
        self.fetch_tasks_from_server()

    def _grid_width(self):
        return len(self.dates) * DATE_COLUMN_WIDTH

    def _grid_height(self):
        if not self.tasks:
            return DATE_ROW_HEIGHT * 2
        return self.current_row * DATE_ROW_HEIGHT

    def _col_x(self, col_idx):
        return col_idx * DATE_COLUMN_WIDTH

    def _row_y(self, row_idx):
        return row_idx * DATE_ROW_HEIGHT

    def _sync_scrollbar_gutter(self):
        try:
            self.update_idletasks()
            width = max(self.body_v_scroll.winfo_width(), SCROLLBAR_GUTTER)
            self.dates_area.grid_columnconfigure(1, minsize=width, weight=0)
            self.body_v_scroll.configure(width=width)
            self.header_gutter.configure(width=width)
            self.scroll_corner.configure(width=width)
        except (tk.TclError, AttributeError):
            return

    def _update_scroll_regions(self):
        width = self._grid_width()
        height = self._grid_height()
        self.header_canvas.configure(scrollregion=(0, 0, width, DATE_ROW_HEIGHT))
        self.body_canvas.configure(scrollregion=(0, 0, width, height))
        self.tasks_canvas.configure(scrollregion=(0, 0, TASK_COLUMN_WIDTH, height))

    def _on_body_xscroll(self, *args):
        self.header_canvas.xview(*args)
        self.body_canvas.xview(*args)

    def _on_body_xscroll_set(self, first, last):
        self.body_h_scroll.set(first, last)

    def _on_body_yscroll(self, *args):
        self.body_canvas.yview(*args)
        self.tasks_canvas.yview(*args)

    def _on_body_yscroll_set(self, first, last):
        self.body_v_scroll.set(first, last)

    def _bind_mousewheel_scroll(self):
        def on_wheel(event):
            delta = -1 * (event.delta // 120) if event.delta else 0
            if delta:
                self._scroll_vertical(delta)

        for widget in (self.body_canvas, self.tasks_canvas):
            widget.bind("<MouseWheel>", on_wheel)
            widget.bind("<Button-4>", lambda _e: self._scroll_vertical(-1))
            widget.bind("<Button-5>", lambda _e: self._scroll_vertical(1))

    def _scroll_vertical(self, delta):
        self.body_canvas.yview_scroll(delta, "units")
        self.tasks_canvas.yview_scroll(delta, "units")

    def _scroll_to_today(self):
        try:
            today_index = self.dates.index(self.today)
            total = max(len(self.dates), 1)
            fraction = max(0.0, (today_index - 3) / total)
            self._on_body_xscroll("moveto", fraction)
        except ValueError:
            pass

    def _build_date_headers(self):
        self.header_canvas.delete("all")
        for col_idx, date_obj in enumerate(self.dates):
            x1 = self._col_x(col_idx)
            x2 = x1 + DATE_COLUMN_WIDTH
            text, fg, bg = self._date_header_style(date_obj)
            self.header_canvas.create_rectangle(x1, 0, x2, DATE_ROW_HEIGHT, fill=bg, outline=COLORS["border"])
            self.header_canvas.create_text(
                (x1 + x2) // 2,
                DATE_ROW_HEIGHT // 2,
                text=text,
                fill=fg,
                font=(FONTS["small"][0], 10, "bold"),
            )
        self._update_scroll_regions()

    def _date_header_style(self, date_obj):
        if date_obj == self.today:
            return str(date_obj.day), COLORS["today"], COLORS["accent_soft"]
        if date_obj.weekday() >= 5:
            return str(date_obj.day), COLORS["weekend"], COLORS["card_hover"]
        if date_obj.day == 1:
            return f"{date_obj.day}\n{date_obj.strftime('%b')}", COLORS["text_muted"], COLORS["card_hover"]
        return str(date_obj.day), COLORS["text_muted"], COLORS["card_hover"]

    def _show_empty_grid_message(self):
        self.body_canvas.delete("all")
        self.body_canvas.create_text(
            20,
            40,
            text="No habits yet — add your first one above.",
            anchor="nw",
            fill=COLORS["text_muted"],
            font=(FONTS["body"][0], 13),
            tags="empty",
        )
        self._update_scroll_regions()

    def _cell_colors(self, date_obj, completed, row_idx):
        row_bg = COLORS["card"] if row_idx % 2 == 0 else COLORS["bg"]
        if completed:
            return COLORS["accent"], COLORS["text"]
        if date_obj == self.today:
            return COLORS["accent_soft"], COLORS["text_muted"]
        return row_bg, COLORS["border"]

    def _draw_task_row_canvas(self, task_id, row_idx, completed_dates):
        y1 = self._row_y(row_idx)
        y2 = y1 + DATE_ROW_HEIGHT
        tag = f"task_{task_id}"

        for col_idx, date_obj in enumerate(self.dates):
            date_str = date_obj.strftime("%Y-%m-%d")
            completed = date_str in completed_dates
            fill, outline = self._cell_colors(date_obj, completed, row_idx)
            x1 = self._col_x(col_idx)
            x2 = x1 + DATE_COLUMN_WIDTH

            self.body_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill,
                outline=outline if not completed else fill,
                tags=(tag, f"cell_{task_id}_{col_idx}"),
            )
            if completed:
                self.body_canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text="✓",
                    fill=COLORS["text"],
                    font=(FONTS["body"][0], 12, "bold"),
                    tags=(tag, f"cell_{task_id}_{col_idx}"),
                )

    def _draw_task_name_row(self, task_id, row_idx, task_name):
        y1 = self._row_y(row_idx)
        y2 = y1 + DATE_ROW_HEIGHT
        row_bg = COLORS["card"] if row_idx % 2 == 0 else COLORS["bg"]
        tag = f"task_{task_id}"

        self.tasks_canvas.create_rectangle(
            0, y1, TASK_COLUMN_WIDTH, y2,
            fill=row_bg,
            outline=COLORS["border"],
            tags=tag,
        )
        self.tasks_canvas.create_text(
            12, (y1 + y2) // 2,
            text=task_name,
            anchor="w",
            fill=COLORS["text"],
            font=(FONTS["body"][0], 13),
            tags=tag,
        )
        self.tasks_canvas.create_text(
            TASK_COLUMN_WIDTH - 16, (y1 + y2) // 2,
            text="×",
            anchor="e",
            fill=COLORS["text_muted"],
            font=(FONTS["body"][0], 16, "bold"),
            tags=(tag, f"delete_{task_id}"),
        )
        self.tasks_canvas.tag_bind(f"delete_{task_id}", "<Button-1>", lambda _e, t=task_id: self.delete_task(t))

    def _on_grid_click(self, event):
        if self._today_col < 0:
            return

        col = int(self.body_canvas.canvasx(event.x) // DATE_COLUMN_WIDTH)
        row = int(self.body_canvas.canvasy(event.y) // DATE_ROW_HEIGHT)
        if col != self._today_col:
            return

        task_id = next(
            (tid for tid, data in self.tasks.items() if data["row_idx"] == row),
            None,
        )
        if task_id is None:
            return

        date_str = self.today.strftime("%Y-%m-%d")
        completed = self.tasks[task_id]["completed"]
        if date_str in completed:
            completed.discard(date_str)
            new_status = False
        else:
            completed.add(date_str)
            new_status = True

        self.body_canvas.delete(f"task_{task_id}")
        self._draw_task_row_canvas(task_id, self.tasks[task_id]["row_idx"], completed)
        threading.Thread(
            target=self._async_toggle_task,
            args=(task_id, date_str, new_status),
            daemon=True,
        ).start()

    def _build_last_three_months(self):
        today = self.today
        month = today.month - 3
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        last_day = calendar.monthrange(year, month)[1]
        start = datetime.date(year, month, min(today.day, last_day))
        dates = []
        current = start
        while current <= today:
            dates.append(current)
            current += datetime.timedelta(days=1)
        return dates

    def _range_label_text(self):
        if not self.dates:
            return "No date range"
        start = self.dates[0].strftime("%b %d, %Y")
        end = self.dates[-1].strftime("%b %d, %Y")
        return (
            f"Last 3 months · {start} — {end} · {len(self.dates)} days · "
            f"green column = today · scroll horizontally for earlier dates"
        )

    def fetch_tasks_from_server(self):
        threading.Thread(target=self._async_fetch_tasks, daemon=True).start()

    def _async_fetch_tasks(self):
        try:
            response = self.api.get("/tasks", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.after(0, self._render_fetched_tasks, data)
        except requests.RequestException:
            pass

    def _render_fetched_tasks(self, tasks_data):
        for task in tasks_data:
            self._render_task_row(
                task.get("id"),
                task.get("name"),
                task.get("completedDates", []),
            )

    def add_task(self):
        task_name = self.task_entry.get().strip()
        if not task_name:
            return
        self.btn_add_task.configure(state="disabled", text="Adding…")
        threading.Thread(target=self._async_add_task, args=(task_name,), daemon=True).start()

    def _async_add_task(self, task_name):
        try:
            response = self.api.post(
                "/tasks",
                json={"name": task_name, "completedDates": []},
                timeout=5,
            )
            if response.status_code == 200:
                created_task = response.json()
                self.after(0, self._finalize_add_task, created_task.get("id"), task_name)
            else:
                self.after(0, self._reset_add_button)
        except requests.RequestException:
            self.after(0, self._reset_add_button)

    def _finalize_add_task(self, task_id, task_name):
        self._render_task_row(task_id, task_name, [])
        self.task_entry.delete(0, "end")
        self._reset_add_button()

    def _reset_add_button(self):
        self.btn_add_task.configure(state="normal", text="Add Habit")

    def _render_task_row(self, task_id, task_name, completed_dates):
        if task_id in self.tasks:
            return

        row_idx = self.current_row
        self.current_row += 1
        self.tasks[task_id] = {
            "name": task_name,
            "row_idx": row_idx,
            "completed": set(completed_dates),
        }
        if row_idx == 0 and self.body_canvas.find_withtag("empty"):
            self.body_canvas.delete("empty")

        self._draw_task_name_row(task_id, row_idx, task_name)
        self._draw_task_row_canvas(task_id, row_idx, self.tasks[task_id]["completed"])
        self._update_scroll_regions()

    def _async_toggle_task(self, task_id, date_str, status):
        try:
            self.api.put(
                f"/tasks/{task_id}/history",
                json={"date": date_str, "completed": status},
                timeout=5,
            )
        except requests.RequestException:
            pass

    def delete_task(self, task_id):
        if task_id not in self.tasks:
            return

        del self.tasks[task_id]
        self.tasks_canvas.delete(f"task_{task_id}")
        self.body_canvas.delete(f"task_{task_id}")

        threading.Thread(target=self._async_delete_task, args=(task_id,), daemon=True).start()

        if not self.tasks:
            self.current_row = 0
            self._show_empty_grid_message()
            self.tasks_canvas.delete("all")
        else:
            self._update_scroll_regions()

    def _async_delete_task(self, task_id):
        try:
            self.api.delete(f"/tasks/{task_id}", timeout=5)
        except requests.RequestException:
            pass
