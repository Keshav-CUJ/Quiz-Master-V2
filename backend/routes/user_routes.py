import os
from posixpath import basename
from flask import Blueprint, request, jsonify, send_from_directory, session, redirect, make_response, render_template
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Subject, Chapter, Quiz,Question, Score, QuestionStatus 
from datetime import datetime
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from flask_jwt_extended import jwt_required


user_routes = Blueprint('user_routes', __name__)



@user_routes.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400

    # Convert DOB string to a date object
    try:
        dob_date = datetime.strptime(data['dob'], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    # hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        qualification=data.get('qualification', ''),
        dob=dob_date,  # Now it is a proper date object
        role='user'
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201



@user_routes.route('/api/login/user', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.password == data['password']:
        access_token = create_access_token(identity="user", additional_claims={"role": "user", "username": user.username})
        return jsonify({
            "message": "User login successful",
            "access_token": access_token
        }), 200

    return jsonify({"message": "Invalid user credentials"}), 401



@user_routes.route("/api/chapters/by_subject", methods=["GET"])
@jwt_required()
def get_chapters_by_subject():
    subject_id = request.args.get("subject_id")
    if not subject_id:
        return jsonify([])

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    return jsonify([
        {"id": c.id, "name": c.name, "description": c.description, "subject_id": c.subject_id}
        for c in chapters
    ])


@user_routes.route("/api/quizzes/by_chapter", methods=["GET"])
@jwt_required()
def get_quizzes_by_chapter():
    chapter_id = request.args.get("chapter_id")
    if not chapter_id:
        return jsonify([])

    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    return jsonify([
        {
            "id": q.id,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.strftime("%Y-%m-%d"),
            "time_duration": q.time_duration,
            "remarks": q.remarks
        }
        for q in quizzes
    ])


@user_routes.route("/api/subjects", methods=["GET"])
@jwt_required()
def get_subjects():
    subjects = Subject.query.all()
    
    return jsonify([
        {"id": s.id, "name": s.name, "description": s.description}
        for s in subjects
    ])




@user_routes.route("/api/user/quiz/<int:quiz_id>", methods=["GET"])
@jwt_required()
def start_quiz(quiz_id):
    claims = get_jwt()
    username = claims.get("username")

    if not username:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    quiz = Quiz.query.get_or_404(quiz_id)

    existing_attempt = Score.query.filter_by(quiz_id=quiz_id, user_id=user.id).first()
    if existing_attempt:
        return jsonify({
            "message": "You have already attempted this quiz!",
            "attempted": True
        }), 403

    return jsonify({
        "quiz_id": quiz.id,
        "duration": quiz.time_duration,
        "attempted": False
    })

@user_routes.route("/api/questions/<int:quiz_id>", methods=["GET"])
@jwt_required()
def get_questions(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        return jsonify([])  # ✅ Return empty list if no questions exist

    return jsonify([
        {
            "id": q.id,
            "question_statement": q.question_statement,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "correct_option": q.correct_option
        }
        for q in questions
    ])



@user_routes.route("/api/submit_quiz/<int:quiz_id>", methods=["POST"])
@jwt_required()
def submit_quiz(quiz_id):
    claims = get_jwt()
    user = User.query.filter_by(username=claims["username"]).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    user_answers = data.get("answers", {})
    question_statuses = data.get("statuses", {})  # { question_id: status }
    user_timestamp = data.get("timestamp")

    try:
        attempt_time = datetime.fromisoformat(user_timestamp.replace("Z", ""))
    except ValueError:
        return jsonify({"message": "Invalid timestamp format"}), 400

    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    total_score = 0
    positive_mark = 1
    negative_mark = -0.25

    for question in questions:
        q_id = str(question.id)
        correct_option = question.correct_option
        chosen_option = int(user_answers.get(q_id, -1))
        status = question_statuses.get(q_id, "Not-Answered")

        # Calculate score
        if chosen_option == correct_option:
            total_score += positive_mark
        elif chosen_option != -1:
            total_score += negative_mark

        # Create or update QuestionStatus
        existing = QuestionStatus.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id,
            question_id=question.id
        ).first()

        if existing:
            existing.status = status
            existing.chosen_option = chosen_option
            existing.correct_option = correct_option
        else:
            db.session.add(QuestionStatus(
                user_id=user.id,
                quiz_id=quiz_id,
                question_id=question.id,
                status=status,
                chosen_option=chosen_option,
                correct_option=correct_option
            ))

    db.session.add(Score(
        quiz_id=quiz_id,
        user_id=user.id,
        timestamp=attempt_time,
        total_score=round(total_score, 2)
    ))
    db.session.commit()

    return jsonify({
        "message": "Quiz submitted!",
        "total_score": round(total_score, 2)
    })





from flask_jwt_extended import jwt_required, get_jwt

@user_routes.route("/api/user_attempted_quizzes")
@jwt_required()
def user_attempted_quizzes():
    claims = get_jwt()
    username = claims.get("username")

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # ✅ Get only scores (i.e., attempted quizzes) for the user
    scores = Score.query.filter_by(user_id=user.id).all()

    quiz_list = []
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if quiz:
            total_questions = len(quiz.questions)
            quiz_list.append({
                "id": quiz.id,
                "chapter": quiz.chapter.name,
                "subject": quiz.chapter.subject.name,
                "total_questions": total_questions,
                "score": score.total_score,
                "attempted": True
            })

    return jsonify({"quizzes": quiz_list})










@user_routes.route("/api/user/summary", methods=["GET"])
@jwt_required()
def user_summary_api():
    claims = get_jwt()
    username = claims.get("username")

    user = User.query.filter_by(username=username).first()
    
    user_id = user.id
    

    # Subject-wise Number of Quizzes Attempted
    quiz_count = (
        db.session.query(Subject.name, func.count(Score.quiz_id))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Score, (Quiz.id == Score.quiz_id) & (Score.user_id == user_id))
        .group_by(Subject.name)
        .all()
    )

    # Subject-wise Top Scores
    top_scores = (
        db.session.query(Subject.name, func.max(Score.total_score))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Score, (Quiz.id == Score.quiz_id) & (Score.user_id == user_id))
        .group_by(Subject.name)
        .all()
    )

    

    return jsonify({
        "quiz_count": [{"subject": q[0], "count": q[1]} for q in quiz_count],
        "top_scores": [{"subject": s[0], "score": s[1]} for s in top_scores],
            })
    
    
################Async CSV Export API#####################
@user_routes.route("/api/user/export-csv", methods=["POST"])
@jwt_required()
def export_csv():
    from task import export_user_csv
   
    user_id = User.query.filter_by(username=get_jwt().get("username")).first().id
    task = export_user_csv.delay(user_id)
    return jsonify({"task_id": task.id}), 202


@user_routes.route("/api/user/export-status/<task_id>")
def export_status(task_id):
    from task import celApp
    result = celApp.AsyncResult(task_id)
    if result.state == 'SUCCESS':
        return jsonify({
            "status": "SUCCESS",
            "download_url": f"/{result.result}"  # e.g., /static/exports/user_5_quiz_export.csv
        })
    return jsonify({"status": result.state})


@user_routes.route("/download/<filename>")
def download_csv_file(filename):
    export_dir = os.path.join(os.getcwd(), "static", "exports")
    return send_from_directory(export_dir, filename, as_attachment=True)