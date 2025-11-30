import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
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

# --- Master Key Configuration ---
MASTER_USER = "unisa"
MASTER_PASS = "unisa"

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    cars = db.relationship('Car', backref='owner', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    plate = db.Column(db.String(20), nullable=True) # New
    year = db.Column(db.Integer, nullable=True) # New
    km = db.Column(db.Float, nullable=True) # New
    status = db.Column(db.String(20), default='available') # available, rented, maintenance
    price_per_day = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    car = db.relationship('Car')
    user = db.relationship('User')

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(50), nullable=False) # Username or 'MASTER'
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- Loader ---
@login_manager.user_loader
def load_user(user_id):
    if user_id == 'MASTER':
        # Create a transient user object for Master Key
        # We use a plain class or just the User model but we can't set properties that are read-only on UserMixin
        # UserMixin properties (is_authenticated, etc) return True/False based on methods, but default is True for is_authenticated.
        u = User(id=0, username=MASTER_USER, is_admin=True)
        # We don't need to set is_authenticated = True, UserMixin does it.
        # We need to ensure get_id returns 'MASTER'
        u.get_id = lambda: 'MASTER'
        return u
    return User.query.get(int(user_id))

def log_action(action, details=None):
    """Helper to log admin actions"""
    admin_name = current_user.username if current_user.is_authenticated else 'SYSTEM'
    new_log = Log(admin_id=admin_name, action=action, details=details)
    db.session.add(new_log)
    db.session.commit()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        
        # Master Key bypass or DB Admin check
        is_master = (current_user.get_id() == 'MASTER')
        if not is_master and not getattr(current_user, 'is_admin', False):
            flash('Acesso negado: Área restrita a administradores.', 'error')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    # Public route
    cars = Car.query.filter_by(status='available').all()
    return render_template('home.html', cars=cars)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 1. Master Key Check
        if username == MASTER_USER and password == MASTER_PASS:
            user = User(id=0, username=MASTER_USER, is_admin=True)
            user.get_id = lambda: 'MASTER'
            login_user(user)
            session['_user_id'] = 'MASTER' # Force ID to string 'MASTER' just in case
            flash('Login Mestre realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))

        # 2. Regular DB Check
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if user.is_blocked:
                flash('Sua conta está bloqueada. Contate o suporte.', 'error')
                return redirect(url_for('login'))

            login_user(user)
            
            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Login inválido. Verifique suas credenciais.', 'error')
            
    return render_template('login.html')

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
        return redirect(url_for('index')) # Regular users go to home
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- User Routes ---

@app.route('/my_reservations')
@login_required
def my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('my_reservations.html', reservations=reservations)

@app.route('/cars')
@login_required
def cars():
    brand = request.args.get('brand')
    max_price = request.args.get('max_price')
    order = request.args.get('order')

    query = Car.query.filter(Car.status != 'maintenance') # Show rented but maybe mark them?

    if brand and brand != "Todas":
        query = query.filter(Car.brand == brand)

    if max_price:
        query = query.filter(Car.price_per_day <= float(max_price))

    if order == "menor_preco":
        query = query.order_by(Car.price_per_day.asc())
    elif order == "maior_preco":
        query = query.order_by(Car.price_per_day.desc())

    all_cars = query.all()
    brands = sorted({c.brand for c in Car.query.all()})

    return render_template('cars.html', cars=all_cars, brands=brands)

@app.route('/car/<int:id>')
@login_required
def car_details(id):
    car = Car.query.get_or_404(id)
    return render_template('cars.details.html', car=car)

@app.route('/reserve/<int:car_id>', methods=['GET', 'POST'])
@login_required
def reserve(car_id):
    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        start = request.form.get('start_date')
        end = request.form.get('end_date')

        from datetime import datetime
        try:
            d1 = datetime.strptime(start, "%Y-%m-%d")
            d2 = datetime.strptime(end, "%Y-%m-%d")
            days = (d2 - d1).days
        except ValueError:
            flash("Datas inválidas.", "error")
            return redirect(url_for('car_details', id=car_id))

        if days <= 0:
            flash("O período deve ser de pelo menos 1 dia.", "error")
            return redirect(url_for('car_details', id=car_id))

        total = days * car.price_per_day
        
        new_res = Reservation(
            car_id=car.id,
            user_id=current_user.id,
            start_date=start,
            end_date=end,
            total_price=total,
            status='pending'
        )

        db.session.add(new_res)
        db.session.commit()

        flash("Solicitação de reserva realizada! Aguarde aprovação.", "success")
        return redirect(url_for('my_reservations'))

    return render_template('reservation.html', car=car)

@app.route('/cancel_reservation/<int:id>')
@login_required
def cancel_reservation(id):
    res = Reservation.query.get_or_404(id)
    if res.user_id != current_user.id and not getattr(current_user, 'is_admin', False) and current_user.get_id() != 'MASTER':
        flash("Permissão negada.", "error")
        return redirect(url_for('my_reservations'))

    res.status = 'cancelled'
    db.session.commit()
    flash("Reserva cancelada.", "success")
    return redirect(url_for('my_reservations'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash("Mensagem enviada com sucesso!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Legacy dashboard route, redirect to new admin dashboard
    return redirect(url_for('admin_dashboard'))

@app.route('/add_car', methods=['POST'])
@login_required
@admin_required
def add_car():
    # Legacy add_car, redirect or handle. 
    # Since we have admin_add_car, let's just redirect or keep it for compatibility if forms point here.
    # But forms in new admin point to admin_add_car.
    # Old dashboard.html pointed here. 
    # Let's keep it working but restricted.
    brand = request.form.get('brand')
    model = request.form.get('model')
    price = request.form.get('price')
    image_url = request.form.get('image_url')
    
    if not image_url:
        image_url = 'https://via.placeholder.com/400x250?text=Carro'

    new_car = Car(brand=brand, model=model, price_per_day=float(price), image_url=image_url, status='available')
    db.session.add(new_car)
    db.session.commit()
    flash('Veículo adicionado com sucesso!', 'success')
    return redirect(url_for('admin_cars'))

@app.route('/delete_car/<int:id>')
@login_required
@admin_required
def delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    flash('Veículo removido.', 'success')
    return redirect(url_for('admin_cars'))


# --- Admin Routes ---

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Dashboard Summary
    total_cars = Car.query.count()
    total_users = User.query.count()
    active_rentals = Reservation.query.filter_by(status='active').count()
    pending_rentals = Reservation.query.filter_by(status='pending').count()
    recent_logs = Log.query.order_by(Log.timestamp.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_cars=total_cars, 
                           total_users=total_users,
                           active_rentals=active_rentals,
                           pending_rentals=pending_rentals,
                           recent_logs=recent_logs)

@app.route('/admin/cars')
@login_required
@admin_required
def admin_cars():
    cars = Car.query.all()
    return render_template('admin/cars.html', cars=cars)

@app.route('/admin/car/add', methods=['POST'])
@login_required
@admin_required
def admin_add_car():
    brand = request.form.get('brand')
    model = request.form.get('model')
    plate = request.form.get('plate')
    year = request.form.get('year')
    km = request.form.get('km')
    price = request.form.get('price')
    image_url = request.form.get('image_url') or 'https://via.placeholder.com/400x250?text=Carro'
    
    new_car = Car(
        brand=brand, model=model, plate=plate, year=int(year) if year else None, 
        km=float(km) if km else 0, price_per_day=float(price), image_url=image_url,
        status='available'
    )
    db.session.add(new_car)
    db.session.commit()
    log_action(f"Adicionou veículo: {brand} {model} ({plate})")
    flash('Veículo cadastrado com sucesso!', 'success')
    return redirect(url_for('admin_cars'))

@app.route('/admin/car/delete/<int:id>')
@login_required
@admin_required
def admin_delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    log_action(f"Excluiu veículo ID {id}")
    flash('Veículo removido.', 'success')
    return redirect(url_for('admin_cars'))

@app.route('/admin/car/status/<int:id>/<status>')
@login_required
@admin_required
def admin_car_status(id, status):
    car = Car.query.get_or_404(id)
    if status in ['available', 'rented', 'maintenance']:
        car.status = status
        db.session.commit()
        log_action(f"Alterou status do veículo {id} para {status}")
    return redirect(url_for('admin_cars'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/toggle_block/<int:id>')
@login_required
@admin_required
def admin_toggle_block_user(id):
    user = User.query.get_or_404(id)
    if user.username == MASTER_USER:
        flash("Não é possível bloquear o usuário mestre.", "error")
        return redirect(url_for('admin_users'))
        
    user.is_blocked = not user.is_blocked
    db.session.commit()
    status = "bloqueado" if user.is_blocked else "desbloqueado"
    log_action(f"Usuário {user.username} foi {status}")
    flash(f'Usuário {user.username} {status}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/rentals')
@login_required
@admin_required
def admin_rentals():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    return render_template('admin/rentals.html', reservations=reservations)

@app.route('/admin/rental/action/<int:id>/<action>')
@login_required
@admin_required
def admin_rental_action(id, action):
    res = Reservation.query.get_or_404(id)
    if action == 'approve':
        res.status = 'active'
        res.car.status = 'rented'
        flash('Reserva aprovada. Veículo marcado como alugado.', 'success')
    elif action == 'complete':
        res.status = 'completed'
        res.car.status = 'available'
        flash('Reserva finalizada. Veículo disponível.', 'success')
    elif action == 'cancel':
        res.status = 'cancelled'
        res.car.status = 'available'
        flash('Reserva cancelada.', 'success')
    
    db.session.commit()
    log_action(f"Ação de reserva {id}: {action}")
    return redirect(url_for('admin_rentals'))

@app.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(100).all()
    return render_template('admin/logs.html', logs=logs)

# --- Init DB ---
def init_db():
    with app.app_context():
        db.create_all()
        # Check if we need to migrate or just create
        # For simplicity in this environment, we might need to rely on create_all handling new tables
        # But existing tables won't get new columns automatically with SQLAlchemy.
        # We will attempt to add columns manually if they fail, or recommend a reset.
        
        # Simple check for new columns
        try:
            inspector = inspect(db.engine)
            cols = [c['name'] for c in inspector.get_columns('car')]
            if 'plate' not in cols:
                print("Migrating DB: Adding new columns...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE car ADD COLUMN plate VARCHAR(20)"))
                    conn.execute(text("ALTER TABLE car ADD COLUMN year INTEGER"))
                    conn.execute(text("ALTER TABLE car ADD COLUMN km FLOAT"))
                    conn.execute(text("ALTER TABLE car ADD COLUMN status VARCHAR(20) DEFAULT 'available'"))
                    conn.execute(text("ALTER TABLE user ADD COLUMN is_blocked BOOLEAN DEFAULT 0"))
                    conn.execute(text("ALTER TABLE reservation ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
                    conn.execute(text("ALTER TABLE reservation ADD COLUMN created_at DATETIME"))
                    conn.commit()
        except Exception as e:
            print(f"Migration check failed or not needed: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
