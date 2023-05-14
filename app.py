import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = '=&^+b7cf26151flh$f0+z=4!8&jorefnr%6srwc#t*ex^2o36n'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.sqlite3')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.sqlite3')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user_data = c.fetchone()
        conn.close()

        if user_data and user_data[2] == password:  # Убедитесь, что хэшируете пароли в реальных приложениях
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.sqlite3')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('registration.html')


posts = [
    {
        'id': 1,
        'title': 'Study tips for exams',
        'author': 'u/username',
        'published_at': '3 hours ago',
        'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'upvotes': 123,
        'comments': [
            {
                'author': 'u/username2',
                'content': 'Great tips!'
            }
        ]
    },
    {
        'id': 2,
        'title': 'My cat is too cute!',
        'author': 'u/catlover',
        'published_at': '1 day ago',
        'content': 'Everyone, look at my adorable cat!',
        'upvotes': 573,
        'comments': [
            {
                'author': 'u/doglover',
                'content': 'Cats are overrated.'
            },
            {
                'author': 'u/animalfriend',
                'content': 'What a sweet kitty!'
            }
        ]
    }
]


@app.route('/')
def index():
    for post in posts:
        post['comment_count'] = len(post['comments'])

    return render_template("index.html", posts=posts)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if post is None:
        return "Post not found.", 404

    post['comment_count'] = len(post['comments'])
    return render_template("post_detail.html", post=post)


if __name__ == '__main__':
    app.run(debug=True)
