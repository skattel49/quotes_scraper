from enum import auto
from flask import Flask, request
from bs4 import BeautifulSoup
from flask_cors import CORS
import requests
import json
import random
import time
from dotenv import load_dotenv
import os
import json

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ACCESS_KEY=os.getenv("ACCESS_KEY")

random.seed(time.time())

app = Flask(__name__)
CORS(app)

#could have used a database but I don't really want to save all the data that I get from goodreads
quotes_genre = {
    'love': 0, 'life': 0, 'inspirational': 0,'humor': 0, 'philosophy': 0, 'god': 0,\
    'inspirational-quotes': 0,'truth': 0, 'wisdom': 0, 'poetry': 0, 'romance': 0, 'death': 0, \
    'happiness': 0, 'hope': 0, 'faith': 0, 'inspiration': 0, 'quotes': 0, 'writing': 0,\
    'life-lessons': 0, 'motivational': 0, 'religion': 0, 'relationships': 0, 'success': 0,\
    'spirituality': 0, 'time': 0, 'love-quotes': 0, 'life-quotes': 0, 'knowledge': 0,\
    'science': 0, 'motivation': 0
    }

#suprisingly an easy solution but took me a lot of time to come to this solution
#sometimes it's better to stick to naive solutions rather than prompting for a sophisticated idea
def html_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    my_data = soup.find_all("div", {"class": "quoteText"})
    quotes = []
    for data in my_data:
        #find the author of the quote
        span_author = data.find("span", {"class": "authorOrTitle"})
        authorOrTitle = span_author.string.strip()
        #delete the span tag
        span_author.extract()
        #could have created a lambda function
        all_span_tags = [x.extract() for x in data.find_all("span")]
        all_script_tags = [x.extract() for x in data.find_all("script")]
        all_br_tags = [x.extract() for x in data.find_all("br")]
        #list of all the quote contents
        quote = [str(child).strip() for child in data.children]
        quotes.append({
            "quote": "".join(quote)[:-1],
            "author": authorOrTitle
        })
    return quotes

def genre_scraper(genre):
    pg_number = int(random.random()*101)
    good_reads_url = f"https://www.goodreads.com/quotes/tag/{genre}?page={pg_number}"
    r = requests.get(good_reads_url)
    data = html_parser(r.text)
    return data

#converts bytes to python object
def get_image():
    pic_url = f"https://api.unsplash.com/photos/random?client_id={ACCESS_KEY}&count=30"
    r = requests.get(pic_url).json()
    img_list = []
    for img_dict in r:
        data = {}
        data['image_urls'] = img_dict['urls']
        data['image_author'] = img_dict['user']['username']
        data['image_author_instagram'] = img_dict['user']['instagram_username']
        img_list.append(data)

    return img_list


#returns response with correct format for the api along with the status code and content-type header
def response(data, code):
    image_data = get_image()
    return json.dumps({"data": {"quotes": data, "image_data": image_data}}), code, {"Content-Type": "application/json"}

#explains how to use the api, a simple documentation
@app.route("/")
def index():
    #documentation
    tools_dict = {
        "popular quotes": {
            "description": "get 30 random popular quotes from good reads along with 30 images",
            "usage": "/quotes/popular"
        },
        "quotes": {
            "description": "get 30 random quotes with your specified genre along with 30 images",
            "usage": "/quotes/<your genre of choice here>",
            "genres": [x for x in quotes_genre.keys()]
        },
        "random quotes": {
            "description": "get 30 random quotes of random genre given above along with 30 images",
            "usage": "/quotes",
        }
    }
    return response(tools_dict, 200)

@app.route('/quotes')
def random_quotes():
    genre = random.choice(list(quotes_genre.keys()))
    quotes = genre_scraper(genre)
    return response(quotes, 200)

#returns 10 random popular-quotes
@app.route('/quotes/popular')
def popular_quotes():
    pg_number = int(random.random()*101)
    good_reads_url = f"https://www.goodreads.com/quotes/?page={pg_number}"
    r = requests.get(good_reads_url)
    quotes = html_parser(r.text)
    return response(quotes, 200)

#returns 10 random quotes from a genre of your choice
@app.route('/quotes/<genre>')
def quotes(genre):
    if genre in quotes_genre.keys():
        data = genre_scraper(genre)
        return response(data, 200)
    else:
        err = {
            "data": f"genre {genre} not found, please use the genres mentioned in the api documentation at the root url"
        }
        return response(err, 400)

if __name__=="__main__":
    app.run(debug=True)
