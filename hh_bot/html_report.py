""" Модуль генерации HTML отчета
    Используется когда найдено более 20 вакансий"""
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('view_vacancies.html')


def generate_html(vacancies):
    """ Генерация html файла с короткими описаниями вакансий """

    context = {
        "count": len(vacancies),
        "vacancies": vacancies
    }
    rendered_page = template.render(context)

    with open('report.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    return open('report.html', 'rb')
