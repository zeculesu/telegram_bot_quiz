import telebot
from telebot import types
import json
import emoji
import random
from datetime import datetime
from api_key import api_key

bot = telebot.TeleBot(api_key)
file_info_questions = json.load(open('info_questions.json', encoding='utf-8'))
file_info_user = json.load(open('info_users.json', encoding='utf-8'))
questions = file_info_questions['questions']


def update_json(id_user):
    file_info_user["id"][id_user] = {}
    file_info_user["id"][id_user]["number_quiz"] = 0
    file_info_user["id"][id_user]["answer_exict"] = False
    file_info_user["id"][id_user]["start_chat"] = False
    file_info_user["id"][id_user]["count"] = []
    with open('info_users.json', 'w') as file:
        json.dump(file_info_user, file)


def save_changes(file_info_user):
    with open('info_users.json', 'w') as file:
        json.dump(file_info_user, file)


def generate_keyboard(*answer):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in answer:
        button = types.KeyboardButton(item)
        keyboard.add(button)
    return keyboard


def make_key(question, num):
    keyboard = types.InlineKeyboardMarkup()
    question = random.sample(question, len(question))
    for i in range(len(question)):
        key = types.InlineKeyboardButton(text=question[i], callback_data=f"{question[i].split()[0]};{num}")
        keyboard.add(key)
    return keyboard


def quiz(message, id_user):
    bot.send_message(id_user, "Начнём с простого")
    transition = ['Следующий вопрос:', 'Твой следующий вопрос:', 'Новый вопрос:', 'Лови следующий вопрос:']
    count = file_info_user["id"][id_user]["count"]
    for i in range(len(questions)):
        if i != 0:
            bot.send_message(id_user, random.choice(transition))
        file_info_user["id"][id_user]["number_quiz"] = i
        keyboard = make_key(questions[list(questions.keys())[i]], i)
        bot.send_message(id_user, list(questions.keys())[i], reply_markup=keyboard)
        while not file_info_user["id"][id_user]["answer_exict"]:
            continue
        file_info_user["id"][id_user]["answer_exict"] = False
        save_changes(file_info_user)
    while len(count) != len(questions):
        continue
    if len(count) == len(questions):
        bot.send_message(id_user, f"Это был последний вопрос, молодец! {emoji.emojize(':brain: ')}\n"
                                  f"Спасибо за отличную игру")
        bot.send_message(id_user, f'Ты правильно ответил на {sum(count)}/{len(questions)} вопросов')
        print(datetime.today().strftime('%d-%m-%Y %H:%M'))
        print(message.from_user.first_name, message.from_user.first_name)
        print(f'{sum(count)}/{len(questions)}')
        print('---------')
        update_json(id_user)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    transition = ['Попробуй ещё', 'Неверно, увы', 'Не правильно', 'Подумай ещё', 'Нет, не так']
    id_user = call.message.chat.id
    number_quiz = file_info_user["id"][id_user]["number_quiz"]
    count = file_info_user["id"][id_user]["count"]
    if int(call.data.split(';')[1]) == number_quiz:
        correct_answer = file_info_questions["answer"][str(number_quiz)][1]
        if call.data.split(';')[0] in correct_answer:
            answer_to_user = file_info_questions["answer"][str(number_quiz)][0]
            bot.send_message(call.message.chat.id, answer_to_user)
            file_info_user["id"][id_user]["answer_exict"] = True
            if len(count) != number_quiz + 1:
                count.append(1)
            number_quiz += 1
        else:
            if len(count) != number_quiz + 1:
                count.append(0)
            bot.send_message(call.message.chat.id, random.choice(transition))
    save_changes(file_info_user)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    id_user = message.from_user.id
    if id_user in file_info_user['id']:
        if file_info_user["id"][id_user]["start_chat"]:
            bot.send_message(id_user, "Вы не закончили прошлый квиз")
            return
        elif message.text == "/start":
            bot.send_message(id_user, f"Привет, {message.from_user.first_name}! \n\n"
                                      f"Это квиз по интересным фактам из сферы IT 💡💡💡 \n"
                                      f"Всё что тебе понадобится для прохождения - смартфон 📱")
            keyboard = generate_keyboard('Да', 'Нет')
            bot.send_message(id_user, "Готов начать?", reply_markup=keyboard)
            update_json(id_user)
        elif message.text == 'Да':
            bot.send_message(id_user, "Отлично!", reply_markup=types.ReplyKeyboardRemove())
            file_info_user["id"][id_user]["start_chat"] = True
            with open('info_users.json', 'w') as f:
                json.dump(file_info_user, f)
            quiz(message, id_user)
        elif message.text == 'Нет':
            bot.send_photo(id_user, open('img/sad.jpg', 'rb'))
        elif message.text == "/help":
            bot.send_message(id_user, "Чтобы начать - напиши: /start")
        else:
            bot.send_message(id_user, "Я тебя не понимаю. Напиши /help.")
    else:
        if message.text == "/start":
            bot.send_message(id_user, f"Привет, {message.from_user.first_name}! \n\n"
                                      f"Это квиз по интересным фактам из сферы IT 💡💡💡 \n"
                                      f"Всё что тебе понадобится для прохождения - смартфон 📱")
            keyboard = generate_keyboard('Да', 'Нет')
            bot.send_message(id_user, "Готов начать?", reply_markup=keyboard)
            update_json(id_user)


bot.polling(none_stop=True, interval=0)
