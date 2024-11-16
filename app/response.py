from flask import jsonify, make_response

def success(data, message="success"):
    return make_response(jsonify({
        "status": True,
        "message": message,
        "data": data
    }), 200)

def error(message="error"):
    return make_response(jsonify({
        "status": False,
        "message": message,
    }), 400)

def badRequest(values, message):
    res = {
        'data' : values,
        'message': message
    }

    return make_response(jsonify(res)), 400