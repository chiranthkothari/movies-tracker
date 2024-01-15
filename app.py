import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
import os
from time import sleep
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

cred = credentials.Certificate("/etc/secrets/creds.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

bot = telegram.Bot(os.environ["BOT_KEY"])


async def send_message(message):
    try:
        print(message)
        await bot.sendMessage(chat_id=-1002063808221, text=f'''New release:
                              
{message}''')
    except Exception as e:
        print(e)


@app.get("/track/")
async def scrape_site():
    last_movie = db.collection(
        'latest-movie').document('LHU2CQpehHqVgXDaQNXX').get().to_dict()
    url = 'https://www.1tamilblasters.tel/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the list of movies
    li = soup.find(
        'li', class_='ipsWidget ipsWidget_horizontal ipsBox ipsResponsive_block')
    div = li.find("div", "ipsWidget_inner ipsPad ipsType_richText")
    p_tags = div.find_all("p")[3:]
    updated_doc = {"title": p_tags[0].get_text().strip().strip(
        "-").strip(), "timestamp": datetime.now().isoformat()}
    db.collection(
        'latest-movie').document('LHU2CQpehHqVgXDaQNXX').update(updated_doc)
    for index, item in enumerate(p_tags):
        for tag in item.find_all():
            tag.unwrap()
        p_tags[index] = item.get_text().strip().strip("-").strip()
    filtered_movies = p_tags[:p_tags.index(last_movie['title'])]
    for p in filtered_movies:
        await send_message(p)
    return JSONResponse(status_code=200, content=jsonable_encoder({"movies": filtered_movies}), media_type="application/json")


if __name__ == "__main__":
    asyncio.run(scrape_site())
