import psycopg2
import psycopg2.pool

# Connection pooling configuration
pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,
    maxconn=10,
    host="localhost",
    dbname="survival_game",
    user="your_user",
    password="your_password"
)

def connect_db():
    return pool.getconn()

# Error handling and resource management
def add_player(user_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO players (user_id) VALUES (%s) RETURNING id", (user_id,))
                player_id = cursor.fetchone()[0]
                return player_id
    except psycopg2.Error as e:
        print(f"Error adding player: {e}")
        raise

def get_resources(player_id):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT wood, food, water FROM resources WHERE player_id = %s", (player_id,))
                resources = cursor.fetchone()
                return resources if resources else (0, 0, 0)  # Return zero resources if not found
    except psycopg2.Error as e:
        print(f"Error getting resources: {e}")
        raise

def update_resources(player_id, wood, food, water):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM resources WHERE player_id = %s)", (player_id,))
                exists = cursor.fetchone()[0]
                if exists:
                    cursor.execute("""
                        UPDATE resources SET wood = wood + %s, food = food + %s, water = water + %s WHERE player_id = %s
                    """, (wood, food, water, player_id))
                else:
                    cursor.execute("""
                        INSERT INTO resources (player_id, wood, food, water) VALUES (%s, %s, %s, %s)
                    """, (player_id, wood, food, water))
    except psycopg2.Error as e:
        print(f"Error updating resources: {e}")
        raise

def add_event(player_id, event_type, description):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO events (player_id, event_type, description) VALUES (%s, %s, %s)",
                               (player_id, event_type, description))
    except psycopg2.Error as e:
        print(f"Error adding event: {e}")
        raise
        
