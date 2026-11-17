from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/d-day')
def d_day_detail():
    return render_template('d-day.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)