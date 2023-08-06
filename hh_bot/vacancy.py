from dataclasses import dataclass


@dataclass
class Vacancy:
    id: str
    url: str
    name: str
    employer_name: str
    salary_from: int
    salary_to: int
    description: str
    requirements: str

    def __str__(self):
        specification = f'''Должность - {self.name}
            Обязанности - {self.description}
            Компания - {self.employer_name}
            Требования - {self.requirements}
            Зарплата:
                От: {self.salary_from}
                До: {self.salary_to}
            Сcылка - {self.url}'''

        specification = specification.replace('None', 'Не указана')
        return specification


