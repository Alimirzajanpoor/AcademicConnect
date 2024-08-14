from db.db_orm import Base, AsyncDatabaseSession
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    LargeBinary,
    ForeignKey,
    Enum,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime


db = AsyncDatabaseSession()


async def get_session():
    async with db.begin():
        yield db


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String)
    firstname = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    national_code = Column(
        Integer,
        nullable=False,
        unique=True,
    )
    role_enum = Enum(
        "admin",
        "student",
        "teacher",
        name="role_enum",
    )
    role = Column(role_enum, default=None)
    created_date = Column(DateTime(timezone=True), default=func.now())
    # admin = relationship("Admin", uselist=False, back_populates="user")
    age = Column(Integer)
    gender = Column(String(50))
    teacher = relationship(
        "Teachers",
        uselist=False,
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    avatar = relationship("Avatars", back_populates="owner", lazy="selectin")
    student = relationship(
        "Students",
        uselist=False,
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sent_comments = relationship(
        "User_comments",
        foreign_keys="[User_comments.sender]",
        back_populates="sender_user",
        lazy="selectin",
    )
    received_comments = relationship(
        "User_comments",
        foreign_keys="[User_comments.receiver]",
        back_populates="receiver_user",
        lazy="selectin",
    )


class follow_request(Base):
    __tablename__ = "follow_request"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    student_id = Column(Integer, ForeignKey("students.id"))


class StudentTeacherAssociation(Base):
    __tablename__ = "student_teacher_association"
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), primary_key=True)


# check chat gpt for latest update :D
class Students(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    is_banned = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    related_teachers = relationship(
        "Teachers",
        secondary=StudentTeacherAssociation.__table__,
        back_populates="related_students",
        lazy="selectin",
    )
    user = relationship("User", back_populates="student", lazy="selectin")


class Teachers(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)

    user = relationship("User", back_populates="teacher", lazy="selectin")

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    group_staff = Column(Boolean, default=False)
    rate = Column(Integer)

    related_students = relationship(
        "Students",
        secondary=StudentTeacherAssociation.__table__,
        back_populates="related_teachers",
        lazy="selectin",
    )
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)


class Avatars(Base):
    __tablename__ = "avatars"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="avatar", lazy="selectin")
    avatar = Column(LargeBinary, nullable=True)
    is_current = Column(Boolean, default=False)


class User_comments(Base):
    __tablename__ = "user_comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    receiver = Column(ForeignKey("users.id"))
    sender = Column(ForeignKey("users.id"))
    created_date = Column(DateTime(timezone=True), default=func.now())
    sender_user = relationship(
        "User", foreign_keys=[sender], back_populates="sent_comments", lazy="selectin"
    )
    receiver_user = relationship(
        "User",
        foreign_keys=[receiver],
        back_populates="received_comments",
        lazy="selectin",
    )
