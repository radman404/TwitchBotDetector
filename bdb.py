from twitch_chatters import search_all_games, remove_offline

while True:
    try:
        search_all_games()
        remove_offline()
    except KeyboardInterrupt:
        exit()
