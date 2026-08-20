from backend.models.serviceModels import ServiceImport
import json
from database.index import db

def insert_services(cursor, services: list[ServiceImport]) -> None:
    """
    Insert danh sách services vào database.
    """

    if not services:
        return

    sql = """
        INSERT INTO services (
            title,
            realTitle,
            category,
            url,
            buttonPosition,
            active
        )
        VALUES (
            %s, %s, %s, %s, %s
        )
    """

    values = [
        (
            service.title,
            service.realTitle,
            service.url,
            service.buttonPosition,
            service.active
        )
        for service in services
    ]

    cursor.executemany(sql, values)


def get_service_ids(cursor) -> dict[str, int]:
    """
    Lấy mapping realTitle -> serviceID từ database.

    Ví dụ:
    {
        "Chứng thực bản sao": 1,
        "Đăng ký khai sinh": 2
    }
    """

    sql = """
        SELECT serviceID, realTitle
        FROM services
    """

    cursor.execute(sql)

    return {
        row["realTitle"]: row["serviceID"]
        for row in cursor.fetchall()
    }


def delete_all_services(cursor) -> None:
    """
    Xóa toàn bộ dữ liệu trong bảng services.
    """

    cursor.execute("""
        DELETE FROM services
    """)

def get_active_services():
    with db.get_cursor() as cursor:
        sql = "SELECT serviceID, title, realTitle, category FROM `services` WHERE active = TRUE"
        cursor.execute(sql)
        return cursor.fetchall()

def get_categories():
    with db.get_cursor() as cursor:
        sql = "SELECT DISTINCT category FROM `services`"
        cursor.execute(sql)
        return [row["category"] for row in cursor.fetchall()]