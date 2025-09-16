from __future__ import annotations
import smtplib, ssl, html
from typing import List, Dict, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

EMAIL_TMPL = Template('''
<!doctype html>
<html>
  <body>
    <h2>New Job Alerts ({{ total }})</h2>
    {% for job in jobs %}
    <div style="margin-bottom:16px;padding:12px;border:1px solid #eee;border-radius:10px;">
      <div style="font-weight:700;font-size:16px;">
        <a href="{{ job.url|e }}">{{ job.title|e }}</a>
      </div>
      <div>{{ job.company|e }} — {{ job.location|e }}{% if job.source %} ({{ job.source|e }}){% endif %}</div>
      {% if job.salary %}<div>Salary: {{ job.salary|e }}</div>{% endif %}
      {% if job.job_type %}<div>Type: {{ job.job_type|e }}</div>{% endif %}
      <p style="white-space:pre-wrap;">{{ (job.description or '')[:400] | e }}{% if (job.description or '')|length > 400 %}…{% endif %}</p>
    </div>
    {% endfor %}
  </body>
</html>
''')

class EmailNotifier:
    def __init__(self, email: str, password: str, smtp_server: str, smtp_port: int):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send(self, recipients: List[str], jobs: List[Dict[str, Any]]):
        if not recipients or not jobs:
            return
        subject = f"🚀 {len(jobs)} New Job Alert{'s' if len(jobs) != 1 else ''}"
        html_body = EMAIL_TMPL.render(total=len(jobs), jobs=jobs)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=context)
            server.login(self.email, self.password)
            server.sendmail(self.email, recipients, msg.as_string())
