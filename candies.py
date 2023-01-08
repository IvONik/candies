import logging
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
candies = 50
step = 15

reply_keyboard = [['/play', '/rules'], # задается клавиатура, сколько строк, сколько кнопок в строке
                  ['/setting','/close' ]]


markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False) # передали список команд,
# one_time_keyboard=False чтобы клавиатура не закрывалась

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5938698218:AAE8PUol2UNv_vtXR8W9_8fduIky8vIA94s'


def start(update, context):
    name = f'{update.message.from_user.first_name} {update.message.from_user.last_name}' #вытягивает имя пользователя из телеграм
    update.message.reply_text(
        f"{name},давай сыграем. Выбери действие",
        reply_markup = markup #показать клавиатуру
    )

def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup = ReplyKeyboardRemove() # убрать клавиаутру
    )

def rules(update, context):
    update.message.reply_text(
        f"Каждый игрок берет количество конфет не больше {step}, кто возьмет последние конфеты, тот выиграл")


def setting(update, context):
    update.message.reply_text(
        "Определите количество разыгрываемых конфет. И максимально возмодное количество, которое можно взять за один ход")
    return 1


def set_setting(update, context):
    global candies # сделаем их global, чтобы другие функции могли их видеть
    global step
    candies, step = map(int,update.message.text.split()) #сделали int
    update.message.reply_text(
        'Правила установлены')
    return ConversationHandler.END #выход из диалога

def play(update, context):
    update.message.reply_text(
        f"Ваш ход. Какое количество конфет вы берете. Доступно {candies} конфет. "
        f"Максимальное количество {step}")#reply_markup=ReplyKeyboardRemove()) # убрираем клавиаутру
    return 1


def stop(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def play_step(update, context):
    global candies # т.к. ниже в функции мы меняем глобальную переменную candies, мы ее здесь объявляем
    candy = int(update.message.text)
    if candy > step:
        update.message.reply_text(f'Вы взяли слишком много ⛔, можно взять до {step} конфет! Попробуйте еще раз')
        return play_step()
    else:
        candies -= candy
    if candies <= step:
        update.message.reply_text('Я забираю, оставшиеся конфеты, Я победил! 🎉')
        reply_markup = markup #показать клавиатуру)
        return ConversationHandler.END
    else:
        n =  candies % (step+1)
        if 0 < n <= step:
            update.message.reply_text(
            f" Мой ход. доступно {candies} конфет. Я беру {n} конфет."
            f" Теперь {candies-n} конфет, выш ход")
        else:
            n = random.randint(1,step)
            update.message.reply_text(
                f" Мой ход. Доступно {candies} конфет. Я беру {n} конфет."
                f" Теперь {candies - n} конфет, выш ход")

    candies -= candies % (step+1)
    if candies <= step:
        update.message.reply_text('Поздравляю, ты победил!')
        reply_markup = markup #показать клавиатуру)
        return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    setting_handler = ConversationHandler(
        entry_points = [CommandHandler('setting', setting)],
        states = {
            1:[MessageHandler(Filters.text & ~Filters.command, set_setting)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    play_handler = ConversationHandler(
        entry_points = [CommandHandler('play', play)],
        states = {
            1:[MessageHandler(Filters.text & ~Filters.command, play_step)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("rules", rules))
    dp.add_handler(setting_handler)
    dp.add_handler(play_handler)
    dp.add_handler(CommandHandler("close", close_keyboard))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()