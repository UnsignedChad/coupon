from flask import Flask, jsonify
from flask_cors import CORS
import random
import datetime
import os
import json

app = Flask(__name__)
CORS(app)  # This will allow cross-origin requests

# Define the coupon pool
coupons = [f"coupon{i}" for i in range(1, 15)]

# File to store the selected coupon days and coupons for the week
WEEKLY_FILE = 'weekly_coupons.json'


def load_weekly_data():
    """Load the persisted coupons and selected days for the week."""
    if os.path.exists(WEEKLY_FILE):
        with open(WEEKLY_FILE, 'r') as f:
            data = json.load(f)
            return data.get('coupons'), data.get('selected_days'), data.get('week_start')
    return None, None, None


def save_weekly_data(coupons, selected_days, week_start):
    """Save the selected days, coupons, and the current week's start date to a file."""
    with open(WEEKLY_FILE, 'w') as f:
        json.dump({'coupons': coupons, 'selected_days': selected_days, 'week_start': week_start}, f)


def get_weekly_coupons():
    """Select 2 random days and corresponding coupons for the week if needed."""
    today = datetime.datetime.today()
    week_start = today - datetime.timedelta(days=today.weekday())  # Get the start of the week (Monday)
    week_start_str = week_start.strftime('%Y-%m-%d')

    # Load persisted data
    saved_coupons, saved_days, saved_week_start = load_weekly_data()

    # If the saved week is still valid, return the saved coupons and days
    if saved_week_start == week_start_str:
        return saved_coupons, saved_days

    # Otherwise, select 2 random days (Monday to Friday) and 2 random coupons for the new week
    selected_days = sorted(random.sample(range(0, 5), 2))  # Randomly pick 2 weekdays (0 = Monday, 4 = Friday)
    selected_coupons = [random.choice(coupons) for _ in selected_days]  # Pick a coupon for each selected day

    # Persist the selected days and coupons for the week
    save_weekly_data(selected_coupons, selected_days, week_start_str)

    return selected_coupons, selected_days


@app.route('/')
def serve_coupon():
    """Serve the coupon for today if it's one of the selected days; otherwise, return 'No coupon today'."""
    today = datetime.datetime.today().weekday()  # Monday = 0, Sunday = 6
    selected_coupons, selected_days = get_weekly_coupons()

    if today in selected_days:
        # Return the coupon for today's index in the selected_days list
        coupon = selected_coupons[selected_days.index(today)]
        return jsonify({"coupon": coupon})
    else:
        # It's not a coupon day
        return jsonify({"coupon": "No coupon today"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
