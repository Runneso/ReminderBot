from aiogram import types

clear_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[types.KeyboardButton(text=" ")]])

none_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[types.KeyboardButton(text="None")]])

main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
add_task_button = types.KeyboardButton(text="➕ Add task.")
remove_task_button = types.KeyboardButton(text="➖ Remove task.")
change_timezone_button = types.KeyboardButton(text="🕐 Change timezone task.")
main_keyboard.keyboard.extend([[add_task_button, remove_task_button, change_timezone_button]])

change_timezone_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
UTC = [['UTC +12'], ['UTC +11'], ['UTC +10'], ['UTC +9'], ['UTC +8'], ['UTC +7'], ['UTC +6'], ['UTC +5'], ['UTC +4'],
       ['UTC +3'], ['UTC +2'], ['UTC +1'], ['UTC 0'], ['UTC -1,'], ['UTC -2'], ['UTC -3'], ['UTC -4'], ['UTC -5'],
       ['UTC -6'], ['UTC -7'], ['UTC -8'], ['UTC -9'], ['UTC -10,'], ['UTC -11'], ['UTC -12']]
change_timezone_keyboard.keyboard.extend(UTC)
