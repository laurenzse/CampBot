from camp_data import get_session, is_admin
from camp_data_declarative import Participant, Murderer, TelegramUser
from random import shuffle

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Filters, CallbackQueryHandler

keyboard = [[InlineKeyboardButton("Ja", callback_data='murder_ja')], [InlineKeyboardButton("Nein", callback_data='murder_nein')]]
reply_markup = InlineKeyboardMarkup(keyboard)


def generate_murder_game(bot, update):
    if not is_admin(update.effective_user.id):
        update.message.reply_text('Du hast leider nicht die erforderlichen Rechte für diesen Befehl.')

        return

    session = get_session()

    session.query(Murderer).delete()

    registered_participants = session.query(Participant).filter(Participant.telegram_id.isnot(None)).all()
    players = list(registered_participants)

    shuffle(players)

    iterator = iter(players)

    prev_player = next(iterator)
    for player in iterator:
        murderer = Murderer(participant=prev_player, victim=player)
        session.add(murderer)

        prev_player = player

    murderer = Murderer(participant=players[len(players) - 1], victim=players[0])
    session.add(murderer)

    session.commit()
    session.close()


def inform_about_victims(bot, update):
    if not is_admin(update.effective_user.id):
        update.message.reply_text('Du hast leider nicht die erforderlichen Rechte für diesen Befehl.')

        return

    session = get_session()
    murderers = session.query(Murderer).all()

    for murderer in murderers:
        inform_murderer(bot, murderer)

    session.close()


def inform_murderer(bot, murderer):
    participant = murderer.participant
    victim = murderer.victim

    bot.send_message(participant.telegram_id, "{}, dein nächstes Mordopfer ist {} {}. Übergebe einen Gegenstand und schreibe dann /kill. Viel Erfolg!".format(participant.first_name, victim.first_name, victim.last_name))


def killed_victim(bot, update):
    session = get_session()

    telegram_id = update.effective_user.id
    participant = session.query(Participant).filter_by(telegram_id=telegram_id).first()

    if not participant:
        update.message.reply_text('Du bist anscheinend kein Camp-Teilnehmer.')
        return

    murderer = session.query(Murderer).filter_by(participant=participant).first()

    if not murderer:
        update.message.reply_text('Oh, anscheinend wurdest du schon ermordet oder nimmst nicht am Spiel teil.')
        return

    victim = murderer.victim

    update.message.reply_text('Okay, ich frage nun {}, ob der Mord sich tatsächlich zugetragen hat.'.format(
        victim.first_name))

    ask_victim(bot, murderer)


def ask_victim(bot, murderer):
    victim = murderer.victim

    bot.send_message(victim.telegram_id,
                     "Kurze Zwischenfrage: Wurdest du ermordet?",
                     reply_markup=reply_markup)


def handle_victim_murdered(bot, update):
    session = get_session()
    query = update.callback_query
    query.edit_message_reply_markup(reply_markup=None)

    victim_id = update.effective_user.id
    bot.send_message(victim_id,
                     "Okay, ich hoffe du hattest viel Spaß beim Spiel!")

    victim_participant = session.query(Participant).filter_by(telegram_id=victim_id).first()
    murderer = session.query(Murderer).filter_by(victim=victim_participant).first()
    victim_murderer = session.query(Murderer).filter_by(participant=victim_participant).first()

    murderer.victim = victim_murderer.victim
    session.delete(victim_murderer)
    session.commit()

    inform_murderer(bot, murderer)
    give_update(bot)

    session.close()


def give_update(bot):
    session = get_session()

    murderers_left = session.query(Murderer).count()

    if murderers_left == 1:
        inform_about_winner(bot)
    else:
        inform_about_murder(bot)


def inform_about_murder(bot):
    session = get_session()

    telegram_users = session.query(TelegramUser).all()

    for telegram_user in telegram_users:
        bot.send_message(telegram_user.telegram_id,
                         "Oh nein, mir wurde gesagt, dass gerade jemand ermordet wurde.")


def inform_about_winner(bot):
    session = get_session()

    telegram_users = session.query(TelegramUser).all()
    winner = session.query(Murderer).first()

    for telegram_user in telegram_users:
        bot.send_message(telegram_user.telegram_id,
                         "Liebe Ermordetengemeinde, auf dieser Welt ist nur Platz für eine Person. "
                         "Und {} ist diese Person. Herzlichen Glückwunsch!".format(winner.participant.first_name))



def handle_victim_not_murdered(bot, update):
    session = get_session()
    query = update.callback_query
    query.edit_message_reply_markup(reply_markup=None)

    victim_id = update.effective_user.id
    bot.send_message(victim_id,
                     "Gut, dann geht es jetzt einfach weiter.")

    victim_participant = session.query(Participant).filter_by(telegram_id=victim_id).first()
    murderer = session.query(Murderer).filter_by(victim=victim_participant).first()

    bot.send_message(murderer.participant.telegram_id,
                     "Dein Mordopfer hat den Mord nicht bestätigt.")

    session.close()


def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('generate_murder_game', generate_murder_game, filters=Filters.private))
    dispatcher.add_handler(CommandHandler('inform_all_murderers', inform_about_victims, filters=Filters.private))
    dispatcher.add_handler(CommandHandler('kill', killed_victim, filters=Filters.private))
    dispatcher.add_handler(CallbackQueryHandler(handle_victim_murdered,
                                                pattern='^murder_ja$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_victim_not_murdered,
                                                pattern='^murder_nein'))