"""
report.py — turns the collected data dict into a shareable HTML report,
and offers two ways to get it to someone else:

1. "mailto:" hand-off — opens the user's own default mail client with a
   prefilled subject/body pointing at the exported file. No credentials
   needed, works everywhere, user attaches the file themselves.
2. Optional direct SMTP send — only used if the user explicitly fills in
   their own SMTP server + login in Settings. Nothing is sent anywhere
   without the user typing their own mail server details in first.
"""
from __future__ import annotations

import html
import os
import platform
import smtplib
import socket
import webbrowser
from datetime import datetime
from email.message import EmailMessage
from typing import Any


CSS = """
:root{
  --bg:#0f1115; --panel:#171a21; --border:#2a2f3a; --text:#e7e9ee;
  --muted:#9aa3b2; --accent:#5b9dff;
}
*{box-sizing:border-box}
body{
  margin:0; padding:32px; background:var(--bg); color:var(--text);
  font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
}
h1{font-size:22px; margin:0 0 4px 0}
.subtitle{color:var(--muted); margin-bottom:24px; font-size:13px}
.section{
  background:var(--panel); border:1px solid var(--border); border-radius:10px;
  padding:16px 20px; margin-bottom:16px;
}
.section h2{font-size:15px; margin:0 0 12px 0; color:var(--accent)}
table{width:100%; border-collapse:collapse; font-size:13px}
td, th{padding:6px 10px; text-align:left; border-bottom:1px solid var(--border); vertical-align:top}
td.key{color:var(--muted); width:38%; white-space:nowrap}
.list-item{border-bottom:1px solid var(--border); padding:8px 0}
.list-item:last-child{border-bottom:none}
.badge{
  display:inline-block; font-size:11px; padding:2px 8px; border-radius:999px;
  background:#22314d; color:var(--accent); margin-left:8px;
}
footer{color:var(--muted); font-size:12px; margin-top:24px; text-align:center}
"""


def _render_value(v: Any) -> str:
    if isinstance(v, dict):
        rows = "".join(
            f"<tr><td class='key'>{html.escape(str(k))}</td><td>{_render_value(val)}</td></tr>"
            for k, val in v.items()
        )
        return f"<table>{rows}</table>"
    if isinstance(v, list):
        if not v:
            return "<em>n/a</em>"
        if all(isinstance(x, dict) for x in v):
            parts = [f"<div class='list-item'>{_render_value(x)}</div>" for x in v]
            return "".join(parts)
        return "<ul>" + "".join(f"<li>{html.escape(str(x))}</li>" for x in v) + "</ul>"
    return html.escape(str(v))


def build_html_report(data: dict[str, Any], title: str = "System Info Report") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()
    os_name = f"{platform.system()} {platform.release()}"

    sections = []
    for section_name, section_data in data.items():
        sections.append(f"""
        <div class="section">
          <h2>{html.escape(section_name)}</h2>
          {_render_value(section_data)}
        </div>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)} — {html.escape(hostname)}</title>
<style>{CSS}</style>
</head>
<body>
  <h1>{html.escape(title)} <span class="badge">{html.escape(os_name)}</span></h1>
  <div class="subtitle">Host: {html.escape(hostname)} &nbsp;•&nbsp; Generated: {now}</div>
  {''.join(sections)}
  <footer>Generated locally by System Info Tool — no data leaves this machine unless you export or send it yourself.</footer>
</body>
</html>"""


def save_report(html_str: str, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_str)
    return path


def open_share_via_default_mail_client(to_addr: str, subject: str, exported_path: str) -> None:
    """
    Opens the OS's own default mail app with a prefilled draft. This is
    the safest, credential-free sharing path — the user reviews and
    attaches the file themselves before hitting send.
    """
    body = (
        f"System info report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}.\n\n"
        f"Please attach the exported file before sending:\n{exported_path}\n"
    )
    import urllib.parse
    url = f"mailto:{urllib.parse.quote(to_addr)}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    webbrowser.open(url)


def send_via_smtp(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    to_addr: str,
    subject: str,
    html_body: str,
    use_tls: bool = True,
) -> None:
    """
    Direct send — only ever called if the user has typed their own SMTP
    server + credentials into the app's Settings panel. The app never
    ships with, stores remotely, or defaults to any mail server.
    """
    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content("This report requires an HTML-capable mail client to view.")
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        if use_tls:
            server.starttls()
        server.login(username, password)
        server.send_message(msg)
