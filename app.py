from flask import Flask, request, render_template_string, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_NAME = "Weekly Client Dashboard"
HEADERS = [
    "Date", "Tenant Code", "Golive AM", "Go Live Mgr",
    "Current Status", "Dashboard Status", "Remarks"
]
SHEET_ID = "1m57mjkgMr1JLrpPapV-pNOZva-8zeY_8wtJlyFbbhQQ"

# ----------------------------- Helpers -----------------------------
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

# ----------------------------- Main Form Route -----------------------------
form_html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Client Dashboard – Unicommerce</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f9;
      padding: 20px;
    }}
    h1 {{ text-align: center; color: #003366; }}
    .logo {{ position: absolute; left: 20px; top: 10px; height: 40px; }}
    .top-right {{ position: absolute; top: 20px; right: 20px; }}
    .icon-link {{
      text-decoration: none;
      font-size: 24px;
      margin-left: 15px;
    }}
    .icon-search {{ color: #007bff; }}
    .icon-delete {{ color: #dc3545; }}
    .icon-view {{ color: #28a745; }}
    form {{
      max-width: 800px;
      margin: 80px auto 20px auto;
      background: #fff;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    input, textarea, select {{
      width: 100%;
      padding: 10px;
      margin-top: 8px;
      margin-bottom: 15px;
      border: 1px solid #ccc;
      border-radius: 6px;
    }}
    label {{ font-weight: 600; }}
    button {{
      background-color: #007bff;
      color: white;
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
    }}
    .download-button {{
      display: inline-block;
      border-radius:5px;
      background-color: #28a745;
      color: white;
      padding: 10px 15px;
      text-decoration: none;
      font-weight: bold;
      float: right;
      margin: 10px 0;
    }}
  </style>
</head>
<body>
  <img src="https://infowordpress.s3.ap-south-1.amazonaws.com/wp-content/uploads/2023/02/03060918/unicommerce-logo.jpg" class="logo">
  <div class="top-right">
    <a href="/search" class="icon-link icon-search" title="Search">🔍</a>
    <a href="/delete" class="icon-link icon-delete" title="Delete">🗑</a>
    <a href="/view" class="icon-link icon-view" title="View">📋</a>
  </div>

  <h1> Weekly Client Dashboard</h1>

  <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx" target="_blank" class="download-button">
    Download Current Sheet
  </a>

  <form method="POST">
    <label>Tenant Code</label><input name="tenant_code" required>
    <label>Golive AM</label><input name="golive_am" required>

    <label>Go Live Mgr</label>
    <select name="golive_mgr" required>
      <option value="">-- Select Manager --</option>
      <option>Shubham varshney</option>
      <option>praneet singh</option>
      <option>ifrah sabir</option>
      <option>prakhar kesarwani</option>
    </select>

    <label>Status</label>
    <select name="status" required>
      <option value="">-- Select Status --</option>
      <option>wip</option>
      <option>uo</option>
      <option>Handover Pending</option>
      <option>On Hold</option>
      <option>Live</option>
    </select>

    <label>Dashboard Status</label>
    <select name="dashboard_status" required>
      <option value="">-- Select Status --</option>
      <option>DONE</option>
      <option>NOT REQUIRED</option>
      <option>PENDING</option>
    </select>

    <label>Remarks</label><textarea name="remarks" rows="3"></textarea>
    <button type="submit"> Submit Update</button>
  </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        worksheet = get_current_week_tab()
        data = [
            datetime.now().strftime('%Y-%m-%d'),
            request.form.get("tenant_code"),
            request.form.get("golive_am"),
            request.form.get("golive_mgr"),
            request.form.get("status"),
            request.form.get("dashboard_status"),
            request.form.get("remarks")
        ]
        worksheet.append_row(data)
        return "✅ Data submitted successfully! <a href='/'>Go back</a>"
    return render_template_string(form_html)

# ----------------------------- View Route -----------------------------
@app.route("/view")
def view():
    ws = get_current_week_tab()
    data = ws.get_all_values()
    html = "<h2>📋 Weekly Dashboard View</h2><table border='1' cellpadding='6'>"
    for i, row in enumerate(data):
        html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
    html += "</table><br><a href='/'>⬅ Back</a>"
    return html

# ----------------------------- Search Route -----------------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("tenant_code", "").strip().lower()
        ws = get_current_week_tab()
        data = ws.get_all_values()
        headers, rows = data[0], data[1:]
        results = [row for row in rows if query in row[1].lower()]  # Column 1 is Tenant Code
        html = "<h2>🔍 Search Results</h2><table border='1' cellpadding='6'><tr>"
        html += "".join([f"<th>{h}</th>" for h in headers]) + "</tr>"
        for r in results:
            html += "<tr>" + "".join([f"<td>{c}</td>" for c in r]) + "</tr>"
        html += "</table><br><a href='/search'>🔁 New Search</a> | <a href='/'>⬅ Back</a>"
        return html
    return '''
        <h2>🔍 Search Tenant Code</h2>
        <form method="POST">
            <input name="tenant_code" placeholder="Enter tenant code">
            <button type="submit">Search</button>
        </form>
        <br><a href="/">⬅ Back</a>
    '''

# ----------------------------- Delete Route -----------------------------
@app.route("/delete", methods=["GET", "POST"])
def delete():
    ws = get_current_week_tab()
    data = ws.get_all_values()
    headers, rows = data[0], data[1:]
    if request.method == "POST":
        index = int(request.form.get("row_index"))
        ws.delete_rows(index + 2)  # Skip header row + 0 index
        return redirect(url_for("delete"))

    html = "<h2>🗑 Delete Row</h2><form method='POST'>"
    html += "<select name='row_index'>"
    for i, row in enumerate(rows):
        html += f"<option value='{i}'>Row {i+1}: {row[1]} | {row[2]} | {row[4]}</option>"
    html += "</select><button type='submit'>Delete Selected Row</button></form>"
    html += "<br><a href='/'>⬅ Back</a>"
    return html

# ----------------------------- Run Flask -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
