from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'
    userId = db.Column(db.String(12), primary_key=True)
    passwd = db.Column(db.String(255), nullable=False)
    userName = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.passwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwd, password)

class ProjectExp(db.Model):
    __tablename__ = 'ProjectExp'
    expId = db.Column(db.Integer, primary_key=True)
    devLanguage = db.Column(db.String(50))
    framework = db.Column(db.String(50))
    detail = db.Column(db.Text)
    userId = db.Column(db.String(12), db.ForeignKey('User.userId'))

class JobExperience(db.Model):
    __tablename__ = 'JobExperience'
    jobExperienceId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(12), db.ForeignKey('User.userId'))
    companyName = db.Column(db.String(256))
    role = db.Column(db.String(128))
    jobDescription = db.Column(db.Text)
    startDate = db.Column(db.Date)
    endDate = db.Column(db.Date)

class Education(db.Model):
    __tablename__ = 'Education'
    educationId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(12), db.ForeignKey('User.userId'))
    schoolName = db.Column(db.String(256))
    degree = db.Column(db.String(128))
    fieldOfStudy = db.Column(db.String(256))
    startDate = db.Column(db.Date)
    endDate = db.Column(db.Date)

class Interview(db.Model):
    __tablename__ = 'Interview'
    interviewId = db.Column(db.Integer, primary_key=True)
    interviewSetId = db.Column(db.Integer, db.ForeignKey('InterviewSet.interviewSetId'))
    interviewStartTime = db.Column(db.DateTime)
    interviewSequence = db.Column(db.Integer)

class InterviewSet(db.Model):
    __tablename__ = 'InterviewSet'
    interviewSetId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(12), db.ForeignKey('User.userId'))
    expId = db.Column(db.Integer, db.ForeignKey('ProjectExp.expId'))
    industry = db.Column(db.String(128))
    department = db.Column(db.String(128))
    role = db.Column(db.String(128))
    workYear = db.Column(db.Integer)

class InterviewQA(db.Model):
    __tablename__ = 'InterviewQA'
    InterviewQAId = db.Column(db.Integer, primary_key=True)
    interviewId = db.Column(db.Integer, db.ForeignKey('Interview.interviewId'))
    sequence = db.Column(db.Integer, unique=True)

class Questions(db.Model):
    __tablename__ = 'Questions'
    questionId = db.Column(db.Integer, primary_key=True)
    interviewQAId = db.Column(db.Integer, db.ForeignKey('InterviewQA.InterviewQAId'))
    question = db.Column(db.Text)
    questionTime = db.Column(db.DateTime)

class Answer(db.Model):
    __tablename__ = 'Answer'
    answerId = db.Column(db.Integer, primary_key=True)
    interviewQAId = db.Column(db.Integer, db.ForeignKey('InterviewQA.InterviewQAId'))
    answer = db.Column(db.Text)
    answerTime = db.Column(db.DateTime)
