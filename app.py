# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, request
import logging
from logging import Formatter, FileHandler

from pymongo import MongoClient

from forms import *
import os

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
client = MongoClient('mongodb://localhost:27017')
db = client['development']

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
PERIODS = {
    'rate_day': '1 Day',
    'rate_week_1': '1 Week',
    'rate_weeks_2': '2 Weeks',
    'rate_month_1': '1 Month',
    'rate_months_2': '2 Months',
    'rate_months_3': '3 Months',
    'rate_months_4': '4 Months',
    'rate_months_5': '5 Months',
    'rate_months_6': '6 Months',
    'rate_months_7': '7 Months',
    'rate_months_8': '8 Months',
    'rate_months_9': '9 Months',
    'rate_months_10': '10 Months',
    'rate_months_11': '11 Months',
    'rate_months_12': '12 Months',
}

PERCENTAGE = 100
MONTHS = 12


@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    contexts = {
        'amount_requested': 0,
        'period': '',
        'periods': PERIODS,
        'results': results
    }
    if request.method == 'POST':
        amount_requested = int(request.form['amount'])
        period = request.form['period']

        rates = db.rates.find()
        for rate in rates:
            try:
                range_amounts = rate['rates'][period]
                result = dict()
                for amount, interest_rated in range_amounts:
                    if amount_requested <= amount:
                        result['interest_rated'] = interest_rated
                        result['interest_earned'] = round(interest_rated * amount_requested / PERCENTAGE / MONTHS, 2)
                        result['amount_requested'] = amount_requested
                        result['bank_name'] = rate['bank_name']
                        result['period'] = period
                        break

                if result != {}:
                    results.append(result)
            except KeyError:
                pass

        results = [] if results == [] else sorted(results, key=lambda k: k['interest_earned'], reverse=True)

        contexts['amount_requested'] = amount_requested
        contexts['period'] = period
        contexts['results'] = results[1:]
        contexts['best_result'] = results[:1]
    return render_template('pages/placeholder.home.html', **contexts)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)


# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
