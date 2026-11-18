from sqlalchemy import text

from app.db.session import engine

with engine.connect() as connection:
    result = connection.execute(
        text("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'users'
        """)
    )

    print(result.scalar())