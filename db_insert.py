import mysql.connector

db_host = '127.0.0.1'
db_name = 'memorybotbd'
db_user = 'root'
db_pass = ''


def log_in(login):

    global db_host, db_name, db_user, db_pass

    user_id = None
    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        user_login = int(login)
        cur = connection.cursor()

        cur.execute("SELECT id FROM users WHERE login='%s'" % user_login)

        user_id = cur.fetchone()
        if user_id is None:
            mysql_insert_query = ("""INSERT INTO `users`(`login`) VALUES ('%s')""" % user_login)
            cursor = connection.cursor()
            cursor.execute(mysql_insert_query)
            user_id = cursor.lastrowid
            connection.commit()
            print(cursor.rowcount, "Запись в бд успешна")
            cursor.close()
            connection.close()
    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    if user_id is None:
        print("err_no_id")
        return "err_no_id"
    else:
        try:
            return user_id[0]
        except Exception as e:
            return user_id


def add_tag(tagname, login):

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        user_login = login
        cur = connection.cursor()

        cur.execute("SELECT * FROM `images` WHERE images.TagName = '%s' "
                    "AND images.UserProjID = "
                    "(SELECT users.id FROM users WHERE users.login = %d)" % (tagname, user_login))

        sql_res = cur.fetchone()
        print(sql_res)
        if sql_res is None:

            mysql_insert_query = ("""
            INSERT INTO 
            images(TagName, UserProjID, Date, TagNameReal) 
            VALUES('%s', (SELECT users.id FROM users WHERE users.login = %d), NOW(), '%s')
            """ % (tagname, user_login, str(user_login) + tagname))

            cursor = connection.cursor()
            cursor.execute(mysql_insert_query)
            sql_res = cursor.lastrowid
            connection.commit()
            print(cursor.rowcount, "Запись в бд успешна")
            cursor.close()
            print(sql_res)
            connection.close()
        else:
            return "err_tag_already_exists"

    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    return sql_res


def add_remark(remark, login):

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        user_login = login
        cur = connection.cursor()

        cur.execute("SELECT id FROM `images` WHERE images.Remark = '' "
                    "AND images.UserProjID = "
                    "(SELECT users.id FROM users WHERE users.login = %d)" % user_login)

        sql_res = cur.fetchone()
        print(sql_res)
        if sql_res is not None:

            mysql_insert_query = ("""UPDATE images SET `Remark` = '%s' WHERE images.id = %d""" % (str(remark), sql_res[0]))

            cursor = connection.cursor()
            cursor.execute(mysql_insert_query)
            sql_res = cursor.lastrowid
            connection.commit()
            print(cursor.rowcount, "Запись в бд успешна")
            cursor.close()
            print(sql_res)
            connection.close()
        else:
            return "err_no_such_row"

    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    return sql_res


def raise_flag(login):

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        user_login = login
        cur = connection.cursor()

        cur.execute("SELECT id FROM `images` WHERE images.azure_flag = 0 "
                    "AND images.UserProjID = "
                    "(SELECT users.id FROM users WHERE users.login = %d)" % user_login)

        sql_res = cur.fetchone()
        print(sql_res)
        if sql_res is not None:

            mysql_insert_query = ("""UPDATE images SET `azure_flag` = 1 WHERE images.id = %d""" % sql_res[0])

            cursor = connection.cursor()
            cursor.execute(mysql_insert_query)
            sql_res = cursor.lastrowid
            connection.commit()
            print(cursor.rowcount, "Запись в бд успешна")
            cursor.close()
            print(sql_res)
            connection.close()
        else:
            return "err_no_such_row"

    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    return sql_res


def kill_row(login):

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        user_login = login
        cur = connection.cursor()

        cur.execute("SELECT id FROM `images` WHERE images.azure_flag = 0 "
                    "AND images.UserProjID = "
                    "(SELECT users.id FROM users WHERE users.login = %d)" % user_login)

        sql_res = cur.fetchone()
        print(sql_res)
        if sql_res is not None:

            mysql_insert_query = ("""DELETE FROM images WHERE id='%d'""" % sql_res[0])

            cursor = connection.cursor()
            cursor.execute(mysql_insert_query)
            sql_res = cursor.lastrowid
            connection.commit()
            print(cursor.rowcount, "Удаление в бд выполнено")
            cursor.close()
            print(sql_res)
            connection.close()
        else:
            return "err_no_such_row"

    except mysql.connector.Error as error:
        print("Ошибка удаления в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    return sql_res


def kill_unfinished_rows():

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        mysql_insert_query = """DELETE FROM images WHERE images.azure_flag = 0"""

        cursor = connection.cursor()
        cursor.execute(mysql_insert_query)
        sql_res = cursor.lastrowid
        connection.commit()
        print(cursor.rowcount, "Удаление в бд выполнено")
        cursor.close()
        print(sql_res)
        connection.close()

    except mysql.connector.Error as error:
        print("Ошибка удаления в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")


def find_tag(tagnamereal):

    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        cur = connection.cursor()

        cur.execute("SELECT id FROM `images` WHERE images.TagNameReal = '%s'" % tagnamereal)

        sql_res = cur.fetchone()
        print(sql_res)
        if sql_res is not None:

            cur.execute("SELECT TagName FROM `images` WHERE images.id = '%d'" % sql_res[0])

            print("Поиск в бд выполнен")
            sql_res = cur.fetchone()
            print(sql_res[0])
            connection.close()
        else:
            return "err_no_such_row"

    except mysql.connector.Error as error:
        print("Ошибка поиска в бд {}".format(error))

    finally:
        print("MySQL соединение закрыто")
    return sql_res[0]


def find_tags(login):
    UserProjID = log_in(login)
    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        cur = connection.cursor()

        cur.execute("SELECT TagName FROM `images` WHERE UserProjID = %d" % UserProjID)

        TagNames = list()
        for row in cur.fetchall():
            TagNames.append(row[0])

        if connection.is_connected():
            connection.close()
            print("MySQL соединение закрыто")

        if TagNames is None:
            return "err_no_such_row"
        else:
            return TagNames
    except mysql.connector.Error as error:
        print("Ошибка поиска в бд {}".format(error))
        return "err_no_such_row"


def find_remark(login, TagName):
    UserProjID = log_in(login)
    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)
        cur = connection.cursor()
        cur.execute("SELECT Remark FROM `images` WHERE UserProjID = '%d' AND TagName = '%s'"
                    % (UserProjID, TagName))
        find_object = cur.fetchone()
        if find_object is None:
            print("MySQL соединение закрыто")
            return "err_no_such_row"
        else:
            print("MySQL соединение закрыто")
            return find_object[0]
    except mysql.connector.Error as error:
        print("Ошибка поиска в бд {}".format(error))
        return "err_no_such_row"


def find_tagnamereal(login, TagName):
    UserProjID = log_in(login)
    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)
        cur = connection.cursor()
        cur.execute("SELECT TagNameReal FROM `images` WHERE UserProjID = '%d' AND TagName = '%s'"
                    % (UserProjID, TagName))
        tagNameReal = cur.fetchone()
        if connection.is_connected():
            connection.close()
            print("MySQL соединение закрыто")
        if tagNameReal is None:
            return "err_no_such_row"
        else:
            return tagNameReal[0]
    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))
        return "err_no_such_row"


def find_tagnamereals(login):
    UserProjID = log_in(login)
    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)

        cur = connection.cursor()

        cur.execute("SELECT TagNameReal FROM `images` WHERE UserProjID = %d" % UserProjID)

        TagNames = list()
        for row in cur.fetchall():
            TagNames.append(row[0])

        if connection.is_connected():
            connection.close()
            print("MySQL соединение закрыто")

        if TagNames is None:
            return "err_no_such_row"
        else:
            return TagNames
    except mysql.connector.Error as error:
        print("Ошибка поиска в бд {}".format(error))
        return "err_no_such_row"


def find_tagnamereal_by_flag(login):
    UserProjID = log_in(login)
    global db_host, db_name, db_user, db_pass

    try:
        connection = mysql.connector.connect(host=db_host,
                                             database=db_name,
                                             user=db_user,
                                             password=db_pass)
        cur = connection.cursor()
        cur.execute("SELECT TagNameReal FROM `images` WHERE UserProjID = '%d' AND azure_flag = 0"
                    % UserProjID)
        tagNameReal = cur.fetchone()
        if connection.is_connected():
            connection.close()
            print("MySQL соединение закрыто")
        if tagNameReal is None:
            return "err_no_such_row"
        else:
            return tagNameReal[0]
    except mysql.connector.Error as error:
        print("Ошибка записи в бд {}".format(error))
        return "err_no_such_row"

