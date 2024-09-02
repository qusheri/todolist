import config
import psycopg2
async def create_note(text, date, message):
    conn = psycopg2.connect(dbname=config.dbname_, user=config.user_, password=config.password_, host=config.host_)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM last_id')
    last_id = cursor.fetchone()[0]
    #note_id int pk, text string, user_id int, date string
    print('INSERT INTO notes VALUES (' + str(last_id + 1) + ', \'' + text + '\', ' + str(message.from_user.id) + ', \'' + date + '\')')
    cursor.execute('INSERT INTO notes VALUES (' + str(last_id + 1) + ', \'' + text + '\', ' + str(message.from_user.id) + ', \'' + date + '\')')
    cursor.execute('UPDATE last_id SET id = ' + str(last_id + 1) + ' WHERE id = ' + str(last_id) + ';')
    conn.commit()