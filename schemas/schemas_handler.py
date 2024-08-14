from fastapi import FastAPI, UploadFile, Form, File
from pydantic import BaseModel, field_validator, ValidationError, ValidationInfo
from typing import List, Union, Optional, Dict, Literal
from datetime import datetime, date, time
from enum import Enum
from typing import Any
from dataclasses import dataclass


class register_user(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    national_code: int

    @field_validator("national_code")
    @classmethod
    def validate_atts(cls, v: int, info: ValidationInfo):
        if info.field_name == "national_code":
            print(v, "test")
            if len(str(v)) > 10:
                raise ValueError(f"{v} is not a valid national_code.")
            else:
                return v


class User_token(BaseModel):
    name: str
    password: str


class assign_user_input(BaseModel):
    user_id: int
    role: str
    age: int
    gender: str
    rate: int
    group_staff: bool

    @field_validator("gender", "role")
    @classmethod
    def validate_atts(cls, v: int, info: ValidationInfo):
        genders = ["male", "female"]
        roles = ["admin", "student", "teacher"]
        if info.field_name == "gender":
            print(v, "test")
            if v not in genders:
                raise ValueError(f"{v} is not a valid gender.")
            else:
                return v
        if info.field_name == "role":
            if v not in roles:
                raise ValueError(f"{v} is not valid role")
            else:
                return v


class edit_form(BaseModel):
    user_id: int
    first_name: str
    username: str
    last_name: str
    password: str
    national_code: int
    role: str
    age: int
    gender: str
    rate: int
    group_staff: bool

    @field_validator("national_code", "gender", "role")
    @classmethod
    def validate_atts(cls, v: int, info: ValidationInfo):
        if info.field_name == "national_code":
            print(v, "test")
            if len(str(v)) > 10:
                raise ValueError(f"{v} is not a valid national_code.")
            else:
                return v
        genders = ["male", "female"]
        roles = ["admin", "student", "teacher"]
        if info.field_name == "gender":
            print(v, "test")
            if v not in genders:
                raise ValueError(f"{v} is not a valid gender.")
            else:
                return v
        if info.field_name == "role":
            if v not in roles:
                raise ValueError(f"{v} is not valid role")
            else:
                return v


class comment_user(BaseModel):
    content: str
    receiver_id: int


class AvatarURLs(BaseModel):
    urls: List[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
