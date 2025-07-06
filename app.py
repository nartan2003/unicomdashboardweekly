from flask import Flask, request, render_template_string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

app = Flask(__name__)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

# Main Google Sheet name
SHEET_NAME = "Weekly Client Dashboard"

# Headers
HEADERS = [
    "Tenant Name", "Tenant Code", "Golive AM", "Go Live Mgr",
    "Current Status", "Dashboard Status", "Remarks"
]

# Get sheet tab for current week
def get_current_week_tab():
    year, week, _ = datetime.now().isocalendar()
    week_tab_name = f"Week {year}-W{week}"

    spreadsheet = client.open(SHEET_NAME)
    
    try:
        worksheet = spreadsheet.worksheet(week_tab_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=week_tab_name, rows="100", cols="10")
        worksheet.append_row(HEADERS)

    return worksheet

# HTML UI Template
SHEET_ID = "1m57mjkgMr1JLrpPapV-pNOZva-8zeY_8wtJlyFbbhQQ"  # your actual Sheet ID

form_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Client Dashboard – Unicommerce</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f9;
      padding: 20px;
    }}
    h1 {{
      text-align: center;
      color: #333;
    }}
    .logo {{
      position: absolute;
      left: 20px;
      top: 10px;
      height: 40px;
    }}
    form {{
      max-width: 800px;
      margin: 80px auto 20px auto;
      background: #fff;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    input, select, textarea {{
      width: 100%;
      padding: 10px;
      margin-top: 8px;
      margin-bottom: 15px;
      border: 1px solid #ccc;
      border-radius: 6px;
      box-sizing: border-box;
    }}
    label {{
      font-weight: 600;
    }}
    button {{
      background-color: #007bff;
      color: white;
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
    }}
    button:hover {{
      background-color: #0056b3;
    }}
    .download-button {{
      display: inline-block;
      border-radius:5px;
      background-color: #28a745;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      text-decoration: none;
      font-weight: bold;
      float: right;
      margin: 10px 0;
    }}
  </style>
</head>
<body>
  <img src="https://infowordpress.s3.ap-south-1.amazonaws.com/wp-content/uploads/2023/02/03060918/unicommerce-logo.jpg" class="logo">
  <h1>🧾 Weekly Client Dashboard</h1>

  <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx" target="_blank" class="download-button">
   Download Current Sheet
  </a>

  <form method="POST">
    <label>Tenant Name</label>
    <input name="tenant_name" required>

    <label>Tenant Code</label>
    <input name="tenant_code" required>

    <label>Golive AM</label>
    <input name="golive_am" required>

    <label>Go Live Mgr</label>
    <input name="golive_mgr" required>

    <label>status</label>
    <input name="status" required>
   
    <label>Dashboard Status</label>
    <input name="dashboard_status" required>

    <label>Remarks</label>
    <textarea name="remarks" rows="3"></textarea>

    <button type="submit">➕ Submit Update</button>
  </form>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        worksheet = get_current_week_tab()
        data = [
            request.form.get("tenant_name"),
            request.form.get("tenant_code"),
            request.form.get("golive_am"),
            request.form.get("golive_mgr"),
            request.form.get("status"),
            request.form.get("dashboard_status"),
            request.form.get("remarks")
        ]
        worksheet.append_row(data)
        return "✅ Data submitted successfully! <a href='/'>Submit another</a>"
    return render_template_string(form_html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # For Railway
    app.run(host="0.0.0.0", port=port)
