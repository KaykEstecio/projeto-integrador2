import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import inspect, text
import click


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
    is_admin = db.Column(db.Boolean, default=False)
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

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    total_price = db.Column(db.Float, nullable=False)


# --- Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not getattr(current_user, 'is_admin', False):
            flash('Acesso negado: admin apenas.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function




# --- Routes ---

@app.route('/')
def index():
    login_required(lambda: None)  # Dummy call to ensure login manager is initialized
    cars = Car.query.all()
    return render_template('home.html', cars=cars)



@app.route('/reserve/<int:car_id>', methods=['GET', 'POST'])
@login_required
def reserve(car_id):
    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        start = request.form.get('start_date')
        end = request.form.get('end_date')

        # Calcular dias
        from datetime import datetime
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
        days = (d2 - d1).days

        if days <= 0:
            flash("Datas inválidas.", "error")
            return redirect(url_for('car_details', id=car_id))

        total = days * car.price_per_day
        
        new_res = Reservation(
            car_id=car.id,
            user_id=current_user.id,
            start_date=start,
            end_date=end,
            total_price=total
        )

        db.session.add(new_res)
        db.session.commit()

        flash("Reserva realizada com sucesso!", "success")
        return redirect(url_for('my_reservations'))

    return render_template('reservation.html', car=car)


@app.route('/car/<int:id>')
@login_required
def car_details(id):
    car = Car.query.get_or_404(id)
    return render_template('cars.details.html', car=car)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/cancel_reservation/<int:id>')
@login_required
def cancel_reservation(id):
    res = Reservation.query.get_or_404(id)

    # Garantir que o usuário só cancele as reservas dele
    if res.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash("Você não tem permissão para cancelar esta reserva.", "error")
        return redirect(url_for('my_reservations'))

    db.session.delete(res)
    db.session.commit()
    flash("Reserva cancelada com sucesso!", "success")

    return redirect(url_for('my_reservations'))



@app.route('/cars')
@login_required
def cars():
    brand = request.args.get('brand')
    max_price = request.args.get('max_price')
    order = request.args.get('order')

    query = Car.query

    # Filtro por marca
    if brand and brand != "Todas":
        query = query.filter(Car.brand == brand)

    # Filtro por preço máximo
    if max_price:
        query = query.filter(Car.price_per_day <= float(max_price))

    # Ordenação
    if order == "menor_preco":
        query = query.order_by(Car.price_per_day.asc())
    elif order == "maior_preco":
        query = query.order_by(Car.price_per_day.desc())

    all_cars = query.all()

    # Buscar todas marcas para preencher o dropdown
    brands = sorted({c.brand for c in Car.query.all()})

    return render_template('cars.html', cars=all_cars, brands=brands)


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
    if car.owner != current_user and not getattr(current_user, 'is_admin', False):
        flash('Você não tem permissão para excluir este veículo.', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(car)
    db.session.commit()
    flash('Veículo removido.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    cars = Car.query.all()
    reservations = Reservation.query.all()
    return render_template('admin.html', users=users, cars=cars, reservations=reservations)


@app.route('/admin/delete_car/<int:id>')
@login_required
@admin_required
def admin_delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    flash('Veículo removido pelo admin.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_reservation/<int:id>')
@login_required
@admin_required
def admin_delete_reservation(id):
    res = Reservation.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash('Reserva removida pelo admin.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.cli.command('create-admin')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(username, password):
    """Cria ou atualiza um usuário como admin via Flask CLI."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            print(f"Usuário '{username}' atualizado como admin.")
        else:
            new = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), is_admin=True)
            db.session.add(new)
            db.session.commit()
            print(f"Usuário admin '{username}' criado com sucesso.")

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
        # Garantir que a coluna `is_admin` exista (para bancos antigos)
        try:
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('user')]
        except Exception:
            cols = []

        if 'is_admin' not in cols:
            try:
                db.session.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                db.session.commit()
                print("Coluna 'is_admin' adicionada à tabela 'user'.")
            except Exception as e:
                # Caso o ALTER TABLE falhe (por ex. permissões), apenas logue a exceção
                print("Falha ao adicionar coluna is_admin:", e)

        # Nota: criação automática de admin foi removida por segurança.
        # Use o comando CLI `flask create-admin` ou o script `scripts/create_admin.py`.










if __name__ == '__main__':
    init_db()
    app.run(debug=True)
