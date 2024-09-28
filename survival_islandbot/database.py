import psycopg2

def connect_db():
    conn = psycopg2.connect(
        dbname="survival_game",
        user="your_user",
        password="your_password",
        host="localhost"
    )
    return conn

# Add a new player
def add_player(user_id):
    query = "INSERT INTO players (user_id) VALUES (%s) RETURNING id;"
    conn = connect_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
            player_id = cursor.fetchone()[0]
    conn.close()
    return player_id

# Get player resources
def get_resources(player_id):
    query = "SELECT wood, food, water FROM resources WHERE player_id = %s;"
    conn = connect_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (player_id,))
            resources = cursor.fetchone()
    conn.close()
    return resources if resources else (0, 0, 0)  # Return zero resources if not found

# Update resources
def update_resources(player_id, wood, food, water):
    query = """
    INSERT INTO resources (player_id, wood, food, water) 
    VALUES (%s, %s, %s, %s) 
    ON CONFLICT (player_id) 
    DO UPDATE SET wood = resources.wood + EXCLUDED.wood,
                  food = resources.food + EXCLUDED.food,
                  water = resources.water + EXCLUDED.water;
    """
    conn = connect_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (player_id, wood, food, water))
    conn.close()

# Add an event for a player
def add_event(player_id, event_type, description):
    query = "INSERT INTO events (player_id, event_type, description) VALUES (%s, %s, %s);"
    conn = connect_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (player_id, event_type, description))
    conn.close()

