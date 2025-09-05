import csv
from datetime import datetime
from email.mime.application import MIMEApplication
from tempfile import NamedTemporaryFile
from celery import Celery
from celery.schedules import crontab
import  smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from app import  create_app
from database import User, Score, Quiz, Chapter, Subject, Question, QuestionStatus

import time
celApp= Celery('tasks', broker='redis://127.0.0.1:6379/1', backend='redis://127.0.0.1:6379/1')
celApp.conf.enable_utc=False
celApp.conf.timezone='Asia/Kolkata'

@celApp.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=17,minute=11),
        send_unattempted_quiz_reminders.s()
    )
    sender.add_periodic_task(
        crontab(day_of_month=30, hour=17, minute=11),  # adjust time as needed
        send_monthly_summary.s()
    )
    
    
###for sceduled tasks and batch jobs    
@celApp.task
def send_unattempted_quiz_reminders():
    app = create_app()
    with app.app_context():
        users = User.query.filter_by(role='user').all()
        quizzes = Quiz.query.all()

        for user in users:
            attempted_ids = {s.quiz_id for s in Score.query.filter_by(user_id=user.id)}
            unattempted = [q for q in quizzes if q.id not in attempted_ids]

            if not unattempted:
                continue

            message = f"Hi {user.username},\n\nYou have unattempted quizzes:\n\n"
            for quiz in unattempted:
                message += f"- {quiz.chapter.subject.name} → {quiz.chapter.name} | Quiz ID: {quiz.id}, Date: {quiz.date_of_quiz.date()}\n"

            message += "\nPlease log in and complete them!\n"

            send_email("<your_email>",user.email, "📚 Unattempted Quizzes Reminder", message,"quiz.png")


@celApp.task
def send_monthly_summary():
        app = create_app()
        with app.app_context():
            users = User.query.filter_by(role='user').all()

            for user in users:
              html_content = generate_summary_html(user)
        # Save HTML content to a temp file
              with NamedTemporaryFile(mode='w+', suffix='.html', delete=False,encoding='utf-8') as tmp:
                tmp.write(html_content)
                tmp_path = tmp.name
            
                
                
              month_name = datetime.now().strftime("%B")  
              message = f"Hi {user.username},\nYour quizz summary report for {month_name} month is here.\nPlease find the attachment.\n\n Regards\n Admin from Quiz Master"
              send_email("<your_email>",user.email, "📊 Your Monthly Quiz Summary Report", message,tmp_path)
 
@celApp.task(bind=True)
def export_user_csv(self, user_id):
    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        scores = Score.query.filter_by(user_id=user_id).all()

        output_path = f"static/exports/user_{user_id}_quiz_export.csv"
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username","quiz_id", "chapter_name", "subject_name", "date_of_quiz", "total_score", "remarks"])
            for score in scores:
                quiz = score.quiz
                chapter = quiz.chapter
                subject = chapter.subject
                writer.writerow([
                    user.username,
                    quiz.id,
                    chapter.name,
                    subject.name,
                    quiz.date_of_quiz.strftime('%Y-%m-%d'),
                    score.total_score,
                    quiz.remarks or ""
                ])
        return output_path




def generate_summary_html(user):
    quiz_blocks_html = ""

    # Get all scores (attempted quizzes)
    scores = Score.query.filter_by(user_id=user.id).all()

    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = quiz.chapter
        subject = chapter.subject
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        
        question_rows = ""
        for i, question in enumerate(questions, start=1):
            q_status = QuestionStatus.query.filter_by(user_id=user.id, quiz_id=quiz.id, question_id=question.id).first()

            selected_option = q_status.chosen_option if q_status and q_status.chosen_option != -1 else "—"
            correct_option = question.correct_option
            status = q_status.status if q_status else "Not-Answered"

            status_class = {
                'Answered': 'status-answered',
                'Marked-for-Review': 'status-marked',
                'Not-Answered': 'status-not'
            }.get(status, 'status-not')

            question_rows += f"""
            <tr>
              <td>{i}</td>
              <td>{question.question_statement}</td>
              <td>{selected_option}</td>
              <td>{correct_option}</td>
              <td class="{status_class}">{status}</td>
            </tr>
            """

        quiz_blocks_html += f"""
        <div class="quiz-block">
          <h3> {subject.name} → {chapter.name}</h3>
          <p><strong>Quiz ID:</strong> {quiz.id} | <strong>Date:</strong> {quiz.date_of_quiz.strftime('%Y-%m-%d')} | <strong>Score:</strong> {score.total_score}</p>

          <table class="question-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Question</th>
                <th>Selected Option</th>
                <th>Correct Option</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {question_rows}
            </tbody>
          </table>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Monthly Quiz Summary Report</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
        h1, h2 {{ color: #2c3e50; }}
        .user-info, .quiz-summary {{ margin-bottom: 20px; }}
        .quiz-block {{ border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .question-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .question-table th, .question-table td {{
          border: 1px solid #ccc; padding: 8px; text-align: left;
        }}
        .question-table th {{ background-color: #f9f9f9; }}
        .status-answered {{ color: green; font-weight: bold; }}
        .status-marked {{ color: orange; font-weight: bold; }}
        .status-not {{ color: red; font-weight: bold; }}
      </style>
    </head>
    <body>
      <h1> Monthly Quiz Summary Report</h1>

      <div class="user-info">
        <h2>User Info</h2>
        <p><strong>Name:</strong> {user.full_name or "N/A"}</p>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
      </div>

      <div class="quiz-summary">
        <h2>Attempted Quizzes</h2>
        {quiz_blocks_html or "<p>No attempted quizzes yet.</p>"}
      </div>
    </body>
    </html>
    """

    return html_template


def send_email(sender,receiver, subject, message, attachment):
    msg=MIMEMultipart()
    msg['From']= sender
    msg['To']= receiver
    msg['Subject']=subject
    msg.attach(MIMEText(message))
    filename=attachment
    path =os.path.join(os.getcwd(),filename)
    with open(path, 'rb') as f:
        attachment=MIMEApplication(f.read(),_subtype='octet-stream')
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment)
    smtp_server='smtp.gmail.com'
    smtp_port=587
    smtp_username=sender
    smtp_password='<your_app_password>'
    
    with smtplib.SMTP(smtp_server,smtp_port) as server:
        server.starttls()
        server.login(smtp_username,smtp_password)
        server.sendmail(sender, receiver, msg.as_string())