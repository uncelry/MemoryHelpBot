import telebot
import os

os.system('python db_insert.py')
from db_insert import kill_unfinished_rows
kill_unfinished_rows()

bot = telebot.TeleBot('1365297856:AAHmBP1egPsge8mjr2n8Jal9cpJQa9cHh5c')

connect_flag_arr = dict()
vid_flag_arr = dict()
tag_flag_arr = dict()
process_flag_arr = dict()
note_flag_arr = dict()

flag_arrs_arr = [connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr]

pubitername = "Iteration 55"  # ВЫСТАВИТЬ ВНАЧАЛЕ


@bot.message_handler(commands=['dev'])
def dev(message):
    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    print(flag_arrs_arr)


@bot.message_handler(commands=['start'])
def start_message(message):

    os.system('python db_insert.py')
    from db_insert import log_in
    log_in(message.chat.id)

    bot.send_message(message.chat.id, 'Привет, чтобы начать пришлите мне фото предмета!')
    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if not connect_flag_arr.get(message.chat.id):
        for flag in flag_arrs_arr:
            flag[message.chat.id] = False
        connect_flag_arr[message.chat.id] = True


@bot.message_handler(commands=['help'])
def help_message(message):

    os.system('python db_insert.py')
    from db_insert import log_in
    log_in(message.chat.id)

    bot.send_message(message.chat.id,
                     'Это бот, который помогает людям запоминать и вспоминать предметы!\nОтправьте фото, чтобы начать')
    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if not connect_flag_arr.get(message.chat.id):
        for flag in flag_arrs_arr:
            flag[message.chat.id] = False
        connect_flag_arr[message.chat.id] = True


@bot.message_handler(commands=['stop'])
def stop_message(message):
    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if not connect_flag_arr.get(message.chat.id):

        os.system('python db_insert.py')
        from db_insert import log_in, kill_row
        log_in(message.chat.id)

        for flag in flag_arrs_arr:
            flag[message.chat.id] = False
        connect_flag_arr[message.chat.id] = True
        bot.send_message(message.chat.id,
                         'Невозможно отменить добавление объекта, так как сейчас ничего не добавляется)')
    else:

        if tag_flag_arr.get(message.chat.id) or vid_flag_arr.get(message.chat.id) or note_flag_arr.get(message.chat.id):

            os.system('python db_insert.py')
            from db_insert import kill_row
            kill_row(message.chat.id)

            for flag in flag_arrs_arr:
                flag[message.chat.id] = False
            connect_flag_arr[message.chat.id] = True
            bot.send_message(message.chat.id, 'Добавление объекта отменено')
        else:
            bot.send_message(message.chat.id,
                             'Невозможно отменить добавление объекта, так как сейчас ничего не добавляется)')


@bot.message_handler(content_types=['photo'])
def send_photo(message):
    os.system('python Project_full.py')
    from Project_full import prediction

    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if not connect_flag_arr.get(message.chat.id):

        os.system('python db_insert.py')
        from db_insert import log_in
        log_in(message.chat.id)

        for flag in flag_arrs_arr:
            flag[message.chat.id] = False
        connect_flag_arr[message.chat.id] = True

    if not process_flag_arr.get(message.chat.id):
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = 'bot_photos_tmp/' + message.photo[-1].file_id + '.jpg'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            print("Загружаем фото - file_id: " + str(message.photo[-1].file_id))

            bot.send_message(message.chat.id, 'Хорошо, картинка получена. Сейчас проверю, было ли уже такое...')

            tags = []
            global pubitername
            r = prediction(src, pubitername)

            percent_cnt = False
            match_item = ''

            os.system('python db_insert.py')
            from db_insert import find_tagnamereals
            real_tags = find_tagnamereals(message.chat.id)

            for prediction in r.predictions:

                tags.append(prediction.tag_name)
                print("\t" + prediction.tag_name + ":{0:.2f}% ".format(prediction.probability * 100))

            mathes = []
            for i in tags:
                for j in real_tags:
                    if i == j:
                        mathes.append(i)
                        break
            print(mathes)
            tags.clear()
            for prediction in r.predictions:
                if (prediction.tag_name in mathes) and ((prediction.probability * 100) > 80.00):
                    percent_cnt = True
                    match_item = prediction.tag_name

            if percent_cnt:
                from db_insert import find_tag, find_remark

                user_obj = find_tag(match_item)
                bot.send_message(message.chat.id, 'Это ' + user_obj)
                tag_flag_arr[message.chat.id] = False
                vid_flag_arr[message.chat.id] = False
                bot.send_message(message.chat.id, 'Вот ваша заметка по этому объекту:\n'
                                 + find_remark(message.chat.id, user_obj))
                bot.send_message(message.chat.id, 'Если название объекта не совпадает с тем, что вы сфотографировали, '
                                                  'то, скорее всего, вы его не добавляли. Если вы хотите его добавить, '
                                                  'то ввидите его название. Если не хотите - введите команду /stop')

                tag_flag_arr[message.chat.id] = True
                vid_flag_arr[message.chat.id] = False
            else:
                bot.send_message(message.chat.id,
                                 'Объект не найден. Чтобы добавить его - напишите его название'
                                 '\nДля отмены введите команду /stop')
                tag_flag_arr[message.chat.id] = True
                vid_flag_arr[message.chat.id] = False

        except Exception as e:
            bot.reply_to(message, "Произошла ошибка! =(\nПопробуйте ещё раз!")
            tag_flag_arr[message.chat.id] = False
            vid_flag_arr[message.chat.id] = False
            print(e)
    else:
        bot.send_message(message.chat.id,
                         'Вы уже добавляете другой объект - сначала закончите добавление '
                         'или отмените его командной /stop')


@bot.message_handler(content_types=['text'])
def send_tag(message):
    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if tag_flag_arr.get(message.chat.id):

        note_flag_arr[message.chat.id] = True
        bot.send_message(message.chat.id,
                         'Напишите свои заметки об этом объекте. Для отмены введите команду /stop')
        tag_flag_arr[message.chat.id] = False
        process_flag_arr[message.chat.id] = True

        os.system('python db_insert.py')
        from db_insert import add_tag
        add_tag(message.text, message.chat.id)

    elif note_flag_arr.get(message.chat.id):
        bot.send_message(message.chat.id,
                         'Теперь запишите короткое видео объекта (~5 секунд). Постарайтесь снять его с разных сторон'
                         '\nДля отмены введите команду /stop')
        vid_flag_arr[message.chat.id] = True
        note_flag_arr[message.chat.id] = False
        process_flag_arr[message.chat.id] = True

        os.system('python db_insert.py')
        from db_insert import add_remark
        add_remark(message.text, message.chat.id)


@bot.message_handler(content_types=['video'])
def send_video(message):
    os.system('python Project_full.py')
    from Project_full import video_to_neiroset

    global connect_flag_arr, vid_flag_arr, tag_flag_arr, process_flag_arr, note_flag_arr, flag_arrs_arr
    if vid_flag_arr.get(message.chat.id):

        file_info = bot.get_file(message.video.file_id)

        if message.video.duration < 5:
            bot.reply_to(message, "Видео слишком короткое!\nЗапишите новое - чуть-чуть подлиннее)")
            return

        bot.send_message(message.chat.id, 'Видео обрабатывается, это займет несколько минут...')

        vid_flag_arr[message.chat.id] = False
        note_flag_arr[message.chat.id] = False
        process_flag_arr[message.chat.id] = True

        try:
            downloaded_file = bot.download_file(file_info.file_path)

            src = 'bot_videos_tmp/' + message.video.file_id + '.mp4'
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            print("Загружаем видео - file_id: " + str(message.video.file_id))

            os.system('python db_insert.py')
            from db_insert import find_tagnamereal_by_flag

            itername = video_to_neiroset(find_tagnamereal_by_flag(message.chat.id), src)

            if itername is "err":
                bot.reply_to(message,
                             "Произошла ошибка! =(\nПопробуйте загрузить другое видео объекта!"
                             "\nДля отмены введите команду /stop")
                vid_flag_arr[message.chat.id] = True
            else:
                bot.send_message(message.chat.id, 'Видео успешно добавлено! c;\n'
                                                  'В следующий раз, если вы сфотографируете этот объет, '
                                                  'он распознается!')

                os.system('python db_insert.py')
                from db_insert import raise_flag
                raise_flag(message.chat.id)

            global pubitername
            pubitername = itername

            print(itername)

        except Exception as e:
            vid_flag_arr[message.chat.id] = True
            note_flag_arr[message.chat.id] = False
            bot.reply_to(message,
                         "Произошла ошибка! =(\nПопробуйте загрузить другое видео объекта!"
                         "\nДля отмены введите команду /stop")
            print(e)
        process_flag_arr[message.chat.id] = False


bot.polling()
