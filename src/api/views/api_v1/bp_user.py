"""
    Created by howie.hu at 2022-04-12.
    Description: 用户API
    Changelog: all notable changes to this file will be documented
"""
import datetime

from flask import Blueprint, current_app, request
from flask_jwt_extended import create_access_token

from src.api.common import (
    ResponseCode,
    ResponseField,
    ResponseReply,
    UniResponse,
    jwt_required,
    response_handle,
)
from src.databases import MongodbBase, mongodb_find
from src.utils import LOGGER, md5_encryption

bp_user = Blueprint("user", __name__, url_prefix="/user")


@bp_user.route("/token_valid", methods=["POST"], strict_slashes=False)
@jwt_required()
def token_valid():
    """验证jwt是否有效
    eg:
    {
        "username": "liuli"
    }
    Returns:
        Response: 响应类
    """
    return response_handle(request=request, dict_value=UniResponse.SUCCESS)


@bp_user.route("/login", methods=["POST"], strict_slashes=False)
def login():
    """用户登录接口
    eg:
    {
        "username": "liuli",
        "password": "liuli"
    }
    Token Demo:
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYyNzc1MDQ1OCwianRpIjoiNzJjZjZkYzYtZDE5NS00NGRhLTg2NWUtNmNhZmY3MTdkMjMwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MTU3Njc5NTY4OTAsIm5iZiI6MTYyNzc1MDQ1OH0.xwUuyTYoXFIymE6RqnEuuteyFbYiMmY72YYtIUMfqNY"
    Returns:
        Response: Flask响应类
    """
    # 获取基本配置
    mongodb_base: MongodbBase = current_app.config["mongodb_base"]
    app_logger: LOGGER = current_app.config["app_logger"]
    coll = mongodb_base.get_collection(coll_name="liuli_user")
    # 获取基础数据
    post_data: dict = request.json
    username = post_data.get("username") or ""
    password = md5_encryption(f"{post_data.get('password')}")
    user_db_res = mongodb_find(
        coll_conn=coll,
        filter_dict={"username": username, "password": password},
        return_dict={"_id": 0},
    )
    user_info_list = user_db_res["info"]
    if username and password and user_db_res["status"] and len(user_info_list) == 1:
        # 半年过期一次 259200
        expires_delta = datetime.timedelta(minutes=259200)
        access_token = create_access_token(
            identity=username, expires_delta=expires_delta
        )
        result = {
            ResponseField.DATA: {"token": access_token, "username": username},
            ResponseField.MESSAGE: ResponseReply.SUCCESS,
            ResponseField.STATUS: ResponseCode.SUCCESS,
        }
    else:
        result = {
            ResponseField.DATA: {},
            ResponseField.MESSAGE: ResponseReply.USER_LOGIN_ERROR,
            ResponseField.STATUS: ResponseCode.USER_LOGIN_ERROR,
        }
        err_info = f"login failed! request data -> {post_data}, db response info -> {user_db_res}"
        app_logger.error(err_info)

    return response_handle(request=request, dict_value=result)
