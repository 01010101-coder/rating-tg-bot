import telebot as tb
from settings import TOKEN, MAFIA_ID
from functions import *

if __name__ == '__main__':
    bot = tb.TeleBot(TOKEN)

    @bot.message_handler(commands=['help'])
    def handle_start(message):
        text = "/rating - топ-10\n/my_rating - ваш рейтинг\n/statistics - статистика по играм"
        bot.send_message(message.chat.id, text)

    @bot.message_handler(commands=['true_rating'])
    def handle_rating(message):
        top = get_rating()
        text = ""
        for i in range(len(top)):
            text += f"{i + 1}. {top[i][0]} - {top[i][1]}\n"
        bot.send_message(message.chat.id, text)

    @bot.message_handler(commands=['my_rating'])
    def handle_my_rating(message):
        user = bot.get_chat_member(message.chat.id, message.from_user.id)
        if user.user.last_name is None:
            username = f"{user.user.first_name}"
        else:
            username = f"{user.user.first_name} {user.user.last_name}"
        result = set_user_id(user, username)
        if result == -1:
            bot.send_message(message.chat.id, "Пользователь не найден")
        else:
            list = get_my_rating(username)
            game_count = list[1] + list[2]
            if game_count == 0:
                villag_proc = 0
                mafia_proc = 0
            else:
                villag_proc = round(list[3] / game_count * 100, 1)
                mafia_proc = round(list[4] / game_count * 100, 1)
            text = f"Рейтинг {username}: {list[0]}\nкол-во игр: {game_count}\nмирных побед: {villag_proc}%\nмаф побед: {mafia_proc}%"
            bot.reply_to(message, text)

    @bot.message_handler(commands=['statistics'])
    def hadle_statistics(message):
        game_count, villager_wins, mafia_wins, average_players = get_statistics()
        text = (f"Кол-во игр: {game_count}\nПроцент мирных побед: {villager_wins/game_count * 100}%\nПроцент маф побед: {mafia_wins/game_count * 100}%\n"
                f"Среднее кол-во игроков в игре: {average_players}")
        bot.reply_to(message, text)

    @bot.message_handler(commands=['update_rating'])
    def handle_update_rating(message):
        if message.from_user.id in MAFIA_ID:
            print(message.text)
            words = message.text.split()
            print(words)
            try:
                result = update_user_rating(words[1], words[2])
                if result == 1:
                    bot.send_message(message.chat.id, "Рейтинг обновлен")
                else:
                    bot.send_message(message.chat.id, "Ошибка при обновлении рейтинга")
            except:
                bot.send_message(message.chat.id, "Ошибка при обновлении рейтинга")
                
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        if message.from_user.id in MAFIA_ID:
            if "Игра окончена! " in message.text:
                print(message.from_user.username, message.from_user.id)

                teams = analizing_message(message.text)
                if teams == 0:
                    bot.send_message(message.chat.id, 'Произошла какая-та ошибка')
                else:
                    rating_update(teams)
                    bot.send_message(message.chat.id, "Игра засчитана!")

    bot.infinity_polling(none_stop=True)
