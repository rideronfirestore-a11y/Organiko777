import aiosqlite

DB = "organico11.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            stock INTEGER
        )
        ''')

        await db.commit()
