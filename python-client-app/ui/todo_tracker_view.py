import datetime
import threading
import requests
import customtkinter as ctk


class TodoTrackerView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.api_base_url = "http://localhost:8081/api"

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.today = datetime.date.today()
        self.dates = [self.today + datetime.timedelta(days=i) for i in range(-3, 4)]

        self.tasks = {}
        self.current_row = 1

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.header_frame, text="Habit & Task Spreadsheet",
                                        font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.task_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter new daily task...", width=300)
        self.task_entry.pack(side="left", padx=(0, 10))

        self.btn_add_task = ctk.CTkButton(self.input_frame, text="Add Task", command=self.add_task)
        self.btn_add_task.pack(side="left")

        self.grid_frame = ctk.CTkScrollableFrame(self)
        self.grid_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.grid_frame.grid_columnconfigure(0, weight=1)

        self.build_grid_headers()
        self.fetch_tasks_from_server()

    def build_grid_headers(self):
        header_task = ctk.CTkLabel(self.grid_frame, text="Task Name", font=ctk.CTkFont(weight="bold"))
        header_task.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        for col_idx, date_obj in enumerate(self.dates, start=1):
            date_str = date_obj.strftime("%b %d")
            if date_obj == self.today:
                date_str = f"{date_str}\n(Today)"
                text_color = "#00cc66"
            else:
                text_color = "white"

            header_date = ctk.CTkLabel(self.grid_frame, text=date_str, text_color=text_color,
                                       font=ctk.CTkFont(weight="bold"))
            header_date.grid(row=0, column=col_idx, padx=15, pady=10)

        header_action = ctk.CTkLabel(self.grid_frame, text="Action", font=ctk.CTkFont(weight="bold"))
        header_action.grid(row=0, column=len(self.dates) + 1, padx=10, pady=10)

    def fetch_tasks_from_server(self):
        threading.Thread(target=self._async_fetch_tasks, daemon=True).start()

    def _async_fetch_tasks(self):
        try:
            response = requests.get(f"{self.api_base_url}/tasks", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.after(0, self._render_fetched_tasks, data)
        except requests.RequestException:
            pass

    def _render_fetched_tasks(self, tasks_data):
        for task in tasks_data:
            task_id = task.get("id")
            name = task.get("name")
            completed_dates = task.get("completedDates", [])
            self._render_task_row(task_id, name, completed_dates)

    def add_task(self):
        task_name = self.task_entry.get().strip()
        if not task_name:
            return

        self.btn_add_task.configure(state="disabled", text="Adding...")
        threading.Thread(target=self._async_add_task, args=(task_name,), daemon=True).start()

    def _async_add_task(self, task_name):
        try:
            response = requests.post(f"{self.api_base_url}/tasks", json={"name": task_name, "completedDates": []},
                                     timeout=5)
            if response.status_code == 200:
                created_task = response.json()
                task_id = created_task.get("id")
                self.after(0, self._finalize_add_task, task_id, task_name)
            else:
                self.after(0, self._reset_add_button)
        except requests.RequestException:
            self.after(0, self._reset_add_button)

    def _finalize_add_task(self, task_id, task_name):
        self._render_task_row(task_id, task_name, [])
        self.task_entry.delete(0, 'end')
        self._reset_add_button()

    def _reset_add_button(self):
        self.btn_add_task.configure(state="normal", text="Add Task")

    def _render_task_row(self, task_id, task_name, completed_dates):
        if task_id in self.tasks:
            return

        self.tasks[task_id] = {"name": task_name}
        row_idx = self.current_row
        self.current_row += 1

        task_label = ctk.CTkLabel(self.grid_frame, text=task_name)
        task_label.grid(row=row_idx, column=0, padx=10, pady=10, sticky="w")

        checkboxes = []
        for col_idx, date_obj in enumerate(self.dates, start=1):
            date_str = date_obj.strftime("%Y-%m-%d")
            var = ctk.StringVar(value="on" if date_str in completed_dates else "off")

            cb_state = "normal" if date_obj == self.today else "disabled"

            cb = ctk.CTkCheckBox(
                self.grid_frame,
                text="",
                variable=var,
                onvalue="on",
                offvalue="off",
                state=cb_state,
                width=24,
                command=lambda t_id=task_id, d=date_obj, v=var: self.toggle_task(t_id, d, v)
            )
            cb.grid(row=row_idx, column=col_idx, padx=15, pady=10)
            checkboxes.append(cb)

        btn_delete = ctk.CTkButton(
            self.grid_frame,
            text="Delete",
            fg_color="#ff4d4d",
            hover_color="#cc0000",
            width=60,
            command=lambda t_id=task_id, r=row_idx, l=task_label, cbs=checkboxes: self.delete_task(t_id, r, l, cbs)
        )
        btn_delete.grid(row=row_idx, column=len(self.dates) + 1, padx=10, pady=10)

    def toggle_task(self, task_id, date_obj, var):
        status = var.get() == "on"
        date_str = date_obj.strftime("%Y-%m-%d")
        threading.Thread(target=self._async_toggle_task, args=(task_id, date_str, status), daemon=True).start()

    def _async_toggle_task(self, task_id, date_str, status):
        try:
            payload = {"date": date_str, "completed": status}
            requests.put(f"{self.api_base_url}/tasks/{task_id}/history", json=payload, timeout=5)
        except requests.RequestException:
            pass

    def delete_task(self, task_id, row_idx, label_widget, checkboxes):
        label_widget.destroy()
        for cb in checkboxes:
            cb.destroy()

        grid_slaves = self.grid_frame.grid_slaves(row=row_idx, column=len(self.dates) + 1)
        for slave in grid_slaves:
            slave.destroy()

        del self.tasks[task_id]
        threading.Thread(target=self._async_delete_task, args=(task_id,), daemon=True).start()

    def _async_delete_task(self, task_id):
        try:
            requests.delete(f"{self.api_base_url}/tasks/{task_id}", timeout=5)
        except requests.RequestException:
            pass