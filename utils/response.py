from flask import jsonify


def make_response(success=True, data=None, message='OK', code=200):
    if data is None:
        data = {}
    response = {
        'success': success,
        'code': code,
        'message': message,
        'data': data,
    }
    return jsonify(response)


def error_response(message='Error', code=400, data=None):
    return make_response(success=False, data=data, message=message, code=code)


def success_response(data=None, message='OK'):
    return make_response(success=True, data=data, message=message, code=200)