import os
import argparse
import datetime
import pandas
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import defaultdict
from pathlib import Path


def get_year_word(years):
    if years % 10 == 1 and years % 100 != 11:
        return "год"
    elif 2 <= years % 10 <= 4 and (years % 100 < 10 or years % 100 >= 20):
        return "года"
    else:
        return "лет"


def load_wines_from_excel(file_path, sheet_name="Лист1"):
    """Загружает данные о винах из Excel файла и группирует их по категориям"""
    wines = load_wine_data(file_path, sheet_name)
    return group_wines_by_category(wines)


def load_wine_data(file_path, sheet_name):
    """Загружает данные о винах из Excel файла и возвращает список словарей"""
    excel_data_df = pandas.read_excel(
        io=file_path, sheet_name=sheet_name, na_values="nan", keep_default_na=False
    )
    return excel_data_df.to_dict(orient="records")


def group_wines_by_category(wines):
    """Группирует вина по категориям и возвращает отсортированные категории и сгруппированные данные"""
    grouped_wines = defaultdict(list)
    for wine in wines:
        category = wine["Категория"]
        grouped_wines[category].append(wine)

    grouped_wines = dict(grouped_wines)
    sorted_categories = sorted(grouped_wines.keys())

    return sorted_categories, grouped_wines


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Генерация сайта о винах из данных Excel"
    )
    parser.add_argument(
        "--file-path",
        default=os.getenv("WINE_DATA_PATH", "wine3.xlsx"),
        help="Путь к файлу Excel с данными о винах (по умолчанию: wine3.xlsx или переменная окружения WINE_DATA_PATH)",
    )
    parser.add_argument(
        "--sheet-name",
        default=os.getenv("WINE_SHEET_NAME", "Лист1"),
        help="Название листа в файле Excel (по умолчанию: Лист1 или переменная окружения WINE_SHEET_NAME)",
    )
    return parser.parse_args()


def main():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    current_year = datetime.datetime.now().year
    foundation_year = 1920
    years = current_year - foundation_year

    args = parse_arguments()

    file_path = Path(args.file_path)
    sorted_categories, grouped_wines = load_wines_from_excel(file_path, args.sheet_name)

    rendered_page = template.render(
        years=years,
        year_word=get_year_word(years),
        sorted_categories=sorted_categories,
        grouped_wines=grouped_wines,
    )

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
