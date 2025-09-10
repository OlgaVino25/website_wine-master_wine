from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import datetime
import pandas
from collections import defaultdict


env = Environment(
    loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
)

template = env.get_template("template.html")

current_year = datetime.datetime.now().year
foundation_year = 1920
years = current_year - foundation_year


def get_year_word(years):
    if years % 10 == 1 and years % 100 != 1:
        return "год"
    elif 2 <= years % 10 <= 4 and (years % 100 < 10 or years % 100 >= 20):
        return "года"
    else:
        return "лет"


file_path = r"C:\DVMN\Layout\lesson_1\wine-master\website_wine-master_wine\wine2.xlsx"
excel_data_df = pandas.read_excel(
    io=file_path, sheet_name="Лист1", na_values="nan", keep_default_na=False
)

wines_list = excel_data_df.to_dict(orient="records")

grouped_wines = defaultdict(list)
for wine in wines_list:
    category = wine['Категория']
    grouped_wines[category].append(wine)

grouped_wines = dict(grouped_wines)
sorted_categories = sorted(grouped_wines.keys())


rendered_page = template.render(
    years=years, year_word=get_year_word(years), sorted_categories=sorted_categories, grouped_wines=grouped_wines
)


with open("index.html", "w", encoding="utf8") as file:
    file.write(rendered_page)


server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
server.serve_forever()
