from dotenv import load_dotenv
load_dotenv()
from app import create_app
from extensions import db
from models import User, Survey, Question, Option
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    # Очистим таблицы
    db.session.query(Option).delete()
    db.session.query(Question).delete()
    db.session.query(Survey).delete()
    db.session.query(User).delete()
    db.session.commit()

    # Создаём тестового пользователя
    user = User(
        email="test@example.com",
        password_hash=generate_password_hash("password123")
    )
    db.session.add(user)
    db.session.commit()

    # Создаём тестовый опрос
    survey = Survey(
        title="Тестовый опрос",
        description="Описание тестового опроса",
        author_id=user.id
    )
    db.session.add(survey)
    db.session.commit()

    # Добавляем вопросы
    q1 = Question(
        survey_id=survey.id,
        text="Как вас зовут?",
        type="text",
        sequence=1
    )
    q2 = Question(
        survey_id=survey.id,
        text="Выберите любимый цвет",
        type="single",
        sequence=2
    )
    q3 = Question(
        survey_id=survey.id,
        text="Выберите все подходящие фрукты",
        type="multiple",
        sequence=3
    )
    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # Добавляем варианты к вопросам с выбором
    options_q2 = [
        Option(question_id=q2.id, text="Красный", position=1),
        Option(question_id=q2.id, text="Синий", position=2),
        Option(question_id=q2.id, text="Зелёный", position=3)
    ]

    options_q3 = [
        Option(question_id=q3.id, text="Яблоко", position=1),
        Option(question_id=q3.id, text="Банан", position=2),
        Option(question_id=q3.id, text="Апельсин", position=3)
    ]

    db.session.add_all(options_q2 + options_q3)
    db.session.commit()

    print("Сидеры успешно добавлены!")