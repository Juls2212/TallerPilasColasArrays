import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Transaction


class BankingUI:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Bank Transfer Simulator")
        self.root.geometry("950x600")
        self.root.minsize(880, 540)

        self._build_style()
        self._build_layout()
        self._refresh_all()
        self._poll_events()

    def run(self):
        self.root.mainloop()


    def _build_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Muted.TLabel", foreground="#444")

    def _build_layout(self):
        header = ttk.Frame(self.root, padding=(14, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Bank Transfer Simulator", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="(Interactive UI - Data Structures Demo)", style="Muted.TLabel").pack(side="left", padx=10)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(header, textvariable=self.status_var, style="Muted.TLabel").pack(side="right")

        body = ttk.Frame(self.root, padding=(14, 10))
        body.pack(fill="both", expand=True)

        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill="both", expand=True)

        self.tab_new = ttk.Frame(self.tabs, padding=12)
        self.tab_pending = ttk.Frame(self.tabs, padding=12)
        self.tab_accounts = ttk.Frame(self.tabs, padding=12)

        self.tabs.add(self.tab_new, text="New Transfer")
        self.tabs.add(self.tab_pending, text="Pending")
        self.tabs.add(self.tab_accounts, text="Accounts & Log")

        self._build_new_tab()
        self._build_pending_tab()
        self._build_accounts_tab()


    def _build_new_tab(self):
        form = ttk.Labelframe(self.tab_new, text="Transfer details", padding=12)
        form.pack(fill="x")

        self.txid_var = tk.StringVar(value="")
        self.origin_var = tk.StringVar(value="ACC-1001")
        self.dest_var = tk.StringVar(value="ACC-2002")
        self.amount_var = tk.StringVar(value="100")

        self._row(form, "Transfer ID (optional)", self.txid_var)
        self._row(form, "From account", self.origin_var)
        self._row(form, "To account", self.dest_var)
        self._row(form, "Amount", self.amount_var)

        btns = ttk.Frame(self.tab_new)
        btns.pack(fill="x", pady=(10, 0))

        ttk.Button(btns, text="Add to pending list", command=self._add_transfer).pack(side="left")
        ttk.Button(btns, text="Reset", command=self._reset_form).pack(side="left", padx=8)

        settings = ttk.Labelframe(self.tab_new, text="Simulation", padding=12)
        settings.pack(fill="x", pady=(12, 0))

        self.slow_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings, text="Slow server mode", variable=self.slow_var, command=self._toggle_slow).pack(anchor="w")

        ttk.Label(settings, text="Failure simulation:", style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        self.fail_choice = tk.StringVar(value="Medium (20%)")
        cb = ttk.Combobox(
            settings,
            textvariable=self.fail_choice,
            state="readonly",
            values=["Low (5%)", "Medium (20%)", "High (40%)"]
        )
        cb.pack(anchor="w", pady=(4, 0))
        cb.bind("<<ComboboxSelected>>", self._apply_failure_choice)
        self._apply_failure_choice()

        ttk.Label(
            self.tab_new,
            text="Tip: demo accounts ACC-1001, ACC-2002, ACC-3003, ACC-4004",
            style="Muted.TLabel"
        ).pack(anchor="w", pady=(10, 0))

    def _build_pending_tab(self):
        top = ttk.Frame(self.tab_pending)
        top.pack(fill="x")

        self.btn_next = ttk.Button(top, text="Process next", command=self._process_next)
        self.btn_next.pack(side="left")

        self.btn_all = ttk.Button(top, text="Process all", command=self._process_all)
        self.btn_all.pack(side="left", padx=8)

        ttk.Button(top, text="Clear list", command=self._clear_pending).pack(side="left", padx=8)
        ttk.Button(top, text="Refresh", command=self._refresh_all).pack(side="right")

        self.pending_table = self._make_table(
            self.tab_pending,
            columns=("id", "from", "to", "amount", "created"),
            headings=("ID", "From", "To", "Amount", "Created At"),
            widths=(120, 120, 120, 110, 180)
        )

        ttk.Label(self.tab_pending, text="Transfers are processed in arrival order.", style="Muted.TLabel").pack(anchor="w", pady=(8, 0))

    def _build_accounts_tab(self):
        split = ttk.Frame(self.tab_accounts)
        split.pack(fill="both", expand=True)

        left = ttk.Frame(split)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(split)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        ttk.Label(left, text="Account balances", style="Muted.TLabel").pack(anchor="w")
        self.accounts_table = self._make_table(
            left,
            columns=("account", "balance"),
            headings=("Account", "Balance"),
            widths=(160, 160),
            height=14
        )

        ttk.Label(right, text="Activity log", style="Muted.TLabel").pack(anchor="w")
        self.log_text = tk.Text(right, wrap="word", height=18)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Clear log", command=self._clear_log).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self._refresh_all).pack(side="right")

    def _row(self, parent, label, var):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=18).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)

    def _make_table(self, parent, columns, headings, widths, height=16):
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True, pady=(8, 0))

        table = ttk.Treeview(wrapper, columns=columns, show="headings", height=height)
        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=vsb.set)

        table.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for c, h, w in zip(columns, headings, widths):
            table.heading(c, text=h)
            table.column(c, width=w, anchor="w")

        return table

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self.btn_next.configure(state=state)
        self.btn_all.configure(state=state)
        self.status_var.set("Processing..." if busy else "Ready.")


    def _add_transfer(self):
        try:
            tx_id = self.txid_var.get().strip()
            origin = self.origin_var.get().strip()
            dest = self.dest_var.get().strip()
            amount = float(self.amount_var.get().strip())

            if not origin or not dest:
                messagebox.showerror("Validation", "Please enter both accounts.")
                return
            if amount <= 0:
                messagebox.showerror("Validation", "Amount must be greater than 0.")
                return

            if not tx_id:
                tx_id = self.controller.engine.next_tx_id()

            tx = Transaction(tx_id=tx_id, origin=origin, destination=dest, amount=amount)
            self.controller.add_transfer(tx)

            self._refresh_all()
            self.tabs.select(self.tab_pending)

        except ValueError:
            messagebox.showerror("Validation", "Invalid amount. Example: 250.50")

    def _process_next(self):
        if self.controller.engine.pending_count() == 0:
            messagebox.showinfo("Info", "There are no pending transfers.")
            return

        self._set_busy(True)
        self.controller.process_next_async(on_done=lambda: self.root.after(0, self._set_busy, False))

    def _process_all(self):
        if self.controller.engine.pending_count() == 0:
            messagebox.showinfo("Info", "There are no pending transfers.")
            return

        self._set_busy(True)
        self.controller.process_all_async(on_done=lambda: self.root.after(0, self._set_busy, False))

    def _clear_pending(self):
        self.controller.clear_pending()
        self._refresh_all()

    def _reset_form(self):
        self.txid_var.set("")
        self.origin_var.set("ACC-1001")
        self.dest_var.set("ACC-2002")
        self.amount_var.set("100")

    def _toggle_slow(self):
        self.controller.set_server_slow(self.slow_var.get())

    def _apply_failure_choice(self, _=None):
        choice = self.fail_choice.get()
        if "Low" in choice:
            rate = 0.05
        elif "High" in choice:
            rate = 0.40
        else:
            rate = 0.20
        self.controller.set_failure_rate(rate)


    def _refresh_all(self):
        engine = self.controller.engine
        self._fill_pending(engine.pending_snapshot())
        self._fill_accounts(engine.balances_snapshot())

    def _fill_pending(self, items):
        self._clear_table(self.pending_table)
        for tx in items:
            self.pending_table.insert("", "end", values=(
                tx.tx_id,
                tx.origin,
                tx.destination,
                f"{tx.amount:.2f}",
                tx.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ))

    def _fill_accounts(self, balances: dict):
        self._clear_table(self.accounts_table)
        for acc, bal in balances.items():
            self.accounts_table.insert("", "end", values=(acc, f"{bal:,.2f}"))

    def _clear_table(self, table):
        for row in table.get_children():
            table.delete(row)


    def _poll_events(self):
        for kind, msg in self.controller.drain_events():
            self._append_log(kind, msg)
            self.status_var.set(msg[:120])

        self.root.after(250, self._poll_events)

    def _append_log(self, kind: str, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {kind.upper()}: {msg}\n"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")