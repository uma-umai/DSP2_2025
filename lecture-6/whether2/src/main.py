import flet as ft
import requests
import sqlite3
from datetime import datetime

class WeatherDB:
    def __init__(self, db_name="weather_cache.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS areas (
                    code TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_code TEXT,
                    sub_area_name TEXT,
                    forecast_date TEXT,
                    weather_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_areas(self, offices):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            for code, info in offices.items():
                cursor.execute("INSERT OR REPLACE INTO areas (code, name) VALUES (?, ?)", (code, info["name"]))
            conn.commit()

    def save_forecast(self, area_code, sub_area_name, forecast_date, weather_text):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO forecasts (area_code, sub_area_name, forecast_date, weather_text)
                VALUES (?, ?, ?, ?)
            """, (area_code, sub_area_name, forecast_date, weather_text))
            conn.commit()

    def get_forecasts_by_date(self, area_code, target_date):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sub_area_name, forecast_date, weather_text 
                FROM forecasts 
                WHERE area_code = ? AND forecast_date = ?
                ORDER BY created_at DESC
            """, (area_code, target_date))
            return cursor.fetchall()

    def get_latest_forecasts(self, area_code):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sub_area_name, forecast_date, weather_text 
                FROM forecasts 
                WHERE area_code = ? 
                ORDER BY created_at DESC
            """, (area_code,))
            return cursor.fetchall()

def get_weather_emoji(weather_text):
    weather_lower = weather_text.lower()
    if any(keyword in weather_lower for keyword in ["晴", "sunny", "clear"]): return "☀️"
    elif any(keyword in weather_lower for keyword in ["曇", "cloudy", "cloud"]): return "☁️"
    elif any(keyword in weather_lower for keyword in ["雨", "rain", "rainy"]): return "🌧️"
    elif any(keyword in weather_lower for keyword in ["雪", "snow"]): return "❄️"
    elif any(keyword in weather_lower for keyword in ["雷", "thunderstorm"]): return "⛈️"
    else: return "🌤️"

def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ (過去検索対応版)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 900
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#f5f7fa"

    db = WeatherDB()
    AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
    FORECAST_URL_BASE = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

    weather_display = ft.Column()
    status_text = ft.Text("地域を選択してください", size=14, color="#666666")
    loading_ring = ft.ProgressRing(visible=False)
    dropdown_area = ft.Dropdown(label="地域を選択", width=350, bgcolor="white", border_radius=8)
    
    selected_date_text = ft.Text("表示日: 未選択 (最新を表示)", size=16, weight="bold")

    def display_data(rows):
        weather_display.controls.clear()
        if not rows:
            weather_display.controls.append(ft.Text("指定された条件のデータが見つかりません。", color="red"))
            page.update()
            return

        displayed_combos = set()
        sub_areas = {}
        for sub_name, date, weather in rows:
            if sub_name not in sub_areas:
                sub_areas[sub_name] = []
            
            combo = f"{sub_name}_{date}"
            if combo not in displayed_combos:
                sub_areas[sub_name].append({"date": date, "weather": weather})
                displayed_combos.add(combo)

        for sub_name, forecasts in sub_areas.items():
            items = []
            for f in forecasts:
                emoji = get_weather_emoji(f['weather'])
                items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(emoji, size=30),
                            ft.Column([
                                ft.Text(f['date'], size=12, color="#666666"),
                                ft.Text(f['weather'], size=14, weight="bold"),
                            ], spacing=1)
                        ]),
                        padding=10, bgcolor="#f9f9f9", border_radius=5
                    )
                )
            weather_display.controls.append(
                ft.Card(ft.Container(ft.Column([
                    ft.Text(f"📍 {sub_name}", size=18, weight="bold", color="#0066cc"),
                    ft.Divider(),
                    ft.Column(items)
                ]), padding=15))
            )
        page.update()

    def on_date_change(e):
        selected_date_text.value = f"表示日: {date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2024, 1, 1),
        last_date=datetime(2030, 12, 31),
        value=datetime.now(),
    )
    page.overlay.append(date_picker)

    def on_get_latest_click(e):
        selected_code = dropdown_area.value
        if not selected_code: return
        loading_ring.visible = True
        page.update()
        try:
            res = requests.get(f"{FORECAST_URL_BASE}{selected_code}.json")
            data = res.json()
            report = data[0]
            time_defines = report["timeSeries"][0]["timeDefines"]
            count = 0
            for area_info in report["timeSeries"][0]["areas"]:
                sub_name = area_info["area"]["name"]
                for i, weather in enumerate(area_info["weathers"]):
                    if i < len(time_defines):
                        db.save_forecast(selected_code, sub_name, time_defines[i][:10], weather)
                        count += 1
            status_text.value = f"✓ {count}件のデータを取得・保存しました ({datetime.now().strftime('%H:%M:%S')})"
            selected_date_text.value = "表示日: 最新データ"
            display_data(db.get_latest_forecasts(selected_code))
        except Exception as ex:
            status_text.value = f"取得失敗: {str(ex)}"
            display_data(db.get_latest_forecasts(selected_code))
        loading_ring.visible = False
        page.update()

    def on_view_history_click(e):
        selected_code = dropdown_area.value
        if not selected_code or not date_picker.value:
            status_text.value = "地域と日付を両方選択してください"
            page.update()
            return
        
        target = date_picker.value.strftime('%Y-%m-%d')
        status_text.value = f"{target} の記録を検索中..."
        display_data(db.get_forecasts_by_date(selected_code, target))

    row_buttons = ft.Row([
        ft.ElevatedButton("最新を取得", icon="refresh", on_click=on_get_latest_click, bgcolor="#0066cc", color="white"),
        ft.ElevatedButton("カレンダーを開く", icon="calendar_month", on_click=lambda _: open_date_picker()),
        ft.ElevatedButton("過去を表示", icon="history", on_click=on_view_history_click),
    ], wrap=True)

    def open_date_picker():
        date_picker.open = True
        page.update()

    page.add(
        ft.Text("気象庁天気予報 (過去データ閲覧対応)", size=24, weight="bold", color="#0066cc"),
        ft.Row([dropdown_area]),
        row_buttons,
        selected_date_text,
        status_text,
        loading_ring,
        weather_display
    )

    try:
        res = requests.get(AREA_URL)
        offices = res.json().get("offices", {})
        db.save_areas(offices)
        dropdown_area.options = [ft.dropdown.Option(key=code, text=info["name"]) for code, info in offices.items()]
        page.update()
    except:
        status_text.value = "エリア取得エラー。"

ft.app(target=main)