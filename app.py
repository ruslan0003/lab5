import os
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from prettytable import PrettyTable

app = Flask(__name__)

# Настройка PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://postgres:postgres@db:5432/pg')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# db model
class Counter(db.Model):
    __tablename__ = 'counter'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime(timezone=True), default=datetime.now(ZoneInfo("Europe/Moscow")))
    client_info = db.Column(db.String(512))

    def __init__(self, client_info):
        self.client_info = client_info


# создание таблицы, если не существует
with app.app_context():
    db.create_all()


@app.route('/')
def hello():
    client_info = request.headers.get('User-Agent', 'Unknown')
    new_entry = Counter(client_info=client_info)
    db.session.add(new_entry)
    db.session.commit()

    total_hits = Counter.query.count()

    all_entries = Counter.query.all()

    table = PrettyTable()
    table.field_names = ["ID", "Дата и время", "Информация о клиенте"]
    for entry in all_entries:
        formatted_datetime = entry.datetime.strftime("%d%b%Y %H:%M:%S")
        table.add_row([entry.id, formatted_datetime, entry.client_info])

    table_html = table.get_html_string(attributes={"class": "table table-striped"})

    return f"""
        <div>
            <h1 class="color: blue; text-align: center">Количество кликов: {total_hits}</h1>
            {table_html}
        </div>
    """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5252)