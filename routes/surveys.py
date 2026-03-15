from flask import Blueprint, request, jsonify
from extensions import db
from models import Survey, User, Answer, Question, Option, Response, AnswerOption
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

surveys_bp = Blueprint("surveys", __name__, url_prefix="/surveys")

@surveys_bp.post("/")
@jwt_required()
def create_survey():
    user_id = int(get_jwt_identity())  # авторизация пользователя
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return {"error": "Title is required"}, 400

    survey = Survey(title=title, description=description, author_id=user_id)
    db.session.add(survey)
    db.session.commit()

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "status": survey.status
    }), 201

@surveys_bp.get("/")
@jwt_required()
def get_surveys():
    user_id = int(get_jwt_identity())
    surveys = Survey.query.filter_by(author_id=user_id).all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "description": s.description,
        "status": s.status
    } for s in surveys])

@surveys_bp.get("/<int:survey_id>")
@jwt_required()
def get_survey(survey_id):
    user_id = int(get_jwt_identity())
    survey = Survey.query.filter_by(id=survey_id, author_id=user_id).first()
    if not survey:
        return {"error": "Survey not found"}, 404

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "status": survey.status
    })

@surveys_bp.put("/<int:survey_id>")
@jwt_required()
def update_survey(survey_id):
    user_id = int(get_jwt_identity())
    survey = Survey.query.filter_by(id=survey_id, author_id=user_id).first()

    if not survey:
        return {"error": "Survey not found"}, 404

    if survey.status != "draft":
        return {"error": "Only draft surveys can be edited"}, 400

    data = request.get_json()
    survey.title = data.get("title", survey.title)
    survey.description = data.get("description", survey.description)
    db.session.commit()

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "status": survey.status
    })

@surveys_bp.delete("/<int:survey_id>")
@jwt_required()
def delete_survey(survey_id):
    user_id = int(get_jwt_identity())
    survey = Survey.query.filter_by(id=survey_id, author_id=user_id).first()

    if not survey:
        return {"error": "Survey not found"}, 404

    db.session.delete(survey)
    db.session.commit()
    return {"message": "Survey deleted"}


@surveys_bp.post("/<int:survey_id>/publish")
@jwt_required()
def publish_survey(survey_id):
    user_id = int(get_jwt_identity())
    survey = Survey.query.filter_by(id=survey_id, author_id=user_id).first()

    if not survey:
        return {"error": "Survey not found"}, 404

    if survey.status != "draft":
        return {"error": "Only draft surveys can be published"}, 400

    survey.status = "published"
    survey.published_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "id": survey.id,
        "status": survey.status,
        "published_at": survey.published_at
    })

@surveys_bp.post("/<int:survey_id>/close")
@jwt_required()
def close_survey(survey_id):
    user_id = int(get_jwt_identity())
    survey = Survey.query.filter_by(id=survey_id, author_id=user_id).first()

    if not survey:
        return {"error": "Survey not found"}, 404

    if survey.status != "published":
        return {"error": "Only published surveys can be closed"}, 400

    survey.status = "closed"
    survey.closed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "id": survey.id,
        "status": survey.status,
        "closed_at": survey.closed_at
    })

@surveys_bp.get("/<int:survey_id>/take")
@jwt_required()
def take_survey(survey_id):

    survey = Survey.query.filter_by(id=survey_id, status="published").first()

    if not survey:
        return {"error": "Survey not found or not published"}, 404

    questions_data = []

    for q in sorted(survey.question, key=lambda x: x.sequence):

        options = sorted(q.options, key=lambda x: x.position)

        questions_data.append({
            "id": q.id,
            "text": q.text,
            "type": q.type,
            "sequence": q.sequence,
            "options": [
                {
                    "id": o.id,
                    "text": o.text,
                    "position": o.position
                }
                for o in options
            ]
        })

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "questions": questions_data
    })

@surveys_bp.post("/<int:survey_id>/responses")
@jwt_required()
def submit_response(survey_id):
    user_id = int(get_jwt_identity())

    # Только опубликованные опросы
    survey = Survey.query.filter_by(id=survey_id, status="published").first()
    if not survey:
        return {"error": "Survey not found or not published"}, 404

    data = request.get_json()
    answers_data = data.get("answers")
    print(answers_data)
    if not isinstance(answers_data, list) or not answers_data:
        return {"error": "Invalid or empty answers list"}, 400

    # Проверка, что пользователь ещё не отправлял ответы
    existing = Response.query.filter_by(survey_id=survey_id, user_id=user_id).first()
    if existing:
        return {"error": "You have already submitted this survey"}, 400

    # Создаём Response
    response = Response(survey_id=survey_id, user_id=user_id)
    db.session.add(response)
    db.session.flush()  # чтобы получить response.id

    for ans in answers_data:
        question_id = ans.get("question_id")
        question = Question.query.get(question_id)
        if not question or question.survey_id != survey_id:
            db.session.rollback()
            return {"error": f"Question {question_id} not found in this survey"}, 400

        answer = Answer(response_id=response.id, question_id=question_id)

        if question.type == "text":
            text_answer = ans.get("text_answer")
            if not text_answer:
                db.session.rollback()
                return {"error": f"Text answer required for question {question_id}"}, 400
            answer.text_answer = text_answer
            db.session.add(answer)

        elif question.type == "single":
            option_ids = ans.get("option_ids")
            if not option_ids or len(option_ids) != 1:
                db.session.rollback()
                return {"error": f"Single choice question {question_id} requires exactly 1 option"}, 400

            option = Option.query.filter_by(id=option_ids[0], question_id=question_id).first()
            if not option:
                db.session.rollback()
                return {"error": f"Invalid option {option_ids[0]} for question {question_id}"}, 400

            db.session.add(answer)
            db.session.flush()
            db.session.add(AnswerOption(answer_id=answer.id, option_id=option.id))

        elif question.type == "multiple":
            option_ids = ans.get("option_ids")
            if not option_ids or not isinstance(option_ids, list):
                db.session.rollback()
                return {"error": f"Multiple choice question {question_id} requires option_ids list"}, 400

            db.session.add(answer)
            db.session.flush()
            for oid in option_ids:
                option = Option.query.filter_by(id=oid, question_id=question_id).first()
                if not option:
                    db.session.rollback()
                    return {"error": f"Invalid option {oid} for question {question_id}"}, 400
                db.session.add(AnswerOption(answer_id=answer.id, option_id=option.id))

        else:
            db.session.rollback()
            return {"error": f"Unknown question type for question {question_id}"}, 400

    db.session.commit()
    return {"message": "Response submitted successfully"}