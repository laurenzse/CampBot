from camp_data_declarative import TelegramUser, Participant
from camp_data import get_session, register_participant, register_admin, register_regular_user


class AuthorizeStrategy:

    def __init__(self):
        self.sending_code = []

    def pass_update(self, bot, update):
        user_id = update.effective_user.id
        if self.is_authorized_user(user_id):
            return update

        message = update.effective_message
        if message is None:
            return None

        if self.user_can_send_code(user_id) and message.text is not None:
            code = message.text

            authorized_name = self.authorize_user(update.effective_user, code)
            if authorized_name:
                # pass original update back to dispatcher
                bot.send_message(update.effective_chat.id, "Hallo, {}! Viel Spaß beim Camp!".format(authorized_name))
                effective_update = [item for item in self.sending_code if item[0] == user_id][0][1]
                return effective_update
            else:
                bot.send_message(update.effective_chat.id, "Dieser Code ist mir leider nicht bekannt.")
                return None


        bot.send_message(update.effective_chat.id,
                         "Bitte schicke mir zunächst deinen Code.")

        # save original update so we can send it back to dispatcher
        self.sending_code.append((user_id, update))
        return None

    @staticmethod
    def authorize_user(user, code):
        # return True
        telegram_id = user.id
        session = get_session()
        fitting_participant = session.query(Participant).filter_by(authentication_code=code, telegram_id=None).first()
        session.close()
        if fitting_participant is not None:
            register_participant(telegram_id, code)
            return fitting_participant.first_name

        # TODO if we have more time, consider changing this to a more sophisticated authentication
        if code == 'RosinaGeigerÖffneDich':
            register_admin(telegram_id, user.first_name)
            return user.first_name

        if code == 'Ich bin ein #Betreuer':
            register_regular_user(telegram_id, user.first_name)
            return user.first_name

        return None

    def user_can_send_code(self, telegram_id):
        return len([item for item in self.sending_code if item[0] == telegram_id]) == 1

    @staticmethod
    def is_authorized_user(telegram_id):
        session = get_session()
        authorized = session.query(TelegramUser).filter_by(telegram_id=telegram_id).count() == 1
        session.close()
        return authorized




