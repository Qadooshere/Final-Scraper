from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from main import GoogleScraper
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)
scraper = GoogleScraper()

# Initialize SQLite database
def init_db():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT)")
        conn.commit()


init_db()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/email_scraper')
def email_scraper():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM links")
        links = [row[0] for row in cursor.fetchall()]
    return render_template("email_scraper.html", links=links)

@app.route('/store_links', methods=['POST'])
def store_links():
    links = request.json.get('links', [])
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM links")  # Clear previous links
        cursor.executemany("INSERT INTO links (url) VALUES (?)", [(link,) for link in links])
        conn.commit()
    return "OK"

@socketio.on('start_scraping')
def start_scraping(data):
    query = data['query']
    num_pages = int(data['num_pages'])
    country = data['country']
    language = data['language']

    results_generator = scraper.scrape_generator(query, num_pages, country, language)

    for page_results in results_generator:
        emit('new_results', page_results)


if __name__ == '__main__':
    socketio.run(app, debug=True)
