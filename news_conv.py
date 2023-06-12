from datetime import date

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler, Filters, MessageHandler

from camp_data import is_admin, get_session
from camp_data_declarative import TelegramUser
from screenshot_generator import create_article_screenshot
from utils import generate_file_name, post_screenshot
import os

START = 'pressemitteilung'
ENTER_HEADLINE, ENTER_TEASER, SEND_PHOTO, ENTER_PHOTO_CAPTION, ENTER_ARTICLE_TEXT, CONFIRM = range(6)

confirm_keyboard = [['Ja', 'Nein']]

DOWNLOAD_PATH = 'downloaded_photos/'

def ask_for_headline(bot, update):
    if not is_admin(update.effective_user.id):
        update.message.reply_text('Du hast leider nicht die erforderlichen Rechte für diesen Befehl.')

        return ConversationHandler.END

    update.message.reply_text('Gut, lass uns einen Artikel entwerfen. \n\n'
                              'Ich benötige dafür eine Überschrift, einen Teaser-Text, ein Foto, eine Fotounterschrift '
                              'und den eigentlichen Text. Bevor ich den Artikel an alle versende, lass ich dich '
                              'natürlich nochmal darübersehen.')
    update.message.reply_text('Schick mir zuerst die Überschrift.')

    return ENTER_HEADLINE


def ask_for_teaser(bot, update, user_data):
    headline = update.message.text

    user_data['headline'] = headline

    update.message.reply_text('Schick mir jetzt den Teaser-Text. Dieser sollte alle Aufmerksaamkeit auf sich ziehen und '
                              'ganz allgemein sagen, was Tolles am HPI passiert ist.')

    return ENTER_TEASER


def ask_for_photo(bot, update, user_data):
    teaser = update.message.text

    user_data['teaser'] = teaser

    update.message.reply_text('Sende mir jetzt das Foto für den Artikel.')

    return SEND_PHOTO


def handle_file(bot, update, user_data):
    downloaded_file_path = generate_file_name(DOWNLOAD_PATH + 'IN')

    update.message.document.get_file().download(
        custom_path=downloaded_file_path)

    user_data['photo_path'] = downloaded_file_path

    return ask_for_photo_caption(bot, update, user_data)


def handle_photo(bot, update, user_data):
    downloaded_file_path = generate_file_name(DOWNLOAD_PATH + 'IN')

    update.message.photo[0].get_file().download(
        custom_path=downloaded_file_path)

    user_data['photo_path'] = downloaded_file_path

    return ask_for_photo_caption(bot, update, user_data)


def ask_for_photo_caption(bot, update, user_data):
    update.message.reply_text('Schick mir eine Beschreibung, die ich unter das Foto schreiben kann. For added '
                              'professionality kannst du auch (Foto: XXX) ans Ende schreiben.')

    return ENTER_PHOTO_CAPTION


def ask_for_article_text(bot, update, user_data):
    photo_caption = update.message.text

    user_data['photo_caption'] = photo_caption

    update.message.reply_text('Schreib mir als letztes den Text der Pressemitteilung. Am besten kommt es, wenn '
                              'dieser mit einer Hauptperson/einem Hauptobjekt beginnt und mit der Meinung einer '
                              'wichtigen Person endet.')

    return ENTER_ARTICLE_TEXT


def confirm_news(bot, update, user_data):
    article_text = update.message.text

    user_data['article_text'] = article_text

    update.message.reply_text('Danke!')
    update.message.reply_text('Gib mir nun einen kleinen Moment für die Erstellung der Pressemitteilung...')

    date_text = date.today().strftime('%d.%m.%Y')

    generated_file_path = create_article_screenshot(user_data['headline'],
                                                    user_data['teaser'],
                                                    user_data['photo_path'],
                                                    user_data['photo_caption'],
                                                    user_data['article_text'],
                                                    date_text)

    user_data['generated_file_path'] = generated_file_path

    photo = open(generated_file_path, 'rb')
    bot.send_photo(update.effective_chat.id, photo)

    bot.send_message(update.effective_chat.id,
                     'Soll ich die Pressemitteilung so an alle bei mir registrierten Nutzer schicken?',
                     reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True),
                     parse_mode=ParseMode.MARKDOWN)

    return CONFIRM


def distribute_article(bot, update, user_data):
    session = get_session()

    registered_users = session.query(TelegramUser).all()

    update.message.reply_text('Gut, ich fange nun an zu senden...')
    for user in registered_users:
        if user.telegram_id == update.effective_user.id:
            continue
        photo = open(user_data['generated_file_path'], 'rb')
        bot.send_photo(user.telegram_id, photo)

    update.message.reply_text('Fertig!')

    clean_up(user_data)

    session.close()

    return ConversationHandler.END


def cancel(bot, update, user_data):
    clean_up(user_data)

    update.message.reply_text('Okay, abgebrochen.')

    return ConversationHandler.END


def clean_up(user_data):
    if user_data['photo_path']:
        os.remove(user_data['photo_path'])
    if user_data['generated_file_path']:
        os.remove(user_data['generated_file_path'])


def add_handlers(dispatcher):
    confirm_regexes = ['^{}'.format(item) for sublist in confirm_keyboard for item in sublist]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START, ask_for_headline, filters=Filters.private)],
        states={
            ENTER_HEADLINE: [MessageHandler(Filters.text, ask_for_teaser, pass_user_data=True)],
            ENTER_TEASER: [MessageHandler(Filters.text, ask_for_photo, pass_user_data=True)],
            SEND_PHOTO: [MessageHandler(Filters.photo, handle_photo, pass_user_data=True),
                         MessageHandler(Filters.document, handle_file, pass_user_data=True)],
            ENTER_PHOTO_CAPTION: [MessageHandler(Filters.text, ask_for_article_text, pass_user_data=True)],
            ENTER_ARTICLE_TEXT: [MessageHandler(Filters.text, confirm_news, pass_user_data=True)],
            CONFIRM: [RegexHandler(confirm_regexes[0], distribute_article, pass_user_data=True),
                      RegexHandler(confirm_regexes[1], cancel, pass_user_data=True)]
        },
        fallbacks=[CommandHandler("cancel", cancel, pass_user_data=True)],
        per_user=True,
    )

    dispatcher.add_handler(conv_handler)
