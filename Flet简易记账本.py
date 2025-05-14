from typing import cast

import flet as ft
import datetime
import json
import os
from collections import defaultdict

from flet.core.textfield import KeyboardType


expenses = []
selected_month = "全部"
months = ["全部", "1月", "2月", "3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
DATA_FILE = "expenses.json"

def save_expenses():
    with open(DATA_FILE, "w",encoding="utf-8") as f:
        json.dump([
            {
                "名目": e["名目"],
                "金额": e["金额"],
                "分类": e["分类"],
                "日期": e["日期"].strftime('%Y-%m-%d')
            } for e in expenses
        ], cast('SupportsWrite[str]', f), ensure_ascii=False, indent=2)
        print("write ok...")

def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                expenses.append({
                    "名目": item["名目"],
                    "金额": item["金额"],
                    "分类": item["分类"],
                    "日期": datetime.datetime.strptime(item["日期"], '%Y-%m-%d').date()
                })


def main(page: ft.Page):
    def yes_click(e):
        page.close(confirm_dialog)
        page.window.prevent_close = False
        page.window.close()

    def no_click(e):
        page.close(confirm_dialog)
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("温馨提示"),
        content=ft.Text("是否想要退出程序？"),
        actions=[
            ft.ElevatedButton("是", on_click=yes_click),
            ft.OutlinedButton("否", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    def window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)
            page.update()

    page.window.prevent_close = True
    page.window.on_event = window_event
    page.window.height = 700
    page.window.width= 400
    page.window.center()
    page.window.visible = True
    page.title = "💸 简单记账本"
    #page.window.icon = r"test.ico"

    #支持中文本地化
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("zh", "CN"),
            ft.Locale("en", "US")
        ],
        current_locale=ft.Locale("zh", "CN")
    )
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    #page.window.height = 400
    #page.window.width = 800
    #page.window.center()
    load_expenses()

    title = ft.Text("💰 简单记账本", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN)

    dropdown = ft.Dropdown(
        label="选择月份",
        options=[ft.dropdown.Option(month) for month in months],
        value="全部",
        on_change=lambda e: [refresh_ui(), update_pie_chart()],
        width= 250
    )

    amount_input = ft.TextField(label="金额：", keyboard_type=KeyboardType.NUMBER, width=120)
    title_input = ft.TextField(label="名目：", width=160)
    category_input = ft.TextField(label="分类：", width=140)
    date_picker = ft.DatePicker(first_date=datetime.date(2023, 1, 1), last_date=datetime.date.today())
    page.overlay.append(date_picker)

    pie_chart = ft.PieChart(
        sections=[],
        sections_space=2,
        center_space_radius=80,
        expand=True
    )

    def update_pie_chart():
        month = dropdown.value
        category_totals = defaultdict(float)

        for exp in expenses:
            exp_month =  f"{exp["日期"].month}月"
            print(exp_month, month)
            if month == "全部" or exp_month == month:
                cat = exp["分类"]
                amt = exp["金额"]
                category_totals[cat] += amt

        pie_chart.sections = [
            ft.PieChartSection(
                value=amt,
                title=f"{cat}\n ¥{amt}",
                color=ft.Colors.CYAN if i % 2 == 0 else ft.Colors.TEAL
            )
            for i, (cat, amt) in enumerate(category_totals.items())
        ]

        pie_chart.update()


    def add_expense(e):
        if not amount_input.value or not title_input.value or not category_input.value or not date_picker.value:
            page.open(ft.SnackBar(ft.Text(f"请完整填写数据！"),duration = 1000,bgcolor=ft.Colors.RED_ACCENT))
            return

        expenses.append({
            "名目": title_input.value,
            "金额": float(amount_input.value),
            "分类": category_input.value,
            "日期": date_picker.value
        })

        save_expenses()
        amount_input.value = title_input.value = category_input.value = ""
        refresh_ui()
        update_pie_chart()
        page.open(ft.SnackBar(ft.Text(f"添加成功！"), duration=1000, bgcolor=ft.Colors.GREEN_ACCENT))

    def delete_expense(index):
        expenses.pop(index)
        save_expenses()
        refresh_ui()
        update_pie_chart()

    add_button = ft.ElevatedButton("➕ 添加记录", on_click=add_expense, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    input_row = ft.ResponsiveRow([
        title_input,
        amount_input,
        category_input,
        ft.ElevatedButton("📅 选择日期", on_click=lambda _: page.open(date_picker)),
        add_button
    ], spacing=10, run_spacing=10)

    total_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER)
    expense_list = ft.Column()
    category_bars = ft.Column()

    def refresh_ui():
        month = dropdown.value
        filtered = []
        total = 0
        chart_data = defaultdict(float)
        for idx, exp in enumerate(expenses):
            exp_month = f"{exp["日期"].month}月"
            if month == "全部" or exp_month == month:
                filtered.append((idx, exp))
                total += exp["金额"]
                chart_data[exp["分类"]] += exp["金额"]

        category_bars.controls.clear()
        for cat, amount in chart_data.items():
            percent = (amount / total) if total else 0
            category_bars.controls.append(
                ft.Column([
                    ft.Text(f"{cat} - ¥{amount:.2f} ({percent*100:.1f}%)"),
                    ft.ProgressBar(value=percent, color=ft.Colors.LIGHT_BLUE_ACCENT)
                ])
            )

        expense_list.controls.clear()
        for idx, exp in filtered:
            card = ft.Card(
                ft.Container(
                    ft.Row([
                        ft.Column([
                            ft.Text(exp["名目"], weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                            ft.Text(f"¥{exp['金额']} | {exp['分类']} | {exp['日期'].year}年{exp['日期'].month}月{exp['日期'].day}日", color=ft.Colors.BLACK)
                        ], spacing=5),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, i=idx: delete_expense(i), icon_color=ft.Colors.RED_ACCENT)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=3,
                color=ft.Colors.with_opacity(0.85, ft.Colors.LIGHT_BLUE_300),
                shape=ft.RoundedRectangleBorder(radius=10)
            )
            expense_list.controls.append(card)

        total_text.value = f"总计 {month}: 💴{total:.2f}"
        page.update()

    # Final layout
    page.add(
        ft.Column([
            title,
            dropdown,
            input_row,
            total_text,
            ft.Container(content=pie_chart, width=400, height=400),
            ft.Divider(),
            category_bars,
            ft.Divider(),
            expense_list
        ])
    )

    refresh_ui()
    update_pie_chart()

ft.app(target=main)
