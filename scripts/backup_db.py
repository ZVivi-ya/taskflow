import sqlite3
from pathlib import Path
from datetime import datetime

# 1. 定义数据库和备份文件的路径
SOURCE_DB = Path("/app/data/taskflow.db")
BACKUP_DIR = Path("/tmp")

def create_backup():
    # 2. 检查源数据库是否存在
    if not SOURCE_DB.is_file():
        raise FileNotFoundError(f"数据库不存在：{SOURCE_DB}")

    # 3. 根据当前时间生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"taskflow_{timestamp}.db"
    backup_path = BACKUP_DIR / filename

    # 先写入临时文件，验证通过后再正式命名
    temp_path = BACKUP_DIR / f".{filename}.tmp"

    source = None
    target = None

    try:
        # 4. 以只读模式打开源数据库
        source = sqlite3.connect(
            f"file:{SOURCE_DB}?mode=ro",
            uri=True,
        )

        # 5. 创建目标备份数据库
        target = sqlite3.connect(str(temp_path))

        # 6. 使用 SQLite Backup API 进行一致性备份
        source.backup(target)

        # 7. 检查备份数据库的完整性
        result = target.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if result != "ok":
            raise RuntimeError(
                f"备份完整性检查失败：{result}"
            )

        print("备份完整性检查：", result)

        # 8. 关闭数据库连接
        target.close()
        target = None

        source.close()
        source = None

        # 9. 验证通过后，将临时文件改为正式备份文件名
        temp_path.replace(backup_path)

        print("备份成功！")
        print("备份文件：", backup_path)

    except Exception:
        if target is not None:
            target.close()

        if source is not None:
            source.close()

        temp_path.unlink(missing_ok=True)
        raise

if __name__ == "__main__":
    create_backup()
