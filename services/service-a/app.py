from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory store
_users = {}
_next_id = 1


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'service-a'})


@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(list(_users.values()))


@app.route('/users/<int:uid>', methods=['GET'])
def get_user(uid):
    user = _users.get(uid)
    if not user:
        abort(404, description='User not found')
    return jsonify(user)


@app.route('/users', methods=['POST'])
def create_user():
    global _next_id
    data = request.get_json(silent=True) or {}
    name  = data.get('name', '').strip()
    email = data.get('email', '').strip()
    if not name or not email:
        abort(400, description='name and email are required')
    user = {'id': _next_id, 'name': name, 'email': email}
    _users[_next_id] = user
    _next_id += 1
    return jsonify(user), 201


@app.route('/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    if uid not in _users:
        abort(404, description='User not found')
    del _users[uid]
    return jsonify({'message': 'deleted'})


@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e.description)}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': str(e.description)}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
