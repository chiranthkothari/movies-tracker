import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import os
from time import sleep

last_movie = ""
bot = telegram.Bot(os.environ["BOT_KEY"])


async def send_message(message):
    try:
        print(message)
        await bot.sendMessage(chat_id=-1002063808221, text=f'''New release:
                              
{message}''')
    except Exception as e:
        print(e)


def get_last_movie():
    global last_movie
    with open('last_movie.txt', 'r') as file:
        last_movie = file.read()


async def scrape_site():
    get_last_movie()
    url = 'https://www.1tamilblasters.tel/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the list of movies
    li = soup.find(
        'li', class_='ipsWidget ipsWidget_horizontal ipsBox ipsResponsive_block')
    div = li.find("div", "ipsWidget_inner ipsPad ipsType_richText")
    p_tags = div.find_all("p")[3:]
    with open('last_movie.txt', 'w') as file:
        file.write(p_tags[0].get_text().strip().strip("-").strip())
    for index, item in enumerate(p_tags):
        for tag in item.find_all():
            tag.unwrap()
        p_tags[index] = item.get_text().strip().strip("-").strip()
    for p in p_tags[:p_tags.index(last_movie)]:
        await send_message(p)
    print("Worker sleeping")
    sleep(3600)
    await scrape_site()


if __name__ == "__main__":
    asyncio.run(scrape_site())
