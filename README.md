# 🏝️ Island Survival Bot

Island Survival Bot is a text-based adventure game built for Telegram. Embark on an epic survival journey on a deserted island, utilizing Pyrogram for Telegram integration and MongoDB for backend support.

## 🌟 Features

| Feature            | Description                                      | Status |
|--------------------|--------------------------------------------------|--------|
| /start             | Begin your survival adventure                     | ✅     |
| /explore           | Explore the island to find resources              | ✅     |
| /inventory         | Check your current inventory                      | ✅     |
| /craft             | Craft items using collected resources             | ✅     |
| Customizable       | Modify gameplay settings through JSON files       | ✅     |

## 🚀 Installation Guide

1. **Clone the repository:**
    ```bash
    git clone https://github.com/ultroi/island_gamebot.git
    cd island_gamebot
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the bot:**
    ```bash
    python bot.py
    ```

## 🎮 How to Play

- **Start the game:**
    ```bash
    /start
    ```

- **Explore the island:**
    ```bash
    /explore
    ```

- **Check your inventory:**
    ```bash
    /inventory
    ```

- **Craft items:**
    ```bash
    /craft
    ```

## ⚙️ Configuration

You can customize the gameplay settings through JSON configuration files. Below is an example configuration:
```json
{
    "start_message": "Welcome to Island Survival!",
    "explore_chance": 0.3,
    "resources": ["wood", "stone", "food"],
    "craftable_items": {
        "shelter": {"wood": 5, "stone": 2},
        "fire": {"wood": 3}
    }
}
