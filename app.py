from flask import Flask, request, render_template_string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

app = Flask(__name__)

# Google Sheets Setup
import json
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)


SHEET_NAME = "Weekly Client Dashboard"
HEADERS = [
    "Tenant Name", "Tenant Code", "Golive AM", "Go Live Mgr",
    "Current Status", "Dashboard Status", "Remarks"
]

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

SHEET_ID = "1m57mjkgMr1JLrpPapV-pNOZva-8zeY_8wtJlyFbbhQQ"

# ----------------------------- Home Form -----------------------------
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
    h1 {{
      text-align: center;
      color: #003366;
    }}
    .logo {{
      position: absolute;
      left: 20px;
      top: 10px;
      height: 40px;
    }}
    .top-right {{
      position: absolute;
      top: 20px;
      right: 20px;
    }}
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
    input, textarea {{
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
    <a href="/search" target="_blank" class="icon-link icon-search" title="Search">🔍</a>
    <a href="/delete" target="_blank" class="icon-link icon-delete" title="Delete">🗑</a>
    <a href="/view" target="_blank" class="icon-link icon-view" title="View">📋</a>
  </div>

  <h1> Weekly Client Dashboard</h1>

  <a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx" target="_blank" class="download-button">
    Download Current Sheet
  </a>

  <form method="POST">
    <label>Tenant Name</label><input name="tenant_name" required>
    <label>Tenant Code</label><input name="tenant_code" required>
    <label>Golive AM</label><input name="golive_am" required>
    <label>Go Live Mgr</label><input name="golive_mgr" required>
    <label>Status</label><input name="status" required>
    <label>Dashboard Status</label><input name="dashboard_status" required>
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
            request.form.get("tenant_name"),
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

# ----------------------------- Search -----------------------------
@app.route("/search", methods=["GET", "POST"])
def search_page():
    if request.method == "POST":
        tenant_code = request.form.get("tenant_code_search").strip().lower()
        spreadsheet = client.open(SHEET_NAME)
        all_sheets = spreadsheet.worksheets()

        matches = []
        for sheet in all_sheets:
            data = sheet.get_all_records()
            for row in data:
                if row["Tenant Code"].strip().lower() == tenant_code:
                    row["Sheet Name"] = sheet.title
                    matches.append(row)

        if not matches:
            return f"""
            <html><head><style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; padding: 30px; }}
            h3 {{ color: #dc3545; }}
            a {{ display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            </style></head><body>
            <h3>❗No record found for Tenant Code: {tenant_code}</h3>
            <a href='/search'>🔁 Try again</a>
            </body></html>
            """

        html = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>🔍 Search Results</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, sans-serif;
                background-color: #f4f6f9;
                padding: 30px;
                margin: 0;
            }}
            h2 {{
                text-align: center;
                color: #003366;
            }}
            .table-container {{
                overflow-x: auto;
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 1000px;
            }}
            thead {{
                background-color: #003366;
                color: white;
            }}
            th, td {{
                text-align: left;
                padding: 12px 16px;
                border-bottom: 1px solid #e0e0e0;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .back-btn {{
                display: inline-block;
                margin-top: 20px;
                background-color: #007bff;
                color: white;
                padding: 10px 18px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
            }}
            .back-btn:hover {{
                background-color: #0056b3;
            }}
        </style>
        </head>
        <body>
            <h2>🔍 Search Results for Tenant Code: <i>{}</i></h2>
            <div class="table-container">
                <table>
                    <thead><tr><th>Sheet</th>{}</tr></thead>
                    <tbody>{}</tbody>
                </table>
            </div>
            <div style="text-align:center;">
                <a href="/search" class="back-btn">🔁 Search Again</a>
            </div>
        </body>
        </html>
        """.format(
            tenant_code,
            "".join(f"<th>{h}</th>" for h in HEADERS),
            "\n".join("<tr><td>{}</td>{}</tr>".format(
                row["Sheet Name"],
                "".join(f"<td>{row.get(h, '')}</td>" for h in HEADERS)
            ) for row in matches)
        )
        return html

    return """
    <!DOCTYPE html>
    <html>
    <head>
    <title>🔍 Search Tenant</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f6f9;
            padding: 40px;
        }
        h2 {
            color: #003366;
            text-align: center;
        }
        form {
            max-width: 500px;
            margin: 40px auto;
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }
        label {
            font-weight: 600;
        }
        input {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
    </head>
    <body>
        <h2>🔍 Search Tenant Entry (Across All Weeks)</h2>
        <form method="POST">
          <label>Tenant Code</label>
          <input name="tenant_code_search" required>
          <button type="submit">🔍 Search</button>
        </form>
    </body>
    </html>
    """

# ----------------------------- Delete -----------------------------
@app.route("/delete", methods=["GET", "POST"])
def delete_page():
    if request.method == "POST":
        tenant_code = request.form.get("tenant_code_delete").strip().lower()
        worksheet = get_current_week_tab()
        all_data = worksheet.get_all_values()

        deleted = False
        for idx, row in enumerate(all_data[1:], start=2):
            if len(row) >= 2 and row[1].strip().lower() == tenant_code:
                worksheet.delete_rows(idx)
                deleted = True
                break

        if deleted:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>✅ Deleted</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', sans-serif;
                        background-color: #f4f6f9;
                        padding: 40px;
                        text-align: center;
                    }}
                    .msg {{
                        background-color: #d4edda;
                        color: #155724;
                        padding: 20px;
                        border-radius: 8px;
                        display: inline-block;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        text-decoration: none;
                        color: white;
                        background-color: #dc3545;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-weight: bold;
                    }}
                    a:hover {{
                        background-color: #c82333;
                    }}
                </style>
            </head>
            <body>
                <div class="msg">
                    <h3>✅ Entry with Tenant Code '<i>{tenant_code}</i>' deleted.</h3>
                </div><br>
                <a href='/delete'>🗑 Delete Another</a>
            </body>
            </html>
            """

        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>❌ Not Found</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', sans-serif;
                        background-color: #f4f6f9;
                        padding: 40px;
                        text-align: center;
                    }}
                    .msg {{
                        background-color: #f8d7da;
                        color: #721c24;
                        padding: 20px;
                        border-radius: 8px;
                        display: inline-block;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        text-decoration: none;
                        color: white;
                        background-color: #007bff;
                        padding: 10px 20px;
                        border-radius: 6px;
                        font-weight: bold;
                    }}
                    a:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="msg">
                    <h3>❌ No entry found for Tenant Code '<i>{tenant_code}</i>'.</h3>
                </div><br>
                <a href='/delete'>🔁 Try Again</a>
            </body>
            </html>
            """

    # GET request (show the delete form)
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <title>🗑 Delete Tenant</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f6f9;
            padding: 40px;
        }
        h2 {
            color: #003366;
            text-align: center;
        }
        form {
            max-width: 500px;
            margin: 40px auto;
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }
        label {
            font-weight: 600;
        }
        input {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        button {
            background-color: #dc3545;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #c82333;
        }
    </style>
    </head>
    <body>
        <h2>🗑 Delete Tenant Entry (Current Week Only)</h2>
        <form method="POST">
          <label>Tenant Code</label>
          <input name="tenant_code_delete" required>
          <button type="submit">🗑 Delete</button>
        </form>
    </body>
    </html>
    """


# ----------------------------- View (Professional Style) -----------------------------
@app.route("/view")
def view_page():
    
    worksheet = get_current_week_tab()
    all_data = worksheet.get_all_values()

    if len(all_data) <= 1:
        return "<h3>📭 No data found for current week.</h3><a href='/'>Go Home</a>"

    headers = all_data[0]
    rows = all_data[1:]

    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>📋 Weekly Dashboard View</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background-color: #f4f6f9;
            padding: 30px;
            margin: 0;
        }}
        h2 {{
            text-align: center;
            color: #003366;
        }}
        .table-container {{
            overflow-x: auto;
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 1000px;
        }}
        thead {{
            background-color: #003366;
            color: white;
        }}
        th, td {{
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .back-btn {{
            display: inline-block;
            margin-top: 20px;
            background-color: #007bff;
            color: white;
            padding: 10px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
        }}
        .back-btn:hover {{
            background-color: #0056b3;
        }}
    </style>
    </head>
    <body>
        <h2>📋 Client Dashboard – {}</h2>
        <div class="table-container">
            <table>
                <thead><tr>{}</tr></thead>
                <tbody>{}</tbody>
            </table>
        </div>
        <div style="text-align:center;">
            <a href="/" class="back-btn">⬅ Back to Dashboard</a>
        </div>
    </body>
    </html>
    """.format(
        worksheet.title,
        "".join(f"<th>{h}</th>" for h in headers),
        "\n".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    )

    return html

# ----------------------------- Run -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
