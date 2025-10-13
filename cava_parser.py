import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import calendar
import tkinter as tk
from tkinter import filedialog
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# --- Ask user for the month and year ---
month = int(input("Ingrese el mes (1–12): "))
year = int(input("Ingrese el año (por ejemplo, 2025): "))

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

        if row[0].startswith(text_name_employee):
            if current_employee is not None:
                employees[current_employee] = {
                    "start": start_times,
                    "end": end_times
                }
            current_employee = row[8]
            start_times = []
            end_times = []

        elif text_start_time in row[0]:
            start_times = row[1:]

        elif text_end_time in row[0]:
            end_times = row[1:]

if current_employee is not None:
    employees[current_employee] = {
        "start": start_times,
        "end": end_times
    }

# --- BUILD DATAFRAME ---
report_rows = []
days_in_month = calendar.monthrange(year, month)[1]
regular_mandatory_hours=8
lunch_time = 1

dias_semana = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

for emp_id, data in employees.items():
    for day, (s, e) in enumerate(zip(data["start"], data["end"]), start=1):
        if day > days_in_month:
            continue

        total_hours = calc_hours(s, e)
        total_hours_str = f"{total_hours:.2f}".replace(".", ",")
        net_hours = max(total_hours - 1, 0)
        net_hours_str = f"{net_hours:.2f}".replace(".", ",")
        overtime_hours = 0 if net_hours == 0 else round(net_hours - 8, 2)
        # ✅ Convert to string with comma instead of dot
        overtime_str = f"{overtime_hours:.2f}".replace(".", ",")
        # ✅ Calculate the date and weekday
        date_obj = datetime(year, month, day)
        fecha_str = date_obj.strftime("%Y-%m-%d")
        weekday_es = dias_semana[date_obj.strftime("%A")]


        report_rows.append({
            "Nombre y Apellido": emp_id,
            "Fecha": fecha_str,
            "Día Semana": weekday_es,
            "Entrada": s,
            "Salida": e,
            "Horas mandatorias": regular_mandatory_hours,
            "Hora de Lunch": lunch_time,
            "Horas Trabajadas": total_hours,
            "Horas Netas": net_hours_str,
            "Horas diferencia (±)": overtime_str,
        })

# --- EXPORT ---
df = pd.DataFrame(report_rows)
df.to_csv("reporte_cava.csv", index=False, encoding='utf-8-sig')
print("✅ Archivo 'reporte_cava.csv' generado con éxito.")
