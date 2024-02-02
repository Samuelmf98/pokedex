import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']

def create_table_if_not_exists():
    try:
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

    
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'my_pokedex')")
        table_exists = cur.fetchone()[0]

        if not table_exists:
            # La tabla no existe, crearla
            cur.execute("""
                CREATE TABLE my_pokedex (
                    name VARCHAR(255) PRIMARY KEY,
                    height VARCHAR(255),
                    weight VARCHAR(255),
                    created_date TIMESTAMP
                )
            """)
            conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print("Error al crear la tabla:", e)