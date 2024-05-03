import sqlite3

def analizing_message(message):
    f = open('../data/log.txt', 'a')
    text = message.splitlines()
    good_roles = ["Мирный житель", "Доктор", "Комиссар Каттани", "Любовница",
                  "Камикадзе", "Бомж", "Сержант", "Счастливчик"]
    bad_roles = ["Мафия", "Дон", "Адвокат"]
    good_team = []
    bad_team = []
    team = -1
    try:
        if "Победили: Мирные жители" in text[1]:
            team = 1
        elif "Победила Мафия" in text[1] :
            team = 0

        if team == -1:
            return 0

        for i in range(3, len(text) - 2):
            is_find = 0
            name = text[i].split("-")[0].strip().split(', ')[0]
            for role in good_roles:
                if role in text[i]:
                    good_team.append(name)
                    is_find = 1
                    break
            if is_find == 0:
                for role in bad_roles:
                    if role in text[i]:
                        bad_team.append(name)
                        break

        teams = [good_team, bad_team, team]
        try:
            connection = sqlite3.connect('../data/my_database.db')
            cursor = connection.cursor()
            if team == 0:
                villager_win = 0
                mafia_win = 1
            else:
                villager_win = 1
                mafia_win = 0
            cursor.execute("INSERT INTO Game_logs (players_num, villager_win, mafia_win) VALUES (?,?,?)",
                           (len(teams[0]) + len(teams[1]), villager_win, mafia_win))
            connection.commit()
            connection.close()
            f.write("Добавил лог игры\n")
            print("Добавил лог игры")
        except:
            f.write("Не получилось добавить лог игры\n")
            print("Не получилось добавить лог игры")
        if teams == [[], []]:
            return 0
        return teams

    except:
        return 0

def scores_definition(teams):
    num_players = len(teams[0]) + len(teams[1])

    score = 0
    if num_players < 6:
        score = 10
    elif num_players > 5 and num_players < 12:
        score = 30
    elif num_players > 11 and num_players < 16:
        score = 20
    elif num_players > 15:
        score = 30
    return score

def rating_update(teams):
    win_team = teams[2]

    connection = sqlite3.connect('../data/my_database.db')
    cursor = connection.cursor()
    score = scores_definition(teams)
    f = open('../data/log.txt', 'a')

    if win_team == 0:
        score = -score

    for player in teams[0]:
        cursor.execute("SELECT * FROM Rating WHERE username =?", (player,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Rating (username, scores, villager_games) VALUES (?,?,?)", (player, 100 + score, 1))
            connection.commit()

            if win_team == 1:
                cursor.execute(f"UPDATE Rating SET villager_win = villager_win + 1 WHERE username = ?", (player,))
                connection.commit()

            print(f"{player} добавлен")
            f.write(f"{player} добавлен, {score}\n")

        else:
            cursor.execute(f"UPDATE Rating SET scores = scores + ?, villager_games = villager_games + 1 "
                           f"WHERE username = ?", (score, player,))
            connection.commit()

            if win_team == 1:
                cursor.execute(f"UPDATE Rating SET villager_win = villager_win + 1 WHERE username = ?", (player,))
                connection.commit()

            print(f"{player} обновлен")
            f.write(f"{player} обновлен, {score}\n")

    if win_team == 0:
        score = -score

    for player in teams[1]:
        cursor.execute("SELECT * FROM Rating WHERE username =?", (player,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Rating (username, ?) VALUES (?,?)", (player, 100 - score))
            connection.commit()
            cursor.execute(f"UPDATE Rating SET mafia_games = mafia_games + 1 WHERE username = ?", (player,))

            if win_team == 0:
                cursor.execute(f"UPDATE Rating SET mafia_win = mafia_win + 1 WHERE username = ?", (player,))

            print(f"{player} добавлен")
            f.write(f"{player} добавлен, {score}\n")
        else:
            cursor.execute("UPDATE Rating SET scores = scores - ?, mafia_games = mafia_games + 1 WHERE username =?", (score, player,))
            connection.commit()

            if win_team == 0:
                cursor.execute(f"UPDATE Rating SET mafia_win = mafia_win + 1 WHERE username = ?", (player,))
                connection.commit()

            print(f"{player} обновлен")
            f.write(f"{player} обновлен, {score}\n")

    connection.close()

def get_rating():
    connection = sqlite3.connect('../data/my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT username, scores FROM Rating ORDER BY scores DESC LIMIT 20;")
    top_10 = cursor.fetchall()
    connection.close()
    return top_10

def get_my_rating(username):
    connection = sqlite3.connect('../data/my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT scores, villager_games, mafia_games, villager_win, mafia_win FROM Rating WHERE username =?", (username,))
    my_rating = cursor.fetchone()
    connection.close()
    return my_rating

def set_user_id(user, username):
    conn = sqlite3.connect('../data/my_database.db')
    cursor = conn.cursor()
    f = open('../data/log.txt', 'a')

    try:
        cursor.execute("SELECT * FROM Rating WHERE username = ?;", (username, ))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("SELECT * FROM Rating WHERE user_id = ?;", (user.user.username, ))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute("UPDATE Rating SET username = ? WHERE user_id = ?;", (username, user.user.username))
                conn.commit()
                print("Значение username обновлено успешно.")
                f.write(f"Значение username для {username} обновлено успешно.\n")
                conn.close()
                return 1
            else:
                cursor.execute("INSERT INTO Rating (username, scores, user_id, "
                               "mafia_games, villager_games, mafia_win, villager_win) "
                               "VALUES (?, ?, ?, ?, ?, ?)", (username, 100, user.user.username, 0, 0, 0))
                conn.commit()
                conn.close()
                print("Добавлен новый пользователь.")
                f.write(f"Добавлен новый пользователь {username}.\n")
                return 1
        if row:
            existing_user_id = row[3]  # Предполагаем, что user_id находится во втором столбце
            if existing_user_id is not None:
                pass
            else:
                try:
                    cursor.execute("UPDATE Rating SET user_id = ? WHERE username = ?;", (user.user.username, username))
                    print("Значение user_id обновлено успешно.")
                    f.write(f"Значение user_id для {username} обновлено успешно.\n")
                    conn.commit()
                except:
                    f.write(f"Ошибка при обновлении значения user_id для {username}")
                    print("Ошибка при обновлении значения user_id.")


        conn.close()

        return 1

    except:
        f.write(f"Ошибка при обновлении значения user_id для {username}")
        print("Пользователь не найден.")
        return -1

def update_user_rating(user_id, score):
    conn = sqlite3.connect('../data/my_database.db')
    cursor = conn.cursor()
    f = open('../data/log.txt', 'a')
    print(user_id[0:])

    cursor.execute("SELECT * FROM Rating WHERE user_id = ?;", (user_id[1:], ))
    row = cursor.fetchone()
    print(row)
    if row is not None:
        cursor.execute("UPDATE Rating SET scores = ? WHERE user_id = ?;", (score, user_id[1:]))
        conn.commit()
        conn.close()
        f.write(f"Значение scores для {user_id} обновлено успешно\n")
        return 1
    else:
        cursor.execute("SELECT * FROM Rating WHERE username = ?;", (user_id, ))
        row = cursor.fetchone()
        print(row)
        if row is not None:
            cursor.execute("UPDATE Rating SET scores = ? WHERE username = ?;", (score, user_id))
            conn.commit()
            conn.close()
            f.write(f"Значение scores для {user_id} обновлено успешно\n")
            return 1
        else:
            conn.close()
            f.write(f"Ошибка при обновлении значения scores для {user_id}\n")
            return 0

def get_statistics():
    conn = sqlite3.connect('../data/my_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Game_logs")
    game_count = cursor.fetchone()
    cursor.execute("SELECT SUM(villager_win) FROM Game_logs")
    villager_win = cursor.fetchone()
    cursor.execute("SELECT SUM(mafia_win) FROM Game_logs")
    mafia_win = cursor.fetchone()
    cursor.execute("SELECT AVG(players_num) FROM Game_logs")
    players_avg = cursor.fetchone()
    return game_count[0], villager_win[0], mafia_win[0], players_avg[0]
