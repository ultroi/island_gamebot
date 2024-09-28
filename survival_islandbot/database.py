import psycopg2
from contextlib import contextmanager

# Database connection configuration
DATABASE_CONFIG = {
    'dbname': 'your_db_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

@contextmanager
def connect_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def update_resources(player_id, food=0, water=0, wood=0):
    """
    Update the resources for a specific player.

    :param player_id: ID of the player
    :param food: Amount of food to add (default is 0)
    :param water: Amount of water to add (default is 0)
    :param wood: Amount of wood to add (default is 0)
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE players 
                    SET food = food + %s, water = water + %s, wood = wood + %s 
                    WHERE user_id = %s
                """, (food, water, wood, player_id))
    except psycopg2.Error as e:
        print(f"Error updating resources: {e}")
        raise

def get_resources(player_id):
    """
    Retrieve the resources for a specific player.

    :param player_id: ID of the player
    :return: Tuple containing (food, water, wood)
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT food, water, wood FROM players WHERE user_id = %s", (player_id,))
                return cursor.fetchone()  # Returns a tuple (food, water, wood)
    except psycopg2.Error as e:
        print(f"Error retrieving resources: {e}")
        raise

def add_event(player_id, event_type, description):
    """
    Add an event related to the player in the database.

    :param player_id: ID of the player
    :param event_type: Type of the event (e.g., 'exploration', 'combat')
    :param description: Description of the event
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO events (player_id, event_type, description, timestamp) 
                    VALUES (%s, %s, %s, NOW())
                """, (player_id, event_type, description))
    except psycopg2.Error as e:
        print(f"Error adding event: {e}")
        raise

def get_player_group(player_id):
    """
    Get the group name for a specific player.

    :param player_id: ID of the player
    :return: Group name or None if not in a group
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT group_name FROM players WHERE user_id = %s", (player_id,))
                return cursor.fetchone()  # Returns the group name or None
    except psycopg2.Error as e:
        print(f"Error retrieving player group: {e}")
        raise

def add_player_to_group(player_id, group_name):
    """
    Add a player to a specific group.

    :param player_id: ID of the player
    :param group_name: Name of the group to join
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE players 
                    SET group_name = %s 
                    WHERE user_id = %s
                """, (group_name, player_id))
    except psycopg2.Error as e:
        print(f"Error adding player to group: {e}")
        raise

def remove_player_from_group(player_id):
    """
    Remove a player from their group.

    :param player_id: ID of the player
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE players 
                    SET group_name = NULL 
                    WHERE user_id = %s
                """, (player_id,))
    except psycopg2.Error as e:
        print(f"Error removing player from group: {e}")
        raise

def get_player_health(player_id):
    """
    Retrieve the health of a specific player.

    :param player_id: ID of the player
    :return: Player's health
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT health FROM players WHERE user_id = %s", (player_id,))
                return cursor.fetchone()  # Returns the player's health
    except psycopg2.Error as e:
        print(f"Error retrieving player health: {e}")
        raise

def update_player_health(player_id, health_change):
    """
    Update the health of a specific player.

    :param player_id: ID of the player
    :param health_change: Amount to change the health (can be positive or negative)
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE players SET health = health + %s WHERE user_id = %s", (health_change, player_id))
    except psycopg2.Error as e:
        print(f"Error updating player health: {e}")
        raise

def get_player_inventory(player_id):
    """
    Retrieve the inventory of a specific player.

    :param player_id: ID of the player
    :return: Player's inventory
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT inventory FROM players WHERE user_id = %s", (player_id,))
                return cursor.fetchone()  # Returns the player's inventory
    except psycopg2.Error as e:
        print(f"Error retrieving player inventory: {e}")
        raise

def update_player_inventory(player_id, item, quantity):
    """
    Update the inventory of a specific player by adding or updating an item.

    :param player_id: ID of the player
    :param item: The item to add/update
    :param quantity: The amount to add
    """
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE players 
                    SET inventory = jsonb_set(inventory, '{%s}', coalesce(inventory->'%s', '0')::int + %s) 
                    WHERE user_id = %s
                """, (item, item, quantity, player_id))
    except psycopg2.Error as e:
        print(f"Error updating player inventory: {e}")
        raise
