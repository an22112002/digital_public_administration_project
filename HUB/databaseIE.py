from pathlib import Path
import argparse
import sys
import pandas as pd 
from mysql.connector import pooling
from contextlib import contextmanager

class Database:

    def __init__(self, host, port, user, password, database, pool_size):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool_size = pool_size

    def init_pool(self) -> bool:

        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=self.pool_size,

                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,

                autocommit=False
            )

            # ping thử kết nối
            conn = self.pool.get_connection()
            conn.ping(reconnect=True)
            conn.close()

            return True
        except Exception as e:
            print(f"Lỗi khởi tạo MySQL Pool: {e}")
            self.pool = None
            return False

    def get_connection(self):

        if self.pool is None:
            raise Exception("Pool not initialized")

        return self.pool.get_connection()

    def get_conn_cursor(self):

        conn = self.get_connection()

        cursor = conn.cursor(dictionary=True)

        return conn, cursor

    @contextmanager
    def get_cursor(self):

        conn = self.get_connection()

        cursor = conn.cursor(dictionary=True)

        try:
            yield cursor

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

def get_runtime_base_dir() -> Path:
    # Khi chạy .exe one-file (PyInstaller), ưu tiên thư mục chứa file .exe.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def load_config(config_path: str | None = None):
    if config_path:
        path = Path(config_path)
    else:
        path = get_runtime_base_dir() / "IEconfig.txt"

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        config = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import/Export database to CSV",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "export", "import"],
        default="interactive",
        help="Chế độ chạy: interactive/export/import",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Đường dẫn file IEconfig.txt",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Folder output cho mode export",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Folder input cho mode import",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Mode import: xóa dữ liệu cũ trước khi import",
    )
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="Mode import: không xóa dữ liệu cũ trước khi import",
    )
    return parser.parse_args()

# ============================================================ 
# Thứ tự này dùng khi INSERT: # bảng cha -> bảng con 
# ============================================================ 
IMPORT_ORDER = [ "provinces", "services", "communes", "service_documents", "scan_requirements", ] 
# ============================================================ 
# Thứ tự này dùng khi DELETE: 
# bảng con -> bảng cha # ============================================================ 
DELETE_ORDER = [ "service_documents", "scan_requirements", "communes", "services", "provinces", ] 
def export_database_to_csv( output_folder: str, db: Database, ): 
    """ Export data của toàn bộ các table trong database ra CSV. 
    Không export: - schema - primary key definition - foreign key - index - auto_increment definition 
    Chỉ export data. Ví dụ: export_database_to_csv( "backup/HUB_db", db ) 
    Kết quả: backup/HUB_db/ 
            ├── provinces.csv 
            ├── communes.csv 
            ├── services.csv 
            ├── service_documents.csv 
            └── scan_requirements.csv 
    """ 
    output_path = Path(output_folder) 
    output_path.mkdir(parents=True, exist_ok=True) 
    conn = db.get_connection() 
    try: 
        # Lấy danh sách table từ database hiện tại 
        cursor = conn.cursor() 
        cursor.execute("SHOW TABLES") 
        tables = [ row[0] for row in cursor.fetchall() ] 
        cursor.close() 
        for table in tables: 
            print(f"Exporting table: {table}")
            # pandas đọc trực tiếp từ mysql connection 
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table}`")

            rows = cursor.fetchall()

            cursor.close()

            df = pd.DataFrame(rows)
            csv_path = output_path / f"{table}.csv" 
            df.to_csv( csv_path, index=False, encoding="utf-8-sig", ) 
            print( f" -> {csv_path} " f"({len(df)} rows)" ) 
    finally: conn.close() 

def import_database_from_csv(
    input_folder: str,
    db: Database,
    replace: bool = True,
):
    input_path = Path(input_folder)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy folder: {input_folder}"
        )

    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        if replace:
            print("\nDisabling foreign key checks...")

            cursor.execute(
                "SET FOREIGN_KEY_CHECKS = 0"
            )

            # -------------------------------
            # DELETE
            # -------------------------------

            for table in DELETE_ORDER:

                csv_path = input_path / f"{table}.csv"

                if not csv_path.exists():
                    print(
                        f"Skip clearing {table}: "
                        f"CSV không tồn tại"
                    )
                    continue

                print(f"Clearing table: {table}")

                cursor.execute(
                    f"DELETE FROM `{table}`"
                )

        # -------------------------------
        # IMPORT
        # -------------------------------

        for table in IMPORT_ORDER:

            csv_path = input_path / f"{table}.csv"

            if not csv_path.exists():
                print(
                    f"Skip importing {table}: "
                    f"CSV không tồn tại"
                )
                continue

            df = pd.read_csv(
                csv_path,
                encoding="utf-8-sig",
                keep_default_na=False,
            )

            print(
                f"Importing table: {table}"
            )

            print(
                f" -> CSV rows: {len(df)}"
            )

            if df.empty:
                print(
                    f" -> Skip {table}: empty"
                )
                continue

            columns = list(df.columns)

            column_sql = ", ".join(
                f"`{column}`"
                for column in columns
            )

            placeholders = ", ".join(
                ["%s"] * len(columns)
            )

            query = f"""
                INSERT INTO `{table}`
                ({column_sql})
                VALUES ({placeholders})
            """

            data = []

            for row in df.itertuples(
                index=False,
                name=None,
            ):
                converted_row = []

                for value in row:

                    if pd.isna(value):
                        value = None

                    converted_row.append(value)

                data.append(
                    tuple(converted_row)
                )

            cursor.executemany(
                query,
                data
            )

            print(
                f" -> Inserted rows: "
                f"{cursor.rowcount}"
            )

        if replace:
            cursor.execute(
                "SET FOREIGN_KEY_CHECKS = 1"
            )

        conn.commit()

        print("\nImport database thành công.")

    except Exception as e:

        conn.rollback()

        try:
            cursor.execute(
                "SET FOREIGN_KEY_CHECKS = 1"
            )
        except Exception:
            pass

        print(
            f"\nImport database thất bại: {e}"
        )

        raise

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    args = parse_args()

    try:
        config = load_config(args.config)
        db = Database(
            host=config.get("DB_HOST"),
            port=int(config.get("DB_PORT")),
            user=config.get("DB_USER"),
            password=config.get("DB_PASSWORD"),
            database=config.get("DB_NAME"),
            pool_size=int(config.get("DB_POOL_SIZE"))
        )
        if not db.init_pool():
            print("Không thể kết nối database.")
            exit(1)

    except Exception as e:
        print(f"Lỗi: {e}")
        exit(1)

    if args.mode == "export":
        if not args.output:
            raise ValueError("Thiếu --output cho mode export")
        export_database_to_csv(args.output, db)
        sys.exit(0)

    if args.mode == "import":
        if not args.input:
            raise ValueError("Thiếu --input cho mode import")

        replace = True
        if args.no_replace:
            replace = False
        elif args.replace:
            replace = True

        import_database_from_csv(args.input, db, replace=replace)
        sys.exit(0)

    order = input("Chức năng: \n(0) Close program\n(1) Export database ra CSV\n(2) Import database từ CSV\n: ")
    if order == "0":
        print("Đóng chương trình.")
    elif order == "1":
        output_folder = input("Nhập folder output: ")
        export_database_to_csv(output_folder, db)
    elif order == "2":
        input_path = input("Nhập folder input: ")
        import_database_from_csv(input_path, db)