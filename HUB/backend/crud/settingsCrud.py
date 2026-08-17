from database.index import db

def get_province_list():
    with db.get_cursor() as cursor:
        sql = "SELECT * FROM `provinces`"
        cursor.execute(sql)
        return cursor.fetchall()

def get_commune_list(province_id: int):
    with db.get_cursor() as cursor:
        sql = "SELECT * FROM `communes` WHERE `provinceID` = %s"
        cursor.execute(sql, (province_id,))
        return cursor.fetchall()

def get_position(province_id: int, commune_id: int):
    with db.get_cursor() as cursor:
        sql = "SELECT name FROM `provinces` WHERE `provinceID` = %s"
        cursor.execute(sql, (province_id,))
        province = cursor.fetchone()

        sql = "SELECT name FROM `communes` WHERE `communeID` = %s"
        cursor.execute(sql, (commune_id,))
        commune = cursor.fetchone()

        return province["name"] if province else None, commune["name"] if commune else None