# app.py
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 简单的密钥

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('analysis.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == 'xxx':
        session['logged_in'] = True
        return redirect('/analysis')
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/analysis')
def analysis():
    if 'logged_in' not in session:
        return redirect('/')
    return render_template('analysis.html')

if __name__ == '__main__':
    app.run(debug=True)