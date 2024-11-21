from dbm import error

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Используйте нужный вам URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Создайте объект SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_city = db.Column(db.String(50), nullable=False)
    end_city = db.Column(db.String(50), nullable=False)
    data = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"User('{self.start_city}', '{self.end_city}', '{self.data}', '{self.phone}')"


with app.app_context():
    db.create_all()


@app.route('/')
def index():  # put application's code here
    strips = User.query.all()
    # print(f'Strips: {strips}')  # Отладки, чтобы увидеть, что передается в шаблон
    return render_template('index.html', strips=strips)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']
        data = request.form['data']
        phone = request.form['phone']
        strip = User(start_city=start_city, end_city=end_city, data=data, phone=phone)
        try:
            db.session.add(strip)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(e)
    else:
        return render_template('create.html')

@app.route('/poisk', methods=['GET', 'POST'])
def poisk():
    trip = None  # Инициализируем переменную для хранения информации о поездке
    error = None  # Инициализируем переменную для хранения ошибок

    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        # Проверка на наличие необходимых данных
        if not start_city or not end_city:
            error = "Пожалуйста, заполните оба поля."
        else:
            trip = User.query.filter_by(start_city=start_city, end_city=end_city).first()

            if trip is None:
                error = "Поездка не найдена"

    # Обработка данных для отдачи их обратно в шаблон
    return render_template('poisk.html', trip=trip, error=error)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        phone = request.form['phone']
        strip = User.query.filter_by(phone=phone).first()

        if strip is None:
            return render_template('delete.html', error="Пользователь не найден")

        try:
            db.session.delete(strip)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            # Логгируем ошибку для отладки
            print(f"Ошибка при удалении пользователя: {e}")
            db.session.rollback()  # Возврат назад, чтобы не оставить сессии в неправильном состоянии
            return render_template('delete.html', error="Произошла ошибка при удалении пользователя")
    else:
        return render_template('delete.html')


if __name__ == '__main__':
    app.run(debug=True)
