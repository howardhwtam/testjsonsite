import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from secrets import TELEGRAM_TOKEN, WHITELISTED_USERS

# Replace 'YOUR_TOKEN' with your bot's token
bot = telebot.TeleBot(TELEGRAM_TOKEN)

WHITELISTED_USERS = [
    1761200689,  # Howard
    1111111111,  # Hugo
]


def get_login_time(): 
    with open("d8698dc6486a096a6de364a141z78646.json", "r") as file:
        data = json.load(file)
        return data


# Function to check if a user is allowed
def is_user_allowed(user_id):
    return user_id in WHITELISTED_USERS


# Handle the /start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    if is_user_allowed(message.from_user.id):
        bot.reply_to(
            message, "Hello! Use /view_config to see the current configuration."
        )
    else:
        bot.reply_to(message, "401 Unauthorized")


# Handle the /view_config command
@bot.message_handler(commands=["view_config"])
def show_options(message):
    if is_user_allowed(message.from_user.id):
        # Create an inline keyboard with two buttons
        markup = InlineKeyboardMarkup()
        button_view_config = InlineKeyboardButton(
            "View current config", callback_data="view_config"
        )
        button_help = InlineKeyboardButton("Help", callback_data="help")
        markup.add(button_view_config, button_help)
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)
    else:
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")


# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if is_user_allowed(call.from_user.id):
        if call.data == "view_config":
            # Load and send the configuration data
            config_data = get_login_time()
            config_text = json.dumps(config_data, indent=4)
            bot.send_message(
                call.message.chat.id, f"Current Configuration:\n{config_text}"
            )
        elif call.data == "help":
            # Send a help message
            bot.send_message(
                call.message.chat.id,
                "This is the help message. Use /view_config to view the configuration.",
            )
    else:
        bot.send_message(
            call.message.chat.id, "Sorry, you are not authorized to use this bot."
        )


def main():
    bot.polling()


if __name__ == "__main__":
    main()
