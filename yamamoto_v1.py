import json
import yamamoto_secrets
import shutil
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


bot = telebot.TeleBot(yamamoto_secrets.TELEGRAM_TOKEN)


def is_user_allowed(user_id):
    return user_id in yamamoto_secrets.WHITELISTED_USERS


# ts = timestamp
def get_ts():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def is_time_string_valid(datetime_str):
    try:
        _ = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
        return True
    except:
        return False


def get_aliases():
    with open(yamamoto_secrets.JSON_FILE, "r") as file:
        data = json.load(file)
        aliases = [device["alias"] for device in data]
        return aliases


def get_login_times():
    with open(yamamoto_secrets.JSON_FILE, "r") as file:
        data = json.load(file)

        login_times = []
        for device in data:
            alias = device["alias"]
            time = device["time"]
            login_times.append(f"{alias}: {time}\n")

    return tuple(login_times)


def backup_json():
    og_json = yamamoto_secrets.JSON_FILE
    datetime_str = get_ts().split(".")[0].replace(" ", "_")
    bak_json = f"{datetime_str}_{og_json}"

    print(f"[{get_ts()}] Yamamoto: Backing up JSON, {bak_json}")
    try:
        shutil.copyfile(og_json, bak_json)
        print(f"[{get_ts()}] Yamamoto: JSON back up completed, {bak_json}")
    except Exception as e:
        print(f"[{get_ts()}] Yamamoto: Error during JSON back up: {e}")


def update_json(alias, new_time):
    print(f"[{get_ts()}] Yamamoto: Making changes to JSON file")
    try:
        with open(yamamoto_secrets.JSON_FILE, "r") as file:
            data = json.load(file)

        for device in data:
            if device["alias"] == alias:
                device["time"] = new_time
                break

        with open(yamamoto_secrets.JSON_FILE, "w") as file:
            json.dump(data, file, indent=4)

    except Exception as e:
        print(f"[{get_ts()}] Yamamoto: Error during JSON update: {e}")


# Handle the /start command
@bot.message_handler(commands=["start"])
def reply_start(message):
    print(f"[{get_ts()}] {message.from_user.id}: /start")
    if is_user_allowed(message.from_user.id):
        bot.reply_to(message, "Use /help to see the list of available commands")
    else:
        bot.reply_to(message, f"Your user ID {message.from_user.id} is not on the whitelist")


# Handle the /help command
@bot.message_handler(commands=["help"])
def reply_help(message):
    print(f"[{get_ts()}] {message.from_user.id}: /help")
    if is_user_allowed(message.from_user.id):
        help_text = (
            "**Here are the commands you can use:**\n"
            "/start - Start interacting with the bot\n"
            "/view_config - View the current configuration\n"
            "/edit_config - Update the configuration\n"
            "/help - Show this help message\n"
        )
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, f"Your user ID {message.from_user.id} is not on the whitelist")


# Handle the /view_config command
@bot.message_handler(commands=['view_config'])
def reply_view_config(message):
    print(f"[{get_ts()}] {message.from_user.id}: /view_config")
    if is_user_allowed(message.from_user.id):
        bot.reply_to(message, get_login_times())
    else:
        bot.reply_to(message, f"Your user ID {message.from_user.id} is not on the whitelist")


# Handle the /edit_config command
@bot.message_handler(commands=["edit_config"])
def reply_edit_config(message):
    print(f"[{get_ts()}] {message.from_user.id}: /edit_config")
    if is_user_allowed(message.from_user.id):
        markup = InlineKeyboardMarkup()
        for alias in get_aliases():
            callback_data = f"edit_config_by_alias:{alias}"
            button = InlineKeyboardButton(alias, callback_data=callback_data)
            markup.add(button)

        bot.send_message(message.chat.id, "Pick a device:", reply_markup=markup)
    else:
        bot.reply_to(message, f"Your user ID {message.from_user.id} is not on the whitelist")


# Handle the alias button clicks
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_config_by_alias:"))
def handle_edit_config_callback(call):
    alias = call.data.split(":")[1]
    print(f"[{get_ts()}] {call.message.from_user.id}: /edit_config_by_alias ({alias})")

    bot.answer_callback_query(call.id)  # necessary?

    msg = bot.send_message(call.message.chat.id, f"New login time for {alias}:")

    def process_user_input(message):
        user_input_new_time = message.text.strip()
        if is_time_string_valid():
            update_json(alias, user_input_new_time)
            bot.send_message(message.chat.id, f"Configuration updated for {alias}")
        else:
            bot.send_message(message.chat.id, "Invalid input")

    bot.register_next_step_handler(msg, process_user_input)


def main():
    bot.polling()


if __name__ == "__main__":
    main()
