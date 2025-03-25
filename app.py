from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/timeshare')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    resort = db.Column(db.String(200))

@app.route('/')
def index():
    return render_template('index.html')

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1354005871906000978/mM84gZcicf1OsaRHVIUwSSjEjZrU1OE5CQHq-W7yVR-3YgjGpiEIQtvu3OwYH_gLv4XW"

def send_discord_notification(submission):
    """Send lead notification to Discord webhook"""
    message = f"New lead submission!\n"
    message += f"Name: {submission.first_name} {submission.last_name}\n"
    message += f"Email: {submission.email}\n"
    message += f"Phone: {submission.phone}\n"
    message += f"Resort: {submission.resort or 'Not specified'}"
    
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Failed to send Discord notification: {str(e)}")

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        submission = Submission(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data['phone'],
            resort=data.get('resort', '')
        )
        db.session.add(submission)
        db.session.commit()
        
        # Send Discord notification
        send_discord_notification(submission)
        
        return jsonify({'success': True, 'id': submission.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
