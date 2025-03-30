from flask import Blueprint, redirect, url_for, request, render_template, jsonify
from flask_login import current_user
from models.model import Quiz, Question, Chapter, Subject, Score, db
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
def dashboard():
    data = []

    # Fetch quizzes from the database along with the number of questions and the date
    quizzes = Quiz.query.all()

    for quiz in quizzes:
        # Get Chaper and Subject name
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        questions = Question.query.filter_by(quiz_id=quiz.id).all()

        item = dict()
        item.update(quiz.__dict__)
        item.update({
            "subject": subject.name,
            "chapter": chapter.name,
            "num_questions": len(questions)
        })

        data.append(item)

    if current_user.is_authenticated:
        return render_template("user/dashboard.html", user=current_user, quizzes=data)
    else:
        return redirect(url_for("auth.login"))


@user_bp.route("/view_quiz/<int:quiz_id>")
def view_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)

    data = dict()
    data.update(quiz.__dict__)
    data.update({
        "subject": subject.name,
        "chapter": chapter.name,
        "num_questions": len(questions)
    })

    if current_user.is_authenticated:
        return render_template("user/view_quiz.html", user=current_user, quiz=data)
    else:
        return redirect(url_for("auth.login"))


@user_bp.route("/take_quiz/<int:quiz_id>", methods=["GET", "POST"])
def take_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)

    # Check if the quiz is already taken by the user
    score = Score.query.filter_by(
        quiz_id=quiz_id, user_id=current_user.id).first()
    if score:
        return redirect(url_for("user.view_quiz", quiz_id=quiz_id))

    data = dict()
    data.update(quiz.__dict__)
    data.update({
        "subject": subject.name,
        "chapter": chapter.name,
        "num_questions": len(questions)
    })

    if request.method == "POST":
        # Get the body of the request
        # {'answers': {'3': 2, '4': -1, '5': 3, '6': 3}}
        answers = request.get_json()['answers']
        print(answers)
        score = 0

        # Calculate the score
        for question_id, answer in answers.items():
            question = Question.query.get(int(question_id))
            if question.correct_option == str(answer):
                score += 1

        # Ignore if score is already there
        score_exists = Score.query.filter_by(
            quiz_id=quiz_id, user_id=current_user.id).first()

        if score_exists:
            return jsonify({"score": score_exists.total_scored, "success": False})

        # Save the score in the database
        score = Score(quiz_id=quiz_id, user_id=current_user.id,
                      total_scored=score, time_stamp_of_attempt=datetime.now())

        # Add the score to the database session
        db.session.add(score)
        db.session.commit()

        return jsonify({"score": score.total_scored, "success": True})

    if current_user.is_authenticated:
        # Remove the correct_option key from the questions data
        questionsData = [{k: v for k, v in obj.items() if k != "correct_option"}
                         for obj in list(map(lambda x: x.as_dict(), questions))]

        return render_template("user/take_quiz.html", user=current_user, quiz=data, questions=questionsData)
    else:
        return redirect(url_for("auth.login"))


@user_bp.route("/scores")
def view_scores():
    data = []

    # Fetch scores from the database
    scores = Score.query.filter_by(user_id=current_user.id).all()

    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)

        item = dict()
        item.update(score.__dict__)
        item.update({
            "subject": subject.name,
            "chapter": chapter.name,
            "num_questions": len(Question.query.filter_by(quiz_id=quiz.id).all())
        })

        data.append(item)

    if current_user.is_authenticated:
        return render_template("user/view_scores.html", user=current_user, scores=data)
    else:
        return redirect(url_for("auth.login"))


@user_bp.route("/summary")
def summary():
    # Months wise number of quizzes taken
    months_wise_attempts = {}
    scores = Score.query.filter_by(user_id=current_user.id).all()
    for score in scores:
        month = score.time_stamp_of_attempt.strftime("%B")
        year = score.time_stamp_of_attempt.strftime("%Y")
        
        date = f"{month} {year}"

        if date in months_wise_attempts.keys():
            months_wise_attempts[date] += 1
        else:
            months_wise_attempts[date] = 1

    # Subject wise number of quizzes taken
    subject_wise_attempts = []
    subjects = Subject.query.all()
    for subject in subjects:
        quizzes_taken = 0

        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(
            [chapter.id for chapter in chapters])).all()
        for quiz in quizzes:
            score = Score.query.filter_by(
                quiz_id=quiz.id, user_id=current_user.id).first()
            if score:
                quizzes_taken += 1

        data = {
            "subject": subject.name,
            "quizzes_taken": quizzes_taken
        }

        subject_wise_attempts.append(data)

    if current_user.is_authenticated:
        return render_template("user/summary.html", user=current_user, months=months_wise_attempts, subjects=subject_wise_attempts)
    else:
        return redirect(url_for("auth.login"))


@user_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("search", "").strip()

    # Subjects
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()

    # Chapters
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    chapters_data = []
    for chapter in chapters:
        chapter_dict = chapter.as_dict()
        subject = Subject.query.filter_by(id=chapter.subject_id).first()
        if subject:  # Make sure the subject exists to prevent errors
            chapter_dict["subject"] = subject.name  # Access subject dict
        else:
            chapter_dict["subject"] = None
        chapters_data.append(chapter_dict)

    quizzes = Quiz.query.filter(Quiz.remarks.ilike(f"%{query}%")).all()
    quizzes_data = []
    for quiz in quizzes:
        quiz_dict = quiz.as_dict()
        chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
        subject = Subject.query.filter_by(id=chapter.subject_id).first()
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        if chapter:  # Make sure the chapter exists to prevent errors
            quiz_dict["chapter"] = chapter.name
        else:
            quiz_dict["chapter"] = None
        if subject:  # Make sure the subject exists to prevent errors
            quiz_dict["subject"] = subject.name
        else:
            quiz_dict["subject"] = None
        quiz_dict["num_questions"] = len(questions)
        quizzes_data.append(quiz_dict)

    if current_user.is_authenticated:
        return render_template("user/search.html", user=current_user, subjects=subjects, chapters=chapters_data, quizes=quizzes_data)
    else:
        return redirect(url_for("auth.login"))

