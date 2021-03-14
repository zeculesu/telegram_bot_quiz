import telebot
from telebot import types
import json
import emoji
import random
from datetime import datetime
from api_key import api_key


bot = telebot.TeleBot(api_key)
file_info = json.load(open('info.json', encoding='utf-8'))
questions = file_info['questions']
number_quiz = 0
answer_exict, start_chat = False, False
count = []


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global answer_exict, number_quiz, count
    transition = ['Попробуй ещё', 'Неверно, увы', 'Не правильно', 'Подумай ещё', 'Нет, не так']
    if int(call.data.split(';')[1]) == number_quiz:
        correct_answer = file_info["answer"][str(number_quiz)][1]
        if call.data.split(';')[0] in correct_answer:
            answer_to_user = file_info["answer"][str(number_quiz)][0]
            bot.send_message(call.message.chat.id, answer_to_user)
            answer_exict = True
            if len(count) != number_quiz + 1:
                count.append(1)
            number_quiz += 1
        else:
            if len(count) != number_quiz + 1:
                count.append(0)
            bot.send_message(call.message.chat.id, random.choice(transition))


def make_key(question, num):
    keyboard = types.InlineKeyboardMarkup()
    question = random.sample(question, len(question))
    for i in range(len(question)):
        key = types.InlineKeyboardButton(text=question[i], callback_data=f"{question[i].split()[0]};{num}")
        keyboard.add(key)
    return keyboard


def quiz(message):
    global answer_exict
    global number_quiz, count, start_chat
    bot.send_message(message.from_user.id, "Начнём с простого")
    transition = ['Следующий вопрос:', 'Твой следующий вопрос:', 'Новый вопрос:', 'Лови следующий вопрос:']
    for i in range(len(questions)):
        if i != 0:
            bot.send_message(message.from_user.id, random.choice(transition))
        file_info["number_quiz"] = i
        keyboard = make_key(questions[list(questions.keys())[i]], i)
        bot.send_message(message.from_user.id, list(questions.keys())[i], reply_markup=keyboard)
        while not answer_exict:
            continue
        answer_exict = False
    while len(count) != len(questions):
        continue
    if len(count) == len(questions):
        bot.send_message(message.from_user.id, f"Это был последний вопрос, молодец! {emoji.emojize(':brain: ')}\n"
                                               f"Спасибо за отличную игру")
        bot.send_message(message.from_user.id, f'Ты правильно ответил на {sum(count)}/{len(questions)}')
        print(datetime.today().strftime('%d-%m-%Y %H:%M'))
        print(message.from_user.first_name, message.from_user.first_name)
        print(f'{sum(count)}/{len(questions)}')
        print('---------')
        number_quiz, count, start_chat = 0, [], False


def generate_keyboard(*answer):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in answer:
        button = types.KeyboardButton(item)
        keyboard.add(button)
    return keyboard


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global number_quiz, count, start_chat
    if start_chat:
        bot.send_message(message.from_user.id, "Вы не закончили прошлый квиз")
        return
    elif message.text == "/start":
        bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}! \n\n"
                                               f"Это квиз по интересным фактам из сферы IT 💡💡💡 \n"
                                               f"Всё что тебе понадобится для прохождения - смартфон 📱")
        keyboard = generate_keyboard('Да', 'Нет')
        bot.send_message(message.from_user.id, "Готов начать?", reply_markup=keyboard)
    elif message.text == 'Да' and not start_chat:
        bot.send_message(message.from_user.id, "Отлично!", reply_markup=types.ReplyKeyboardRemove())
        start_chat = True
        quiz(message)
    elif message.text == 'Нет' and not start_chat:
        bot.send_photo(message.from_user.id, open('img/sad.jpg', 'rb'))
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Чтобы начать - напиши: /start")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=0)
