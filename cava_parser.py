import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog
os.environ['TK_SILENCE_DEPRECATION'] = '1'

file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])

text_name_employee = "ID de persona"
text_start_time = "Registro de entrada"
text_end_time = "Registro de salida"

employees = {}
current_employee = None
start_times = []
end_times = []

def calc_hours(start, end):
    if start == "-" or end == "-":
        return 0
    fmt = "%H:%M:%S"
    try:
        t1 = datetime.strptime(start, fmt)
        t2 = datetime.strptime(end, fmt)
        if t2 < t1:  # Handles overnight shifts
            t2 += timedelta(days=1)
        return round((t2 - t1).total_seconds() / 3600, 2)
    except:
        return 0

with open(file_path, 'r', encoding='utf-8') as file:
    document = csv.reader(file)
    for row in document:
        if not row:
            continue

        # 🚨 Detect NEW employee block and SAVE previous one
        if row[0].startswith(text_name_employee):
            # ✅ Save previous employee before switching
            if current_employee is not None:
                employees[current_employee] = {
                    "start": start_times,
                    "end": end_times
                }

            # 🎯 Start new employee block
            current_employee = row[8]  # employee ID
            start_times = []
            end_times = []

        elif text_start_time in row[0]:
            start_times = row[1:]

        elif text_end_time in row[0]:
            end_times = row[1:]

# ✅ Save last employee after loop (important!)
if current_employee is not None:
    employees[current_employee] = {
        "start": start_times,
        "end": end_times
    }

# --- BUILD DATAFRAME ---
report_rows = []
for emp_id, data in employees.items():
    for day, (s, e) in enumerate(zip(data["start"], data["end"]), start=1):
        total_hours = calc_hours(s, e)   # raw hours (no lunch deduction yet)

        # ✅ Deduct 1 hour lunch if hours were actually worked
        net_hours = max(total_hours - 1, 0)

        # ✅ Split into normal vs overtime (keep decimals)
        overtime_hours = max(net_hours - 8, 0)

        report_rows.append({
            "Empleado": emp_id,
            "Dia": day,
            "Entrada": s,
            "Salida": e,
            "Total Horas": total_hours,
            "Horas Netas": net_hours,
            "Horas extra": overtime_hours
        })


df = pd.DataFrame(report_rows)

df.to_csv("reporte_cava.csv", index=False)
print("archivo generado con exito")
