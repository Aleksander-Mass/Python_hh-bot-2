""" Основной модуль программы отвечающий за работу бота """
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import config
from headhunter import HeadHunter
from html_report import generate_html


def telegram_bot(token):
    """
    Основная функция бота, где происходит обработка начинающей функции "/start"
    И остальных строковых команд с обращениями к модулям
    """
    bot = telebot.TeleBot(token)
    hh = HeadHunter()
    # подтягиваем из файла config.py параметры поиска вакансий которые будем заполнять значениями в ходе общения с
    # пользователем
    search_params = config.search_params

    @bot.message_handler(commands=["start"])
    def start_message(message):
        """Функция запускается, в случае, если пользователь выбрал команду /start"""
        welcome_message = f"Добро пожаловать {message.from_user.first_name}! Здесь вы можете удобно искать вакансии " \
                          f"на <b>Head Hunter</b>"
        bot.send_message(message.chat.id, welcome_message, parse_mode='HTML')

        answer = bot.send_message(message.chat.id, "Включаю режим увлекательной беседы!\nНа какую "
                                                   "профессию/должность вы планируете найти работу?\n<i>Пример "
                                                   "сообщения: программист</i>", parse_mode='HTML')
        search_params['text'] = None
        search_params['employer_id'] = None
        # вызываем функцию get_profession, в которой будем обрабатывать ответ пользователя
        bot.register_next_step_handler(answer, get_profession)

    @bot.message_handler(commands=['help'])
    def bot_help(message):
        """Функция для вывода основных команд:
        запускается, в случае, если пользователь выбрал команду /help"""
        text = [f'/{command} - {desk}' for command, desk in config.DEFAULT_COMMANDS]
        bot.send_message(message.from_user.id, 'Бот является учебным проектом. Создатель - Alexander Mass')
        bot.send_message(message.from_user.id, '\n'.join(text))

    def get_profession(message):
        """ Получает от пользователя выбранную профессию/сферу труда
         Запрашивает у пользователя город"""
        search_params['text'] = message.text
        bot.send_message(message.chat.id,
                         'Для вывода интересующей вас информации мне понадобится кое-что уточнить:')
        answer = bot.send_message(message.chat.id, 'Введите название города, в котором ищете работу')
        bot.register_next_step_handler(answer, city_selection_buttons)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
    def get_salary(call):
        """Получает нажатую пользователем кнопку с городом
        Запрашивает у пользователя размер зароботной платы"""
        search_params['area'] = call.data.split('_')[1]
        answer = bot.send_message(call.message.chat.id, "Введите размер желаемой зарплаты в рублях\n<i>Пример "
                                                   "сообщения: 500000</i>", parse_mode='HTML')
        bot.register_next_step_handler(answer, get_experience)

    def get_experience(message):
        """Получает данные о желаемой зарплате пользователя
         Запрашивает у пользователя опыт работы"""
        if message.text.isdigit():
            search_params['salary'] = message.text
        destinations = InlineKeyboardMarkup()
        list_experiences = hh.get_experience()
        for experience in list_experiences:
            destinations.add(InlineKeyboardButton(text=experience['name'],
                                                  callback_data=f"experience_{experience['id']}",
                                                  resize_keyboard=True))

        bot.send_message(message.chat.id, 'Укажите ваш опыт работы', reply_markup=destinations)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('experience'))
    def get_employment(call):
        """Получает нажатую пользователем кнопку об опыте работы
           Запрашивает у пользователя тип занятости"""
        search_params['experience'] = call.data.split('_')[1]
        destinations = InlineKeyboardMarkup()
        list_employments = hh.get_employment()
        for employment in list_employments:
            destinations.add(InlineKeyboardButton(text=employment['name'],
                                                  callback_data=f"employment_{employment['id']}",
                                                  resize_keyboard=True))

        bot.send_message(call.message.chat.id, 'Укажите тип занятости', reply_markup=destinations)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('employment'))
    def get_schedule(call):
        """Получает нажатую пользователем кнопку о типе занятости
           Запрашивает у пользователя график работы"""
        search_params['employment'] = call.data.split('_')[1]
        destinations = InlineKeyboardMarkup()
        list_schedules = hh.get_schedule()
        for schedule in list_schedules:
            destinations.add(InlineKeyboardButton(text=schedule['name'],
                                                  callback_data=f"schedule_{schedule['id']}",
                                                  resize_keyboard=True))

        bot.send_message(call.message.chat.id, 'Укажите график работы', reply_markup=destinations)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule'))
    def get_employers(call):
        """Получает нажатую пользователем кнопку о графике работы
           Запрашивает у пользователя информацию о работодателе"""
        search_params['schedule'] = call.data.split('_')[1]
        bot.send_message(call.message.chat.id,
                         'Осталось совсем немного:')

        bot.send_message(call.message.chat.id, 'Вас интересует какая-то конкретная '
                                                        'компания?', reply_markup=select_yes_no())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer'))
    def search(call):
        """Получает нажатую пользователем кнопку о работодателе
           После чего запускает поиск вакансий"""
        search_params['employer_id'] = call.data.split('_')[1]
        get_vacancies(call)

    @bot.callback_query_handler(func=lambda call: call.data == "Yes")
    def select_employer(call):
        """Срабатывает если пользователь нажал Да на вопрос о конкретной компании """
        answer = bot.send_message(call.message.chat.id,
                                  'Введите название компании:')

        bot.register_next_step_handler(answer, choosing_employers_buttons)

    @bot.callback_query_handler(func=lambda call: call.data == "No")
    def get_vacancies(call):
        """Поиск вакансий"""
        sticker_id = 'CAACAgIAAxkBAAEJwfhkukTyUXr9IVR6I-G1NMcPOFpyoAACVQADr8ZRGmTn_PAl6RC_LwQ'
        bot.send_message(call.message.chat.id, 'Запускаю поиск вакансий')
        bot.send_sticker(chat_id=call.message.chat.id, sticker=sticker_id)
        print('search params:', search_params)
        vacancies = hh.get_vacancies(search_params)
        print('count found vacancies:', len(vacancies))
        if len(vacancies) > 20:
            bot.send_message(call.message.chat.id, 'Найдено более 20 вакансий, формирую отчет')
            html_file = generate_html(vacancies)
            bot.send_document(chat_id=call.message.chat.id, document=html_file)
        elif len(vacancies) == 0:
            bot.send_message(call.message.chat.id, 'Ничего не найдено')
        else:
            bot.send_message(call.message.chat.id, f'Найдено {len(vacancies)} вакансий')
            for vacancy in vacancies:
                bot.send_message(call.message.chat.id, str(vacancy))

    def city_selection_buttons(message):
        """Функция для вывода кнопок
           Создает кнопки с названиями городов/регионов/областей
           принимает сообщение с названием города
           выводит кнопки с :
               text= 'Название города',
               callback_data= f'id города'
           Возвращает кнопки в столбик"""
        keyword = message.text.strip().lower()
        areas = hh.get_areas()
        destinations = InlineKeyboardMarkup()
        for area in areas:
            city_name = area['city_name']
            city_id = area['city_id']
            if keyword == city_name.lower() or keyword in city_name.lower():
                destinations.add(InlineKeyboardButton(text=city_name,
                                                      callback_data=f"city_{city_id}",
                                                      resize_keyboard=True))
        if len(destinations.keyboard):
            bot.send_message(message.chat.id, 'Уточните, пожалуйста:',
                             reply_markup=destinations)
        else:
            bot.send_message(message.chat.id, f'У меня нет информации о городе: {message.text}')
            answer = bot.send_message(message.chat.id, 'Введите название города, в котором ищете работу')
            bot.register_next_step_handler(answer, city_selection_buttons)


    def choosing_employers_buttons(message):
        """Функция для вывода кнопок
        Создает кнопки с названиями компаний
        принимает название компании
           выводит кнопки с :
               text= 'Название компании',
               callback_data= f'id компании'
           Возвращает кнопки в столбик
        """
        employers = hh.get_employers(message.text, search_params['area'])
        destinations = InlineKeyboardMarkup()
        for employer in employers:
            employer_name = employer['employer_name']
            employer_id = employer['employer_id']
            destinations.add(InlineKeyboardButton(text=employer_name,
                                                  callback_data=f"employer_{employer_id}",
                                                  resize_keyboard=True))
        if len(destinations.keyboard):
            bot.send_message(message.chat.id, 'Уточните, пожалуйста:',
                             reply_markup=destinations)
        else:
            bot.send_message(message.chat.id, f'У меня нет информации о работодателе: {message.text}')
            sticker_id = 'CAACAgIAAxkBAAEJx_xkvODet0HzX7e0BSYBLo4Mt8pG0wACIQEAAvcCyA9E9UdZozFIri8E'
            bot.send_sticker(message.chat.id, sticker=sticker_id)
            bot.send_message(message.chat.id, 'Попробуем еще раз найти компанию?', reply_markup=select_yes_no())

    def select_yes_no():
        """Функция для вывода кнопок
        Создает кнопки с текстом Да, Нет
        Возвращает кнопки в одну линию
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Да', callback_data='Yes'),
                     InlineKeyboardButton('Нет', callback_data='No'))
        return keyboard

    bot.polling()
