# Camp Bot

At our university's [IT summer camp for high school students](https://hpi.de/veranstaltungen/schuelerveranstaltungen/2019/hpi-sommercamp-2019.html) in 2019, we decided to teach programming by having the participants build their own [Telegram bots](https://core.telegram.org/bots). I developed a Telegram bot in advance that accompanied the students throughout the camp. This bot provided regular updates on camp activities through official-looking press releases, a digital version of the popular group game Assassin, and most importantly, a visual and collaborative code-breaking challenge.

For more background information, please view this [post](https://laurenzseidel.com/projects/camp-bot) on my personal web page.

## Setup

Install the requirements.

```
pip3 install -r requirements.txt
```

### Preparing the visual code breaking challenge
1) Download the photos and licenses using the [Wikipedia Image Crawler](https://github.com/laurenzse/WikipediaImageCrawler) repository. You need to manually filter the photos according to which licenses you want to permit. It is fine to simply remove the photos and not update the license file. Place the photos in the `raw_image/places` folder.
2) Generate the sky masks using a sky removal algorithm. I used the [skydetector](https://github.com/cnelson/skydetector) repository. Place the resulting masks in the `raw_image/masks` folder.
3) Add semi-random fallback masks to the `raw_image/masks/fallback` folder.
4) The weather images should still be present in the repository but feel free to update them to your liking.
5) Get an OpenWeather API key and place it in the `weather_key.txt` file

### Import participant data
1) Place the particpant data in the `participants.csv` file according to the format defined there.
2) Run `camp_data_import.py`
3) View the created MySQL database and take note of the login keys of the participants. You will need to hand those out to the participants so they can log on the bot.

### Register telegram bot
Register a bot with the telegram bot father and place the API key in the `token.txt` file.

## Running the bot

Run the `main.py` to run the bot.