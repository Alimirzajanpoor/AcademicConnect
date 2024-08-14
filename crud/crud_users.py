from db.models import (
    Students,
    User,
    Teachers,
    StudentTeacherAssociation,
    follow_request,
)
from crud.crud_user_assign import assign_user
from datetime import datetime
from utl_handler.hash import Hash
from sqlalchemy import select
import copy

defualt_secret_key = "CynuprTESFEnR3r09-6x-jdhpOAR7YIXQ3vS_y29SEI"


async def is_value_already_exists(db, column_name, value):
    stmt = select(User).where(getattr(User, column_name) == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def is_value_already_exists_teacher(db, value):
    stmt = select(Teachers).where(getattr(Teachers, "id") == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def is_value_already_exists_student(db, value):
    stmt = select(Students).where(getattr(Students, "id") == value)
    result = await db.execute(stmt)

    exists = result.first() is not None

    return exists


async def is_followed(db, teacher_id, student_id):

    stmt = select(StudentTeacherAssociation).where(
        StudentTeacherAssociation.teacher_id == teacher_id,
        StudentTeacherAssociation.student_id == student_id,
    )
    result = await db.execute(stmt)
    stmt_follow_request = select(follow_request).where(
        follow_request.student_id == student_id,
        follow_request.teacher_id == teacher_id,
    )
    result_request = await db.execute(stmt_follow_request)
    fetched_request = result_request.first()
    exists = result.first() is not None
    if exists or fetched_request:
        return True
    else:
        return False


async def user_register(
    session,
    username: str,
    first_name: str,
    national_code: int,
    password: str,
    last_name: str,
):

    new_user = User(
        username=username,
        password=Hash.bcrypt(password),
        national_code=national_code,
        firstname=first_name,
        last_name=last_name,
    )

    session.add(new_user)

    return {"message": "user created", "user": new_user}


async def edit_user(
    session,
    user_id: int,
    username: str,
    first_name: str,
    last_name: str,
    national_code: int,
    password: str,
    role: str,
    gender: str,
    group_staff: str,
    age: int,
    rate: int,
):

    stmt = select(User).where(User.id == user_id)
    existing_user = await session.execute(stmt)
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:

        existing_user.username = username
        existing_user.firstname = first_name
        existing_user.last_name = last_name
        existing_user.gender = gender
        existing_user.age = age
        existing_user.national_code = national_code
        existing_user.password = Hash.bcrypt(password)

        if role == "teacher":
            stmt = select(Teachers).where(Teachers.id == user_id)
            existing_teacher = await session.execute(stmt)
            existing_teacher = existing_teacher.scalar_one_or_none()
            if existing_teacher:
                existing_teacher.group_staff = group_staff
                existing_teacher.rate = rate

    else:
        return 0

    await session.commit()
    return {"message": "user edited"}


async def update_user_admin(
    session,
    user_id,
    username,
    first_name,
    last_name,
    national_code,
    password,
    role,
    gender,
    group_staff,
    age,
    rate,
    accsess_token,
):

    stmt = select(User).where(User.id == user_id)
    existing_user = await session.execute(stmt)
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:

        existing_user.username = username
        existing_user.firstname = first_name
        existing_user.last_name = last_name
        existing_user.gender = gender
        existing_user.age = age
        existing_user.national_code = national_code
        existing_user.password = Hash.bcrypt(password)

        if role == "teacher":
            stmt = select(Teachers).where(Teachers.id == user_id)
            existing_teacher = await session.execute(stmt)
            existing_teacher = existing_teacher.scalar_one_or_none()
            if existing_teacher:
                existing_teacher.group_staff = group_staff
                existing_teacher.rate = rate
        print(accsess_token, "token")
        if accsess_token["username"] != username and accsess_token["sub"] == user_id:
            return "logout"

    else:
        return 0

    await session.commit()
    return 1


async def update_with_role(
    session,
    user_id,
    username,
    first_name,
    last_name,
    national_code,
    password,
    role,
    gender,
    group_staff,
    age,
    rate,
    secret_key,
    acsess_token,
):

    stmt = select(User).where(User.id == user_id)
    existing_user = await session.execute(stmt)
    existing_user = existing_user.unique().scalar_one_or_none()
    print(existing_user.username)
    if existing_user:

        if existing_user.username != username:
            if await is_value_already_exists(session, "username", username):
                return "username already exists"
        if existing_user.national_code != national_code:
            if await is_value_already_exists(session, "national_code", national_code):
                return "national code already exists"
        if role == "teacher" and existing_user.role == "student":

            existing_user.username = username
            existing_user.firstname = first_name
            existing_user.last_name = last_name
            existing_user.role = role
            existing_user.gender = gender
            existing_user.age = age
            existing_user.national_code = national_code
            existing_user.student = None
            existing_user.password = Hash.bcrypt(password)
            inserting_teacher = Teachers(
                user_id=user_id,
                group_staff=group_staff,
                rate=rate,
            )
            session.add(inserting_teacher)

        if role == "student" and existing_user.role == "teacher":

            existing_user.username = username
            existing_user.firstname = first_name
            existing_user.last_name = last_name
            existing_user.role = role
            existing_user.gender = gender
            existing_user.age = age
            existing_user.national_code = national_code
            existing_user.teacher = None
            existing_user.password = Hash.bcrypt(password)
            inserting_student = Students(
                user_id=user_id,
            )
            session.add(inserting_student)

        if existing_user.role == "admin" and role == "student":

            existing_user.username = username
            existing_user.firstname = first_name
            existing_user.last_name = last_name
            existing_user.role = role
            existing_user.gender = gender
            existing_user.age = age
            existing_user.national_code = national_code
            existing_user.teacher = None
            inserting_student = Students(
                user_id=user_id,
            )
            existing_user.password = Hash.bcrypt(password)
            session.add(inserting_student)
        if existing_user.role == "admin" and role == "teacher":
            print("YOOOO")
            existing_user.username = username
            existing_user.firstname = first_name
            existing_user.last_name = last_name
            existing_user.role = role
            existing_user.gender = gender
            existing_user.age = age
            existing_user.national_code = national_code
            inserting_teacher = Teachers(
                user_id=user_id,
                group_staff=group_staff,
                rate=rate,
            )

            existing_user.student = None
            existing_user.password = Hash.bcrypt(password)
            session.add(inserting_teacher)
        if existing_user.role == "student" and role == "admin":

            if secret_key == defualt_secret_key or acsess_token["user_role"] == "admin":

                existing_user.username = username
                existing_user.firstname = first_name
                existing_user.last_name = last_name
                existing_user.role = role
                existing_user.gender = gender
                existing_user.age = age
                existing_user.national_code = national_code
                existing_user.teacher = None
                existing_user.student = None
                existing_user.password = Hash.bcrypt(password)
                session.add(existing_user)
            else:
                return "403"

        if existing_user.role == "teacher" and role == "admin":
            if (
                secret_key == defualt_secret_key
                or await get_user_role(session, acsess_token["sub"]) == "admin"
            ):
                existing_user.username = username
                existing_user.firstname = first_name
                existing_user.last_name = last_name
                existing_user.role = role
                existing_user.gender = gender
                existing_user.age = age
                existing_user.national_code = national_code
                existing_user.teacher = None
                existing_user.student = None
                existing_user.password = Hash.bcrypt(password)
                session.add(existing_user)
            else:
                return "403"
        if existing_user.role == role:

            existing_user.username = username
            existing_user.firstname = first_name
            existing_user.last_name = last_name
            existing_user.gender = gender
            existing_user.age = age
            existing_user.national_code = national_code
            existing_user.password = Hash.bcrypt(password)
            if existing_user.teacher != None:
                existing_user.teacher.rate = rate
                existing_user.group_staff = group_staff
            session.add(existing_user)

        await session.commit()
        return 1
    else:
        return 0


async def get_user(session, user_id):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    print(user)

    if user:

        return user


async def get_user_role(session, user_id):
    stmt = select(User).where(User.id == int(user_id))
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    if user:
        return user.role


async def delete_user(session, user_id):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    if user:
        await session.delete(user)
        await session.commit()
        return 1
    else:
        return 0


async def insert_assign_teacher_to_students(session, teacher_id, student_id):
    fetched_teacher = await is_value_already_exists_teacher(session, teacher_id)
    if not fetched_teacher:
        return 0
    inserted_association = StudentTeacherAssociation(
        student_id=student_id,
        teacher_id=teacher_id,
    )
    if inserted_association:

        session.add(inserted_association)
        return 1


async def request_follow(session, teacher_id, student_id):
    fetched_teacher = await is_value_already_exists_teacher(session, teacher_id)
    if not fetched_teacher:
        return 0
    fetched_student = await is_value_already_exists_student(session, student_id)
    if not fetched_student:
        return 0
    inserted_association = follow_request(
        student_id=student_id,
        teacher_id=teacher_id,
    )
    if inserted_association:

        session.add(inserted_association)
        return 1


async def is_followed(session, teacher_id, student_id):
    stmt = select(StudentTeacherAssociation).where(
        StudentTeacherAssociation.teacher_id == teacher_id,
        StudentTeacherAssociation.student_id == student_id,
    )
    result = await session.execute(stmt)
    association = result.unique().scalar_one_or_none()
    if association:
        return 1
    else:
        return 0


async def get_follow_request(session, teacher_id):
    stmt = select(follow_request).where(
        follow_request.teacher_id == teacher_id,
    )
    result = await session.execute(stmt)
    request = result.scalars().all()

    if request:
        return request
    else:
        return 0


async def accept_follow_request(session, follow_id):
    stmt = select(follow_request).where(follow_request.id == follow_id)
    result = await session.execute(stmt)
    request = result.unique().scalar_one_or_none()
    if request:
        inserted = await insert_assign_teacher_to_students(
            session, request.teacher_id, request.student_id
        )
        if inserted:
            await session.delete(request)
        await session.commit()
        return 1
    else:
        return 0


async def del_assign_teacher_students(session, teacher_id, student_id):
    stmt = select(StudentTeacherAssociation).where(
        StudentTeacherAssociation.teacher_id == teacher_id,
        StudentTeacherAssociation.student_id == student_id,
    )
    result = await session.execute(stmt)
    association = result.unique().scalar_one_or_none()
    if association:
        await session.delete(association)

        return 1
    else:
        return 0


async def reject_follow(session, follow_id):
    stmt = select(follow_request).where(follow_request.id == follow_id)
    result = await session.execute(stmt)
    association = result.unique().scalar_one_or_none()
    if association:
        await session.delete(association)

        return 1
    else:
        return 0


async def get_teacher(session, user_id):
    stmt = select(Teachers).where(Teachers.id == user_id)
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    if user:
        return user


async def read_all_teacher(session):
    list_of_users = []
    stmt = select(Teachers.id)
    results = await session.execute(stmt)
    results = results.scalars().all()
    for id in results:
        user = await get_teacher(session, id)
        related_students_copy = copy.deepcopy(user.related_students)
        related_students = []
        for student in related_students_copy:
            dicted_row = student.user.__dict__
            dicted_row.pop("password", None)
            dicted_row.pop("_sa_instance_state", None)
            dicted_row.pop("avatar", None)
            dicted_row["created_date"] = dicted_row["created_date"].strftime("%Y-%m-%d")
            dicted_row["student_id"] = student.id

            related_students.append(dicted_row)
        user_dict = {
            "teacher_user_id": user.user_id,
            "teacher_id": user.id,
            "username": user.user.username,
            "firstname": user.user.firstname,
            "last_name": user.user.last_name,
            "national_code": user.user.national_code,
            "role": user.user.role,
            "created_date": user.user.created_date,
            "age": user.user.age,
            "gender": user.user.gender,
            "related_students": related_students,
            "rate": user.rate,
        }
        list_of_users.append(user_dict)

    return list_of_users


async def read_all_teacher(session):
    list_of_users = []

    stmt = select(Teachers.id)
    results = await session.execute(stmt)
    results = results.scalars().all()
    for id in results:
        user = await get_teacher(session, id)
        related_students_copy = copy.deepcopy(user.related_students)
        related_students = []
        list_avatar_ids = []
        for student in related_students_copy:
            dicted_row = student.user.__dict__
            dicted_row.pop("password", None)
            dicted_row.pop("_sa_instance_state", None)
            dicted_row.pop("avatar", None)
            dicted_row["created_date"] = dicted_row["created_date"].strftime("%Y-%m-%d")
            dicted_row["student_id"] = student.id
            dicted_row.pop("avatar", None)
            dicted_row.pop("sent_comments", None)
            dicted_row.pop("received_comments", None)

            related_students.append(dicted_row)

        if user.user.avatar:

            for ids in user.user.avatar:
                list_avatar_ids.append(ids.id)

        user_dict = {
            "teacher_user_id": user.user_id,
            "teacher_id": user.id,
            "username": user.user.username,
            "firstname": user.user.firstname,
            "last_name": user.user.last_name,
            "national_code": user.user.national_code,
            "role": user.user.role,
            "created_date": user.user.created_date,
            "age": user.user.age,
            "gender": user.user.gender,
            "group_staff": user.group_staff,
            "related_students": related_students,
            "received_comments": user.user.received_comments,
            "sent_comments": user.user.sent_comments,
            "avatars": list_avatar_ids,
            "rate": user.rate,
        }
        list_of_users.append(user_dict)

    return list_of_users


async def get_student(session, user_id):
    stmt = select(Students).where(Students.id == user_id)
    result = await session.execute(stmt)
    user = result.unique().scalar_one_or_none()
    if user:
        return user


async def read_all_student(session):
    list_of_users = []

    stmt = select(Students.id)
    results = await session.execute(stmt)
    results = results.scalars().all()
    for id in results:
        user = await get_student(session, id)
        related_teacher_copy = copy.deepcopy(user.related_teachers)
        list_avatar_ids = []
        related_teacher = []
        for teacher in related_teacher_copy:
            dicted_row = teacher.user.__dict__
            dicted_row.pop("password", None)
            dicted_row.pop("_sa_instance_state", None)
            dicted_row.pop("avatar", None)
            dicted_row.pop("sent_comments", None)
            dicted_row.pop("received_comments", None)
            dicted_row["created_date"] = dicted_row["created_date"].strftime("%Y-%m-%d")
            dicted_row["student_id"] = teacher.id

            related_teacher.append(dicted_row)

        if user.user.avatar:
            for ids in user.user.avatar:
                list_avatar_ids.append(ids.id)

        user_dict = {
            "student_user_id": user.user_id,
            "student_id": user.id,
            "username": user.user.username,
            "firstname": user.user.firstname,
            "last_name": user.user.last_name,
            "national_code": user.user.national_code,
            "role": user.user.role,
            "created_date": user.user.created_date,
            "age": user.user.age,
            "gender": user.user.gender,
            "related_teacher": related_teacher,
            "sent_comments": user.user.sent_comments,
            "received_comments": user.user.received_comments,
            "avatars": list_avatar_ids,
        }

        list_of_users.append(user_dict)

    return list_of_users
