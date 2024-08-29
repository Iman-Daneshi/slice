import os

from dotenv import load_dotenv
from flask import Flask,request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
import random
import string
load_dotenv()

app =Flask(__name__)
app.debug = os.getenv("FLASK_DEBUG")

url = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = url

db=SQLAlchemy(app)
migrate = Migrate(app, db)


class Url(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    long_url = db.Column(db.String(200), nullable=False)
    short_url = db.Column(db.String(200), nullable=False)


def generate_short_url(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get('url')
    
    if not long_url:
        return jsonify({"detail": "Invalid input"}), 400
    
    url_record = Url.query.filter_by(long_url=long_url).first()
    if url_record:
        return jsonify({
            "long_url": url_record.long_url,
            "short_url": url_record.short_url
        }), 200

    short_url = "https://www.tinyslice.com/"+ generate_short_url()
    while Url.query.filter_by(short_url=short_url).first():
        short_url = generate_short_url()  # Ensure uniqueness

    new_url = Url(long_url=long_url, short_url=short_url)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        "long_url": new_url.long_url,
        "short_url": new_url.short_url
    }), 201

@app.route('/fetch', methods=['POST'])
def fetch_url():
    data = request.get_json()
    short_url = data.get('url')
    
    if not short_url:
        return jsonify({"detail": "Invalid input"}), 400
    
    url_record = Url.query.filter_by(short_url=short_url).first()
    if url_record:
        return jsonify({
            "long_url": url_record.long_url,
            "short_url": url_record.short_url
        }), 200

    return jsonify({"detail": "Couldn't find any record"}), 404

if __name__ == '__main__':
    app.run(debug=True)

