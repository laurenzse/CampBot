import imgkit
import shutil
import os

from utils import generate_file_name

HPI_PM_PATH = 'websites/hpi_pm/'
INSTAGRAM_POST_PATH = 'websites/instagram_post/'
TEMP_GENERATION_PATH = 'websites/generation_temp/'

RESULT_PATH = 'generated_photos/'

ZOOM_FACTOR = 2

def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)

def create_article_screenshot(headline, teaser_text, photo_path, photo_caption, article_text, date_text):
    copy_and_overwrite(HPI_PM_PATH, TEMP_GENERATION_PATH)
    shutil.copyfile(photo_path, TEMP_GENERATION_PATH + "photo.jpeg")

    with open(TEMP_GENERATION_PATH + "html_file.html", "r+") as f:
        html_content = f.read()  # read everything in the file
        html_content = html_content.replace("DATE", date_text)
        html_content = html_content.replace("HEADLINE", headline)
        html_content = html_content.replace("TEASER", teaser_text)
        html_content = html_content.replace("PHOTO_CAPTION", photo_caption)
        html_content = html_content.replace("ARTICLE_TEXT", article_text)
        f.seek(0)  # rewind
        f.write(html_content)

    options = {
        'zoom': ZOOM_FACTOR,
        'width': 450,
        'quiet': ''
    }
    file_name = generate_file_name(RESULT_PATH + "hpi")
    imgkit.from_file(TEMP_GENERATION_PATH + 'html_file.html', file_name, options=options)
    shutil.rmtree(TEMP_GENERATION_PATH)

    return file_name

# usage:
# create_article_screenshot("HPI Student erfindet ersten digitalen Gullideckel",
#                           "Dem 26-Jährigen HPI-Absolvent kam die Idee beim Wandern mit Freunden. Seine Erfindung stellt die eine wichtige Weiterentwicklung für die Smartcity dar. Die Ergebnisse sollen im Mai auf der Industrie 4.0 Konferenz am Hasso-Plattner-Institut in Potsdam vorgestellt werden.",
#                           None,
#                           "HPI-Studenten geht es immer gut. (Foto: HPI/KSMGL)",
#                           "Es ist ein ganz normaler Montag. Die Straßen sind voll und ächzen unter der Verkehrslast. Diesen Umstand soll die neue Erfindung des HPI-Alumnus angehen.")

def create_instagram_screenshot(user_id, user_name, follow_text, photo_path, liked, can_share, can_comment, like_count, date_text, license, license_author, image_source):
    copy_and_overwrite(INSTAGRAM_POST_PATH, TEMP_GENERATION_PATH)
    shutil.copyfile(photo_path, TEMP_GENERATION_PATH + "photo.jpeg")

    with open(TEMP_GENERATION_PATH + "html_file.html", "r+") as f:
        html_content = f.read()  # read everything in the file
        html_content = html_content.replace("USER_ID", user_id)
        html_content = html_content.replace("USER_NAME", user_name)
        html_content = html_content.replace("FOLLOW_TEXT", follow_text)

        if liked:
            html_content = html_content.replace("<!--LIKED_COMMENT", '')
            html_content = html_content.replace("LIKED_COMMENT-->", '')
        else:
            html_content = html_content.replace("<!--NOT_LIKED_COMMENT", '')
            html_content = html_content.replace("LIKED_COMMENT_NOT-->", '')

        if can_share:
            html_content = html_content.replace("<!--SHARE_COMMENT", '')
            html_content = html_content.replace("SHARE_COMMENT-->", '')

        if can_comment:
            html_content = html_content.replace("<!--COMMENT_COMMENT", '')
            html_content = html_content.replace("COMMENT_COMMENT-->", '')

        html_content = html_content.replace("LIKE_COUNT", like_count)
        html_content = html_content.replace("DATE_TEXT", date_text)
        html_content = html_content.replace("LICENSE", license)
        html_content = html_content.replace("CREDIT_AUTHOR", license_author)
        html_content = html_content.replace("IMAGE_SOURCE", image_source)

        f.seek(0)  # rewind
        f.write(html_content)

    options = {
        # 'print-media-type': 'True',
        'zoom': ZOOM_FACTOR,
        'crop-x': 8 * ZOOM_FACTOR,
        'crop-y': 8 * ZOOM_FACTOR,
        'crop-w': 354 * ZOOM_FACTOR,
        'crop-h': 436 * ZOOM_FACTOR,
        'quiet': ''
    }
    file_name = generate_file_name(RESULT_PATH + "instagram")
    imgkit.from_file(TEMP_GENERATION_PATH + 'html_file.html', file_name, options=options)
    shutil.rmtree(TEMP_GENERATION_PATH)

    return file_name
