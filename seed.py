from dotenv import load_dotenv
load_dotenv()
from app import create_app
from extensions import db
from models import User, Survey, Question, Option, Response, Answer, AnswerOption
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    # Очистим таблицы
    db.session.query(AnswerOption).delete()
    db.session.query(Answer).delete()
    db.session.query(Response).delete()
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

    # Создаём несколько опросов с разными статусами
    surveys = []

    # 1. Черновик
    survey_draft = Survey(
        title="Опрос в черновике",
        description="Черновик опроса",
        author_id=user.id,
        status="draft"
    )
    surveys.append(survey_draft)

    # 2. Опубликованный
    survey_published = Survey(
        title="Опубликованный опрос",
        description="Этот опрос можно проходить",
        author_id=user.id,
        status="published",
        published_at=datetime.utcnow()
    )
    surveys.append(survey_published)

    # 3. Закрытый
    survey_closed = Survey(
        title="Закрытый опрос",
        description="Этот опрос уже закрыт",
        author_id=user.id,
        status="closed",
        published_at=datetime.utcnow(),
        closed_at=datetime.utcnow()
    )
    surveys.append(survey_closed)

    db.session.add_all(surveys)
    db.session.commit()

    # Добавляем вопросы к опубликованному опросу (для прохождения)
    q1 = Question(survey_id=survey_published.id, text="Как вас зовут?", type="text", sequence=1)
    q2 = Question(survey_id=survey_published.id, text="Выберите любимый цвет", type="single", sequence=2)
    q3 = Question(survey_id=survey_published.id, text="Выберите все подходящие фрукты", type="multiple", sequence=3)
    db.session.add_all([q1, q2, q3])
    db.session.commit()

    # Варианты для вопросов с выбором
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

    # Создаём респондента (пользователь, который проходит опрос)
    respondent = User(
        email="1respondent@example.com",
        password_hash=generate_password_hash("password123")
    )
    db.session.add(respondent)
    db.session.commit()

    print("Сидеры успешно добавлены!")
    print(f"Черновик: /surveys/{survey_draft.id}")
    print(f"Опубликованный: /surveys/{survey_published.id}")
    print(f"Закрытый: /surveys/{survey_closed.id}")
    print(f"Респондент: {respondent.email} / password123")