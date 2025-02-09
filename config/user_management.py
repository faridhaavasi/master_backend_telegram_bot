from telebot import TeleBot
from models import User, Rool

user_data = {}

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['register'])
    def set_first_name(message):
        chat_id = message.chat.id
        user_data[chat_id] = {}
        bot.send_message(chat_id, 'لطفا نام خود را وارد کنید')
        bot.register_next_step_handler(message, set_last_name)

    def set_last_name(message):
        chat_id = message.chat.id
        user_data[chat_id]['first_name'] = message.text  
        bot.send_message(chat_id, 'لطفا نام خانوادگی خود را وارد کنید')
        bot.register_next_step_handler(message, set_phone)

    def set_phone(message):
        chat_id = message.chat.id
        user_data[chat_id]['last_name'] = message.text  
        bot.send_message(chat_id, 'لطفا شماره تماس خود را وارد کنید')
        bot.register_next_step_handler(message, set_rool)

    def set_rool(message):
        chat_id = message.chat.id
        user_data[chat_id]['phone'] = message.text  
        master_exists = User.select().join(Rool).where(Rool.name == 'مستر').exists()

        bot.send_message(chat_id, 'لطفا نقش خود را انتخاب کنید:')
        if master_exists:
            bot.send_message(chat_id, '❌ نقش "مستر" قبلاً ثبت شده است. لطفا نقش دیگری را انتخاب کنید.')
        else:
            bot.send_message(chat_id, '1- مستر')
        bot.send_message(chat_id, '2- عادی')
        bot.register_next_step_handler(message, set_status_work, master_exists)

    def set_status_work(message, master_exists):
        chat_id = message.chat.id
        role_choice = message.text.strip()
        if role_choice == '1' and master_exists:
            bot.send_message(chat_id, '❌ شما نمی‌توانید به عنوان "مستر" ثبت نام کنید. لطفا مجددا /register را بزنید و نقش دیگری انتخاب کنید.')
            return
        user_data[chat_id]['rool'] = 'مستر' if role_choice == '1' else 'عادی'
        bot.send_message(chat_id, 'لطفا وضعیت کاری خود را انتخاب کنید:\n1- شاغل\n2- بیکار')
        bot.register_next_step_handler(message, finish_register)

    def finish_register(message):
        chat_id = message.chat.id
        status_choice = message.text.strip()
        user_data[chat_id]['status_work'] = 'شاغل' if status_choice == '1' else 'بیکار'

        user = User.create(
            chat_id=chat_id,
            first_name=user_data[chat_id]['first_name'],
            last_name=user_data[chat_id]['last_name'],
            phone=user_data[chat_id]['phone'],
            rool=Rool.get_or_create(name=user_data[chat_id]['rool'])[0],
            status_work=user_data[chat_id]['status_work']
        )
        user.save()
        bot.send_message(chat_id, '✅ ثبت نام شما با موفقیت انجام شد!')
        del user_data[chat_id]
