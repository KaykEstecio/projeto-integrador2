import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tedcar_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for system cars

# --- Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('cars'))

@app.route('/cars')
def cars():
    all_cars = Car.query.all()
    return render_template('cars.html', cars=all_cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_cars = Car.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', cars=user_cars)

@app.route('/add_car', methods=['POST'])
@login_required
def add_car():
    brand = request.form.get('brand')
    model = request.form.get('model')
    price = request.form.get('price')
    image_url = request.form.get('image_url') # In a real app, we would handle file upload
    
    if not image_url:
        image_url = 'https://via.placeholder.com/400x250?text=Carro' # Default placeholder

    new_car = Car(brand=brand, model=model, price_per_day=float(price), image_url=image_url, owner=current_user)
    db.session.add(new_car)
    db.session.commit()
    flash('Veículo adicionado com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_car/<int:id>')
@login_required
def delete_car(id):
    car = Car.query.get_or_404(id)
    if car.owner != current_user:
        flash('Você não tem permissão para excluir este veículo.', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(car)
    db.session.commit()
    flash('Veículo removido.', 'success')
    return redirect(url_for('dashboard'))

# --- Init DB ---
def init_db():
    with app.app_context():
        db.create_all()
        if not Car.query.first():
            # Pre-registered cars
            cars_data = [
                {"brand": "Tesla", "model": "Model S", "price": 520, "img": "tesla_model_s.png"},
                {"brand": "BMW", "model": "M4 Competition", "price": 480, "img": "bmw_m4.png"},
                {"brand": "Audi", "model": "R8 V10", "price": 750, "img": "audi_r8.png"},
                {"brand": "Porsche", "model": "911 Carrera", "price": 690, "img": "porsche_911.png"},
                {"brand": "Mercedes", "model": "AMG GT", "price": 650, "img": "mercedes_amg.png"}
            ]
            for c in cars_data:
                # Note: Images should be in static/images/
                new_car = Car(brand=c['brand'], model=c['model'], price_per_day=c['price'], image_url=f"/static/images/{c['img']}")
                db.session.add(new_car)
            db.session.commit()
            print("Banco de dados inicializado com carros padrão.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
