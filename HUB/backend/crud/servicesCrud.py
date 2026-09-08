from database.index import db

def get_all_services():
    with db.get_cursor() as cursor:
        sql = "SELECT serviceID, title, realTitle, category, active FROM `services`"
        cursor.execute(sql)
        return cursor.fetchall()

def get_active_services():
    with db.get_cursor() as cursor:
        sql = "SELECT serviceID, title, realTitle, category FROM `services` WHERE active = TRUE"
        cursor.execute(sql)
        return cursor.fetchall()

def get_services(category=str | None, title=str | None):
    with db.get_cursor() as cursor:
        sql = "SELECT serviceID, title, realTitle, category FROM `services` WHERE active = TRUE"
        params = []
        if category:
            sql += " AND category = %s"
            params.append(category)
        if title:
            sql += " AND title LIKE %s"
            params.append(f"%{title}%")
        cursor.execute(sql, params)
        return cursor.fetchall()

def get_categories():
    with db.get_cursor() as cursor:
        sql = "SELECT DISTINCT category FROM `services`"
        cursor.execute(sql)
        return [row["category"] for row in cursor.fetchall()]

def set_service_active(service_id: int, active: bool):
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT serviceID FROM `services` WHERE serviceID = %s",
            (service_id,)
        )
        if cursor.fetchone() is None:
            return False

        sql = "UPDATE `services` SET active = %s WHERE serviceID = %s"
        cursor.execute(sql, (active, service_id))
        return True