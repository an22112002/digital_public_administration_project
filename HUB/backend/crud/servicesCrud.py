from backend.models.serviceModels import ServiceImport
import json

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
            url,
            buttonPosition,
            processes,
            active
        )
        VALUES (
            %s, %s, %s, %s, %s, %s
        )
    """

    values = [
        (
            service.title,
            service.realTitle,
            service.url,
            service.buttonPosition,
            json.dumps(
                service.processes,
                ensure_ascii=False
            ),
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