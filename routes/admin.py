from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from functools import wraps, reduce
from flask_login import current_user
from models.model import db, Subject, Chapter, Quiz, Question, Score, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Decorator to define the route for the admin dashboard
def login_admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # Check if the user is an admin
        if not current_user.role == "admin":
            return redirect(url_for('dashboard'))

        return func(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_admin_required
def dashboard():
    return render_template("admin/index.html", user=current_user)


@admin_bp.route('/quizes')
@login_admin_required
def quizes():
    quizzes = Quiz.query.order_by(Quiz.date_of_quiz).all()

    quizzes_data = []
    for quiz in quizzes:
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        quiz_data = {
            'id': quiz.id,
            'date_of_quiz': quiz.date_of_quiz,
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'chapter': Chapter.query.filter_by(id=quiz.chapter_id).first(),
            'questions': [q for q in questions]
        }
        quizzes_data.append(quiz_data)

    return render_template('admin/quizes.html', user=current_user, quizzes=quizzes_data, all=True)


@admin_bp.route('/quizes/<int:chapter_id>')
@login_admin_required
def quizes_by_chapter(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    quizzes = Quiz.query.filter_by(
        chapter_id=chapter_id).group_by(Quiz.date_of_quiz).all()

    quizzes_data = []
    for quiz in quizzes:
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        quiz_data = {
            'id': quiz.id,
            'date_of_quiz': quiz.date_of_quiz,
            'time_duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'chapter': chapter,
            'questions': [q for q in questions]
        }
        quizzes_data.append(quiz_data)

    return render_template('admin/quizes.html', user=current_user, chapter=chapter, quizzes=quizzes_data)


@admin_bp.route('/new-subject', methods=['GET', 'POST'])
@login_admin_required
def new_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Check if the subject already exists
        subject = Subject.query.filter_by(name=name).first()
        if subject:
            return render_template('admin/new_subject.html', user=current_user, errors=['Subject already exists'])

        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/new_subject.html', user=current_user)


@admin_bp.route('/new-chapter/<int:subject_id>', methods=['GET', 'POST'])
@login_admin_required
def new_chapter(subject_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Check if the chapter already exists
        chapter = Chapter.query.filter_by(name=name).first()
        if chapter:
            return render_template('admin/new_chapter.html', user=current_user, errors=['Chapter already exists'], subject_id=subject_id)

        chapter = Chapter(name=name, description=description,
                          subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/new_chapter.html', user=current_user, subject_id=subject_id)


@admin_bp.route('/delete-chapter/<int:chapter_id>', methods=['GET'])
@login_admin_required
def delete_chapter(chapter_id):
    # Delete the chapter along with all the quizzes and questions and scores associated with it
    chapter = Chapter.query.filter_by(
        id=chapter_id).first()
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    for quiz in quizzes:
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        for question in questions:
            db.session.delete(question)

        scores = Score.query.filter_by(
            quiz_id=quiz.id, user_id=current_user.id).all()
        for score in scores:
            db.session.delete(score)
        db.session.delete(quiz)
    db.session.delete(chapter)

    db.session.commit()

    return redirect(url_for('admin.index'))


@admin_bp.route('/new-quiz/<int:chapter_id>', methods=['GET', 'POST'])
@login_admin_required
def new_quiz(chapter_id):
    if request.method == 'POST':
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']

        quiz = Quiz(chapter_id=chapter_id, date_of_quiz=datetime.strptime(
            date_of_quiz, '%Y-%m-%d'),
            time_duration=time_duration, remarks=remarks)
        db.session.add(quiz)
        db.session.commit()

        return redirect(url_for('admin.quizes_by_chapter', chapter_id=chapter_id))

    chapter = Chapter.query.filter_by(id=chapter_id).first()
    return render_template('admin/new_quiz.html', user=current_user, chapter_id=chapter_id, chapter=chapter)


@admin_bp.route('/new-question/<int:quiz_id>', methods=['GET', 'POST'])
@login_admin_required
def new_question(quiz_id):
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        correct_option = request.form['correct_option']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']

        question = Question(quiz_id=quiz_id, question_statement=question_statement,
                            correct_option=correct_option, option1=option1, option2=option2, option3=option3, option4=option4)
        db.session.add(question)
        db.session.commit()

        return redirect(url_for('admin.new_question', quiz_id=quiz_id))

    quiz = Quiz.query.filter_by(id=quiz_id).first()
    chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
    return render_template('admin/new_question.html', user=current_user, quiz=quiz, chapter=chapter)


@admin_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
@login_admin_required
def edit_question(question_id):
    question = Question.query.filter_by(
        id=question_id).first()

    if request.method == 'POST':
        question_statement = request.form['question_statement']
        correct_option = request.form['correct_option']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']

        question.question_statement = question_statement
        question.correct_option = correct_option
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4

        db.session.commit()

        # Go back to the quiz
        return redirect(url_for('admin.quizes_by_chapter', chapter_id=Quiz.query.filter_by(id=question.quiz_id).first().chapter_id))

    quiz = Quiz.query.filter_by(id=question.quiz_id).first()
    chapter = Chapter.query.filter_by(id=quiz.chapter_id).first()
    return render_template('admin/edit_question.html', user=current_user, quiz=quiz, chapter=chapter, question=question)


@admin_bp.route('/delete-question/<int:question_id>', methods=['GET'])
@login_admin_required
def delete_question(question_id):
    question = Question.query.filter_by(
        id=question_id).first()
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()

    return redirect(request.referrer)


@admin_bp.route('/summary')
@login_admin_required
def summary():
    scores = Score.query.filter_by(user_id=current_user.id).all()

    summary_data = []

    # Get all the subjects
    subjects = Subject.query.all()
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        quizs = Quiz.query.filter(Quiz.chapter_id.in_(
            [chapter.id for chapter in chapters])).all()
        scores = Score.query.filter(Score.quiz_id.in_(
            [quiz.id for quiz in quizs])).all()

        summary_data.append({
            'subject': {
                'name': subject.name,
                'description': subject.description
            },
            'top_scores': reduce(lambda a, b: a if a > b else b, [score.total_scored for score in scores], 0),
            'user_attempts': len(scores)
        })

    return render_template('admin/summary.html', user=current_user, summary_data=summary_data)


@admin_bp.route("/search", methods=["GET"])
@login_admin_required
def search():
    query = request.args.get("search", "").strip()

    # Users
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()

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
        return render_template("admin/search.html", user=current_user, users=users, subjects=subjects, chapters=chapters_data, quizes=quizzes_data)
    else:
        return redirect(url_for("auth.login"))
