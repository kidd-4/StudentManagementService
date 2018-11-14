from flask import Flask,jsonify
from flask import abort
from flask import request
from flask_httpauth import HTTPBasicAuth, make_response

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'omar':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error':'Unauthorized access'}), 401)

app = Flask(__name__)

students = [
    {
        'id':1,
        'name':'Alice Greene',
        'level':'Graduate',
        'passed':False
    },
    {
        'id':2,
        'name':'Steve Smith',
        'level':'Graduate',
        'passed':True
    }
]

@app.route('/ProgrammingCloud/api/v1.0/students',methods=['GET'])
@auth.login_required
def get_students():
    return jsonify({'students':students})

@app.route('/ProgrammingCloud/api/v1.0/students/<int:student_id>',methods=['GET'])
def get_student(student_id):
    student = [s for s in students if s['id'] == student_id]
    if len(student) == 0:
        abort(404)
    return jsonify({'student':student[0]})

@app.route('/ProgrammingCloud/api/v1.0/students',methods=['POST'])
def create_student():
    if not request.json or not 'name' in request.json:
        abort(400)
    student = {
        'id':students[-1]['id']+1,
        'name':request.json['name'],
        'level':request.json.get('level',""),
        'passed':False
    }
    students.append(student)
    return jsonify({'student':student}),201

@app.route('/ProgrammingCloud/api/v1.0/students/<int:student_id>',methods=['PUT'])
def update_student(student_id):
    student = [s for s in students if s['id'] == student_id]
    if len(student) == 0:
        abort(404)
    if not request.json:
        abort(400)
    # if 'name' in request.json and type(request.json['name']) != unicode:
    #     abort(400)
    # if 'level' in request.json and type(request.json['level']) is not unicode:
    #     abort(400)
    student[0]['name'] = request.json.get('name',student[0]['name'])
    student[0]['level'] = request.json.get('level', student[0]['level'])
    student[0]['passed'] = request.json.get('passed', student[0]['passed'])
    return jsonify({'student':student[0]})

@app.route('/ProgrammingCloud/api/v1.0/students/<int:student_id>',methods=['DELETE'])
def delete_student(student_id):
    student = [s for s in students if s['id'] == student_id]
    if len(student) == 0:
        abort(404)
    students.remove(student[0])
    return jsonify({'result':True})








if __name__ == '__main__':
    app.run(debug=True)