from database.index import db

def get_service_by_id(service_id):
    with db.get_cursor() as cursor:
        sql = "SELECT * FROM `services` WHERE serviceID = %s"
        cursor.execute(sql, (service_id,))
        return cursor.fetchone()

def get_documents_to_scan(service_id):
    with db.get_cursor() as cursor:
        sql = "SELECT * FROM `scan_requirements` WHERE serviceID = %s"
        cursor.execute(sql, (service_id,))
        return cursor.fetchall()

def get_service_documents(service_id):
    with db.get_cursor() as cursor:
        sql = "SELECT * FROM `service_documents` WHERE serviceID = %s"
        cursor.execute(sql, (service_id,))
        return cursor.fetchall()