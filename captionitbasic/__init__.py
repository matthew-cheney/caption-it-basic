from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/caption_it.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Caption(db.Model):
    id = db.Column(db.String(64), nullable=False, primary_key=True)
    caption = db.Column(db.String(64), nullable=False)

class Game(db.Model):
    id = db.Column(db.String(64), nullable=False, primary_key=True)
    all_captions_in = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    create_game()
    if all_captions_in():
        return redirect(url_for('review'))
    return render_template('home.html')

@app.route('/addcaption', methods=['POST'])
def add_caption():
    caption = request.form.get('caption')
    add_caption_to_db(caption)
    return redirect(url_for('waiting'))

@app.route('/waiting')
def waiting():
    if all_captions_in():
        return redirect(url_for('review'))
    return render_template('waiting.html')

@app.route('/allin', methods=['POST'])
def all_in():
    set_all_captions_in()
    return redirect(url_for('review'))

@app.route('/review', methods=['GET'])
def review():
    all_captions = get_all_captions()
    return render_template('review.html', captions=all_captions)


@app.route('/newturn', methods=['POST'])
def new_turn():
    clear_captions()
    return redirect(url_for('home'))


def clear_captions():
    db.session.query(Caption).delete()
    game = db.session.query(Game).first()
    if game is None:
        db.session.add(Game(id=uuid.uuid4().hex))
    game.all_captions_in = False
    db.session.commit()

def add_caption_to_db(caption):
    db.session.add(Caption(id=uuid.uuid4().hex, caption=caption))
    db.session.commit()

def all_captions_in():
    game = db.session.query(Game).first()
    if game is None:
        return False
    return game.all_captions_in

def get_all_captions():
    return db.session.query(Caption).all()

def set_all_captions_in():
    game = db.session.query(Game).first()
    game.all_captions_in = True
    db.session.commit()

def create_game():
    game = db.session.query(Game).first()
    if game is None:
        db.session.add(Game(id=uuid.uuid4().hex))
        db.session.commit()
