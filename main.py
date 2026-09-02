"""
System Info Tool — cross-platform (Windows 8/8.1/10/11 + Linux) hardware
and OS information dashboard, in the spirit of PC Internals / TMOG, but
focused on full static + live info rather than a live performance HUD.

Run directly:      python main.py
Portable build:     see README.md (PyInstaller --onefile instructions)
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
import platform
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from collectors import aggregate
from portable import get_app_data_dir, is_portable_mode, load_settings, save_settings
import report as report_mod

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "System Info Tool"
def get_tab_order():
    """Return appropriate tab order based on platform."""
    if platform.system() == "Windows":
        return [
            ("Overview", ["Operating System"]),
            ("CPU", ["CPU (overview)", "CPU (detail)"]),
            ("GPU", ["GPU"]),
            ("Memory", ["Memory", "RAM Modules"]),
            ("Motherboard", ["Motherboard / BIOS", "Chipset", "BIOS Detail", "Windows Edition Detail"]),
            ("Storage", ["Storage (volumes)", "Storage (physical/SMART)"]),
            ("Network", ["Network (interfaces)"]),
            ("Drivers", ["Drivers / Kernel Modules"]),
            ("Processes", ["Top Processes (by RAM)"]),
            ("Battery", ["Battery", "Battery Detail"]),
            ("Display", ["EDID / Monitor Info"]),
            ("System Info", ["ACPI / SMBIOS", "SMBIOS / DMI"]),
            ("Bus Info", ["PCI / USB Bus"]),
        ]
    elif platform.system() == "Linux":
        return [
            ("Overview", ["Operating System"]),
            ("CPU", ["CPU (overview)", "CPU (detail)"]),
            ("GPU", ["GPU"]),
            ("Memory", ["Memory"]),
            ("Motherboard", ["Motherboard / BIOS", "Chipset"]),
            ("Storage", ["Storage (volumes)", "Storage (physical/SMART)"]),
            ("Network", ["Network (interfaces)", "Network Hardware"]),
            ("Drivers", ["Drivers / Kernel Modules"]),
            ("Processes", ["Top Processes (by RAM)"]),
            ("Battery", ["Battery"]),
        ]
    elif platform.system() == "Darwin":  # macOS
        return [
            ("Overview", ["Operating System"]),
            ("CPU", ["CPU (overview)", "CPU (detail)"]),
            ("GPU", ["GPU"]),
            ("Memory", ["Memory"]),
            ("Motherboard", ["Motherboard / BIOS", "Chipset"]),
            ("Storage", ["Storage (volumes)", "Storage (physical/SMART)"]),
            ("Network", ["Network (interfaces)", "Network Hardware"]),
            ("Drivers", ["Drivers / Kernel Modules"]),
            ("Processes", ["Top Processes (by RAM)"]),
            ("Battery", ["Battery", "Battery Detail"]),
            ("System Info", ["SMBIOS / DMI"]),
        ]
    else:
        return [
            ("Overview", ["Operating System"]),
            ("CPU", ["CPU (overview)"]),
            ("GPU", ["GPU"]),
            ("Memory", ["Memory"]),
            ("Motherboard", ["Motherboard / BIOS"]),
            ("Storage", ["Storage (volumes)"]),
            ("Network", ["Network (interfaces)"]),
            ("Drivers", ["Drivers / Kernel Modules"]),
            ("Processes", ["Top Processes (by RAM)"]),
            ("Battery", ["Battery"]),
        ]

TAB_ORDER = get_tab_order()


def _flatten_for_display(value, indent=0) -> list[tuple[str, str]]:
    """Turn a nested dict/list structure into (label, value) row pairs
    with indentation, for a simple readable text/grid view."""
    rows = []
    pad = "    " * indent
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                rows.append((f"{pad}{k}", ""))
                rows.extend(_flatten_for_display(v, indent + 1))
            else:
                rows.append((f"{pad}{k}", str(v)))
    elif isinstance(value, list):
        if not value:
            rows.append((f"{pad}(none found)", ""))
        for i, item in enumerate(value):
            if isinstance(item, dict):
                rows.append((f"{pad}#{i + 1}", ""))
                rows.extend(_flatten_for_display(item, indent + 1))
            else:
                rows.append((f"{pad}-", str(item)))
    else:
        rows.append((pad, str(value)))
    return rows


class SectionPanel(ctk.CTkScrollableFrame):
    """One scrollable panel showing one or more report sections as rows."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)

    def render(self, sections: dict[str, object], section_keys: list[str]):
        for w in self.winfo_children():
            w.destroy()

        row_idx = 0
        for key in section_keys:
            data = sections.get(key)
            if data is None:
                continue
            header = ctk.CTkLabel(
                self, text=key, font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
            )
            header.grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(14, 4), padx=4)
            row_idx += 1

            # Limit the number of rows rendered for performance
            max_rows = 200
            current_rows = 0
            for label, val in _flatten_for_display(data):
                if current_rows >= max_rows:
                    # Add a note that data is limited
                    limit_note = ctk.CTkLabel(
                        self, text="... (display limited for performance)", 
                        anchor="w", text_color="#9aa3b2"
                    )
                    limit_note.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=(12, 8), pady=4)
                    row_idx += 1
                    break
                    
                lbl = ctk.CTkLabel(self, text=label, anchor="w", text_color="#9aa3b2")
                lbl.grid(row=row_idx, column=0, sticky="w", padx=(12, 8), pady=1)
                val_lbl = ctk.CTkLabel(self, text=val, anchor="w", justify="left", wraplength=520)
                val_lbl.grid(row=row_idx, column=1, sticky="w", pady=1)
                row_idx += 1
                current_rows += 1


class SystemInfoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE + (" (Portable)" if is_portable_mode() else ""))
        self.geometry("980x680")
        self.minsize(760, 520)

        self.settings = load_settings()
        self.report_data: dict = {}
        self.last_export_path: str | None = None

        self._build_top_bar()
        self._build_tabs()
        self._build_status_bar()

        # First collection on startup, off the UI thread.
        self.after(150, self.refresh_data)

    # ---------- layout ----------

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, height=48, corner_radius=0)
        bar.pack(side="top", fill="x")

        title = ctk.CTkLabel(bar, text=APP_TITLE, font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(side="left", padx=16, pady=8)

        self.refresh_btn = ctk.CTkButton(bar, text="Refresh", width=90, command=self.refresh_data)
        self.refresh_btn.pack(side="right", padx=(4, 12), pady=8)

        self.export_btn = ctk.CTkButton(bar, text="Export HTML Report", width=150, command=self.export_report)
        self.export_btn.pack(side="right", padx=4, pady=8)

        self.share_btn = ctk.CTkButton(bar, text="Share via Email", width=130, command=self.share_via_email)
        self.share_btn.pack(side="right", padx=4, pady=8)

        self.settings_btn = ctk.CTkButton(bar, text="Settings", width=90, command=self.open_settings)
        self.settings_btn.pack(side="right", padx=4, pady=8)

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(side="top", fill="both", expand=True, padx=10, pady=(6, 0))

        self.panels: dict[str, SectionPanel] = {}
        for tab_name, _keys in TAB_ORDER:
            self.tabview.add(tab_name)
            panel = SectionPanel(self.tabview.tab(tab_name))
            panel.pack(fill="both", expand=True)
            self.panels[tab_name] = panel

    def _build_status_bar(self):
        self.status_var = ctk.StringVar(value="Ready.")
        status = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", text_color="#9aa3b2")
        status.pack(side="bottom", fill="x", padx=12, pady=6)

    # ---------- data ----------

    def refresh_data(self):
        self.status_var.set("Collecting system information…")
        self.refresh_btn.configure(state="disabled")
        threading.Thread(target=self._collect_in_background, daemon=True).start()

    def _collect_in_background(self):
        try:
            data = aggregate.collect_all()
        except Exception as e:
            data = {"Error": {"message": str(e)}}
        self.after(0, lambda: self._on_data_collected(data))

    def _on_data_collected(self, data: dict):
        self.report_data = data
        # Render all tabs but with row limits for performance
        for tab_name, keys in TAB_ORDER:
            self.panels[tab_name].render(data, keys)
        
        self.status_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        self.refresh_btn.configure(state="normal")

    # ---------- export / share ----------

    def export_report(self):
        if not self.report_data:
            messagebox.showinfo(APP_TITLE, "Nothing collected yet — click Refresh first.")
            return

        default_dir = get_app_data_dir()
        default_name = f"system-info-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".html",
            filetypes=[("HTML report", "*.html")],
        )
        if not path:
            return

        html_str = report_mod.build_html_report(self.report_data, title="System Info Report")
        report_mod.save_report(html_str, path)
        self.last_export_path = path
        self.status_var.set(f"Report exported to {path}")
        messagebox.showinfo(APP_TITLE, f"Report saved:\n{path}")

    def share_via_email(self):
        if not self.report_data:
            messagebox.showinfo(APP_TITLE, "Nothing collected yet — click Refresh first.")
            return
        if not self.last_export_path:
            # export first so there's something to attach
            self.export_report()
            if not self.last_export_path:
                return

        to_addr = self.settings.get("default_share_email", "")
        subject = f"System Info Report — {datetime.now().strftime('%Y-%m-%d')}"

        smtp_cfg = self.settings.get("smtp", {})
        if smtp_cfg.get("host") and smtp_cfg.get("username") and smtp_cfg.get("password"):
            # Direct send is only offered if the user configured their own SMTP in Settings.
            if messagebox.askyesno(
                APP_TITLE,
                f"Send this report directly via your configured SMTP account to {to_addr or '(no address set)'}?\n\n"
                f"Choose 'No' to instead open your default mail app so you can review it first.",
            ):
                try:
                    html_str = report_mod.build_html_report(self.report_data, title="System Info Report")
                    report_mod.send_via_smtp(
                        smtp_host=smtp_cfg["host"],
                        smtp_port=int(smtp_cfg.get("port", 587)),
                        username=smtp_cfg["username"],
                        password=smtp_cfg["password"],
                        to_addr=to_addr,
                        subject=subject,
                        html_body=html_str,
                        use_tls=smtp_cfg.get("use_tls", True),
                    )
                    messagebox.showinfo(APP_TITLE, "Report sent.")
                except Exception as e:
                    messagebox.showerror(APP_TITLE, f"Could not send: {e}")
                return

        report_mod.open_share_via_default_mail_client(to_addr, subject, self.last_export_path)
        self.status_var.set("Opened default mail app with a draft — attach the file to send.")

    def open_settings(self):
        SettingsDialog(self, self.settings, on_save=self._on_settings_saved)

    def _on_settings_saved(self, new_settings: dict):
        self.settings = new_settings
        save_settings(new_settings)
        self.status_var.set("Settings saved.")


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, settings: dict, on_save):
        super().__init__(master)
        self.title("Settings")
        self.geometry("420x420")
        self.on_save = on_save
        self.settings = dict(settings)
        smtp = self.settings.get("smtp", {})

        pad = {"padx": 14, "pady": 6}

        ctk.CTkLabel(self, text="Default share email (To:)").pack(anchor="w", **pad)
        self.email_var = ctk.StringVar(value=self.settings.get("default_share_email", ""))
        ctk.CTkEntry(self, textvariable=self.email_var, width=360).pack(**pad)

        ctk.CTkLabel(
            self, text="Optional: your own SMTP account, for direct sending\n"
                       "instead of the default mail-app hand-off.",
            justify="left", text_color="#9aa3b2",
        ).pack(anchor="w", **pad)

        self.smtp_host = ctk.StringVar(value=smtp.get("host", ""))
        self.smtp_port = ctk.StringVar(value=str(smtp.get("port", 587)))
        self.smtp_user = ctk.StringVar(value=smtp.get("username", ""))
        self.smtp_pass = ctk.StringVar(value=smtp.get("password", ""))
        self.smtp_tls = ctk.BooleanVar(value=smtp.get("use_tls", True))

        for label, var, show in [
            ("SMTP host (e.g. smtp.gmail.com)", self.smtp_host, None),
            ("SMTP port", self.smtp_port, None),
            ("Username / email", self.smtp_user, None),
            ("Password / app password", self.smtp_pass, "*"),
        ]:
            ctk.CTkLabel(self, text=label).pack(anchor="w", **pad)
            ctk.CTkEntry(self, textvariable=var, width=360, show=show).pack(**pad)

        ctk.CTkCheckBox(self, text="Use STARTTLS", variable=self.smtp_tls).pack(anchor="w", **pad)

        ctk.CTkButton(self, text="Save", command=self._save).pack(pady=16)

    def _save(self):
        self.settings["default_share_email"] = self.email_var.get().strip()
        try:
            port = int(self.smtp_port.get().strip() or 587)
        except ValueError:
            port = 587
        self.settings["smtp"] = {
            "host": self.smtp_host.get().strip(),
            "port": port,
            "username": self.smtp_user.get().strip(),
            "password": self.smtp_pass.get(),
            "use_tls": bool(self.smtp_tls.get()),
        }
        self.on_save(self.settings)
        self.destroy()


def main():
    app = SystemInfoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
