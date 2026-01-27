import flet as ft
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'DejaVu Sans']

class DataManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.df = self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM properties", conn)
            conn.close()
            
            if df.empty:
                return pd.DataFrame(columns=['name', 'price', 'age', 'floor_plan'])
            
            return df
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()

    def get_kpi(self):
        if self.df.empty:
            return 0, 0, 0
        
        total_count = len(self.df)
        avg_price = self.df['price'].mean()
        avg_age = self.df['age'].mean()
        return total_count, avg_price, avg_age

    def get_price_by_floor_plan(self):
        if self.df.empty: return None
        return self.df.groupby('floor_plan')['price'].mean().reset_index().sort_values('price', ascending=False)

    def get_price_by_age(self):
        if self.df.empty: return None
        self.df['age_group'] = (self.df['age'] // 5) * 5
        grouped = self.df.groupby('age_group')['price'].mean().reset_index()
        return grouped

    def create_boxplot_image(self):
        """箱ひげ図のBase64画像を生成"""
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#2a2a2a')
        
        box_parts = ax.boxplot([self.df['price']], labels=['家賃'], patch_artist=True)
        for patch in box_parts['boxes']:
            patch.set_facecolor('#00a8ff')
        for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
            plt.setp(box_parts[element], color='#ffffff')
        
        ax.set_ylabel('家賃(円)', color='#ffffff')
        ax.set_title('家賃の分布（箱ひげ図）', color='#ffffff', fontsize=12)
        ax.tick_params(colors='#ffffff')
        ax.grid(True, alpha=0.2)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1e1e1e')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"

    def create_scatter_image(self):
        """散布図のBase64画像を生成"""
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#2a2a2a')
        
        ax.scatter(self.df['age'], self.df['price'], alpha=0.6, s=50, color='#ff6b6b')
        ax.set_xlabel('築年数(年)', color='#ffffff')
        ax.set_ylabel('家賃(円)', color='#ffffff')
        ax.set_title('築年数と家賃の関係', color='#ffffff', fontsize=12)
        ax.tick_params(colors='#ffffff')
        ax.grid(True, alpha=0.2)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1e1e1e')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"

    def create_histogram_image(self):
        """ヒストグラムのBase64画像を生成"""
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#2a2a2a')
        
        ax.hist(self.df['price'], bins=30, color='#00d4ff', edgecolor='#ffffff', alpha=0.7)
        ax.set_xlabel('家賃(円)', color='#ffffff')
        ax.set_ylabel('物件数', color='#ffffff')
        ax.set_title('家賃の分布（ヒストグラム）', color='#ffffff', fontsize=12)
        ax.tick_params(colors='#ffffff')
        ax.grid(True, alpha=0.2, axis='y')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1e1e1e')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"

def main(page: ft.Page):
    page.title = "新潟県長岡市 物件データ分析"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    dm = DataManager('suumo.db')
    
    if dm.df.empty:
        page.add(ft.Text("データがありません", color="red"))
        return

    total, avg_price, avg_age = dm.get_kpi()
    
    def create_kpi_card(title, value, emoji, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, color="grey"),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD)
            ], spacing=5),
            padding=20,
            bgcolor="#1e1e1e",
            border_radius=10,
            expand=True
        )

    kpi_row = ft.Row([
        create_kpi_card("物件総数", f"{total} 件", "🏢", "blue"),
        create_kpi_card("平均家賃", f"{avg_price/10000:.2f} 万円", "💰", "green"),
        create_kpi_card("平均築年数", f"{avg_age:.1f} 年", "📅", "orange"),
    ])

    df_floor = dm.get_price_by_floor_plan()
    df_age = dm.get_price_by_age()

    def create_table_rows(df):
        rows = []
        for index, row in df.iterrows():
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row['name'])),
                    ft.DataCell(ft.Text(f"{row['price']:,}")),
                    ft.DataCell(ft.Text(str(row['age']))),
                    ft.DataCell(ft.Text(row['floor_plan'])),
                ])
            )
        return rows

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("物件名")),
            ft.DataColumn(ft.Text("家賃(円)"), numeric=True),
            ft.DataColumn(ft.Text("築年数"), numeric=True),
            ft.DataColumn(ft.Text("間取り")),
        ],
        rows=create_table_rows(dm.df),
        border=ft.border.all(1, "#424242"),
        vertical_lines=ft.border.all(1, "#424242"),
        heading_row_color="#1a1a1a",
        width=1000
    )

    def on_sort_change(e):
        sort_key = sort_dropdown.value
        if sort_key == "price_desc":
            sorted_df = dm.df.sort_values('price', ascending=False)
        elif sort_key == "price_asc":
            sorted_df = dm.df.sort_values('price', ascending=True)
        elif sort_key == "age_new":
            sorted_df = dm.df.sort_values('age', ascending=True)
        elif sort_key == "age_old":
            sorted_df = dm.df.sort_values('age', ascending=False)
        else:
            sorted_df = dm.df
        
        data_table.rows = create_table_rows(sorted_df)
        page.update()

    sort_dropdown = ft.Dropdown(
        label="ソート",
        value="default",
        options=[
            ft.dropdown.Option("default", "デフォルト"),
            ft.dropdown.Option("price_desc", "家賃（高い順）"),
            ft.dropdown.Option("price_asc", "家賃（低い順）"),
            ft.dropdown.Option("age_new", "築年数（新しい順）"),
            ft.dropdown.Option("age_old", "築年数（古い順）"),
        ],
        width=200
    )

    def on_sort_button_click(e):
        on_sort_change(None)

    sort_button = ft.ElevatedButton(
        "ソート",
        on_click=on_sort_button_click
    )

    # グラフ画像を生成
    boxplot_image = dm.create_boxplot_image()
    scatter_image = dm.create_scatter_image()
    histogram_image = dm.create_histogram_image()

    page.add(
        ft.Text("新潟県長岡市 賃貸データ分析", size=30, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        kpi_row,
        ft.Divider(height=30, color="transparent"),
        
        ft.Text("データ分析グラフ", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Container(
                content=ft.Image(src=boxplot_image),
                expand=1,
                height=300,
                bgcolor="#1e1e1e",
                border_radius=10,
                padding=10
            ),
            ft.Container(
                content=ft.Image(src=scatter_image),
                expand=1,
                height=300,
                bgcolor="#1e1e1e",
                border_radius=10,
                padding=10
            ),
            ft.Container(
                content=ft.Image(src=histogram_image),
                expand=1,
                height=300,
                bgcolor="#1e1e1e",
                border_radius=10,
                padding=10
            ),
        ]),
        
        ft.Divider(height=30, color="transparent"),
        ft.Text("データ一覧", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([sort_dropdown, sort_button]),
        ft.Container(content=ft.Column([data_table], scroll=ft.ScrollMode.ADAPTIVE), height=400)
    )

if __name__ == "__main__":
    ft.app(target=main)