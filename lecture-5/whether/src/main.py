import flet as ft
import requests
import json

def get_weather_emoji(weather_text):
    """天気テキストから対応する絵文字を返す関数"""
    weather_lower = weather_text.lower()
    
    if any(keyword in weather_lower for keyword in ["晴", "sunny", "clear"]):
        return "☀️"
    elif any(keyword in weather_lower for keyword in ["曇", "cloudy", "cloud"]):
        return "☁️"
    elif any(keyword in weather_lower for keyword in ["雨", "rain", "rainy"]):
        return "🌧️"
    elif any(keyword in weather_lower for keyword in ["雪", "snow"]):
        return "❄️"
    elif any(keyword in weather_lower for keyword in ["雷", "thunderstorm"]):
        return "⛈️"
    else:
        return "🌤️"

def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 700
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    page.bgcolor = "#f5f7fa"

    AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
    FORECAST_URL_BASE = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

    weather_display = ft.Column()
    loading_ring = ft.ProgressRing(visible=False)
    status_text = ft.Text("起動中...", size=14, color="#666666") 
    
    dropdown_area = ft.Dropdown(
        label="地域（都道府県）を選択",
        width=350,
        bgcolor="white",
        border_radius=8,
    )

    def get_weather(e):
        """天気を取得して表示する関数"""
        selected_code = dropdown_area.value
        if not selected_code:
            status_text.value = "地域が選択されていません"
            page.update()
            return

        # 画面リセット
        weather_display.controls.clear()
        loading_ring.visible = True
        status_text.value = f"データを取得中... (コード: {selected_code})"
        page.update()

        target_url = f"{FORECAST_URL_BASE}{selected_code}.json"

        try:
            print(f"URLにアクセスします: {target_url}")
            response = requests.get(target_url)
            response.raise_for_status()
            data = response.json()

            report = data[0]
            time_series = report["timeSeries"][0]
            time_defines = time_series["timeDefines"]
            areas = time_series["areas"]

            for area in areas:
                area_name = area["area"]["name"]
                weathers = area["weathers"]
                
                forecast_items = []
                for i, weather in enumerate(weathers):
                    if i < len(time_defines):
                        date_str = time_defines[i][:10]
                        weather_emoji = get_weather_emoji(weather)
                        
                        forecast_items.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(weather_emoji, size=32),
                                    ft.Column([
                                        ft.Text(date_str, size=14, color="#666666"),
                                        ft.Text(weather, size=16, weight=ft.FontWeight.BOLD, color="#1a1a1a"),
                                    ], spacing=2)
                                ], spacing=15, alignment=ft.MainAxisAlignment.START),
                                padding=12,
                                border_radius=8,
                                bgcolor="#ffffff",
                                margin=ft.margin.only(bottom=8)
                            )
                        )

                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Row([
                                    ft.Text("📍", size=24),
                                    ft.Text(area_name, size=20, weight=ft.FontWeight.BOLD, color="#0066cc"),
                                ], spacing=10),
                                padding=15,
                                bgcolor="#e8f4fd",
                                border_radius=8,
                                margin=ft.margin.only(bottom=10)
                            ),
                            ft.Divider(height=1, color="#dddddd"),
                            ft.Column(forecast_items, spacing=4)
                        ], spacing=10),
                        padding=15,
                    ),
                    elevation=3,
                    margin=ft.margin.only(bottom=15)
                )
                weather_display.controls.append(card)
            
            status_text.value = "取得完了"

        except Exception as ex:
            status_text.value = f"エラー: {ex}"
            print(f"Error: {ex}")
        
        loading_ring.visible = False
        page.update()

    search_button = ft.ElevatedButton(
        content=ft.Text("天気を見る", size=16, color="white"),
        icon="cloud_download",
        on_click=get_weather,
        bgcolor="#0066cc",
        width=150,
        height=50,
    )

    page.add(
        ft.Container(
            content=ft.Text("気象庁天気予報アプリ", size=28, weight="bold", color="#0066cc"),
            padding=10,
            margin=ft.margin.only(bottom=15)
        ),
        ft.Container(
            content=ft.Column([
                status_text,
                ft.Row([dropdown_area, search_button], spacing=10, alignment=ft.MainAxisAlignment.START),
            ], spacing=10),
            padding=15,
            bgcolor="white",
            border_radius=10,
            margin=ft.margin.only(bottom=15),
            shadow=ft.BoxShadow(blur_radius=5, color="#00000010")
        ),
        loading_ring,
        weather_display
    )
    page.update()

    try:
        status_text.value = "地域リストを読み込み中..."
        page.update()
        
        res = requests.get(AREA_URL)
        res.raise_for_status()
        data = res.json()
        offices = data.get("offices", {})
        
        options = []
        for code, info in offices.items():
            options.append(ft.dropdown.Option(key=code, text=info["name"]))
        
        dropdown_area.options = options
        status_text.value = "地域を選んで「天気を見る」を押してください"
        page.update()

    except Exception as e:
        status_text.value = f"地域リストの読み込みに失敗: {e}"
        status_text.color = "#ff0000"
        page.update()

ft.app(target=main)