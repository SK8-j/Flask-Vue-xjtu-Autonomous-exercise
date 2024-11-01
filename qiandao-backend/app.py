from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# 配置CORS，允许前端访问后端并携带凭证
CORS(app, supports_credentials=True, origins=['http://localhost:8080'])

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(150), unique=True, nullable=False)
    total_check_ins = db.Column(db.Integer, default=0)  # 记录总打卡次数
    remaining_check_ins = db.Column(db.Integer, default=60)  # 离60次打卡任务的差值

    def update_check_in(self):
        self.total_check_ins += 1
        self.remaining_check_ins = max(0, 60 - self.total_check_ins)

# 打卡记录模型
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # 可以改为日期类型

# 打卡API
@app.route('/check_in', methods=['POST'])
def check_in():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')  # 密码不会存储，仅用于验证

    user = User.query.filter_by(student_id=student_id).first()
    if user:
        # 此处可以添加密码验证逻辑，但为了示例暂时跳过
        # 记录打卡
        user.update_check_in()
        db.session.commit()

        # 添加打卡记录
        new_attendance = Attendance(user_id=user.id, date='2024-01-01')  # 示例日期
        db.session.add(new_attendance)
        db.session.commit()

        return jsonify({
            'message': '打卡成功！',
            'total_check_ins': user.total_check_ins,
            'remaining_check_ins': user.remaining_check_ins
        }), 200

    return jsonify({'message': '用户未找到'}), 404

# 首页获取用户信息和打卡记录
@app.route('/user_info', methods=['GET'])
def get_user_info():
    if 'student_id' not in request.args:
        return jsonify({'message': '学号未提供'}), 400

    student_id = request.args['student_id']
    user = User.query.filter_by(student_id=student_id).first()
    if user:
        return jsonify({
            'student_id': user.student_id,
            'total_check_ins': user.total_check_ins,
            'remaining_check_ins': user.remaining_check_ins
        }), 200

    return jsonify({'message': '用户未找到'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
