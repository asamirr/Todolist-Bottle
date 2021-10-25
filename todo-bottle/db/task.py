import db


def select(id=None):
    if id is None:
        sql = """SELECT id, summary, description, duedate, status_id, modified
                FROM task;"""
        return db.connection.execute(sql).fetchall()
    else:
        sql = """SELECT id, summary, description, duedate, status_id, modified
                FROM task WHERE id = ?1;"""
        return db.connection.execute(sql, (id,)).fetchone()


def insert(summary, description, duedate, status_id):
    sql = """INSERT INTO task(summary, description, duedate, status_id)
                  VALUES(?1,?2,?3,?4);"""
    with db.connection:
        cursor = db.connection.cursor()
        cursor.execute(sql, (summary, description, duedate, status_id))
        return cursor.lastrowid


def update(id, summary, description, duedate, status_id):
    sql = """UPDATE task
                SET summary = ?2,
                    description = ?3,
                    duedate = ?4,
                    status_id = ?5
              WHERE id = ?1;"""
    with db.connection:
        db.connection.execute(sql, (id, summary, description, duedate, status_id))


def delete(id=None):
    if id is None:
        sql = """DELETE FROM task;"""
        with db.connection:
            db.connection.execute(sql)
    else:
        sql = """DELETE FROM task WHERE id = ?1;"""
        with db.connection:
            db.connection.execute(sql, (id,))
