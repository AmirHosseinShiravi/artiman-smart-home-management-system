from flask import Flask, render_template
from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins=['192.168.18.232:9000', 'http://192.168.18.232:5000'])


c = 0
@app.route('/')
def index():
    global c
    c+= 1
    # return render_template('modal.html', **{'c':c})
    # return render_template('4-state-button.html', **{'c':c})
    return render_template('hettra-sudo-android.html')
    # return render_template('test.html')
    # return render_template('hettra-sudo-android-with-stack-thermostat-card.html')

@app.route('/1')
def index1():

    return render_template('modal2.html')


if __name__ == '__main__':
    app.run(host="192.168.201.232", port=5000,debug=True)
    # app.run(host="192.168.50.232", port=5000,debug=True, ssl_context=('cert.pem', 'key.pem'))