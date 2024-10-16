from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key= 'chave_super_secreta'

# Configurando o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Criando um modelo para o banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Criando o banco de dados e as tabelas
with app.app_context():
    db.create_all()

# Criando rotas
@app.route('/')
def index():
    return "Conectado"
    
@app.route('/exibe')
def exibir():
    usuarios = Usuario.query.all()
    return str([f'nome: {user.nome}, email: {user.email}, senha:{user.senha}' for user in usuarios])



#cadastrando.
@app.route('/cadastra', methods= ['GET', 'POST'])
def cadastrar():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        novo_usr = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo_usr)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('cadastro.html')

#criando login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('email')
        senha= request.form.get('senha')

        
        if not email or not senha:
            return 'campos não preenchidos'

        #verificação de usuario
        usuario= Usuario.query.filter_by(email=email).first()

        if usuario:
            if usuario.senha == senha:
                session['nome_usuario']= usuario.nome
                return redirect(url_for('autoriza'))
            else:
                return 'senha inválida'
            
        else:
            return 'usuario não encontrado'
    
    return render_template('login.html')


@app.route('/autoriza')
def autoriza(): 
    nome_usuario= session.get('nome_usuario')

    if nome_usuario:
        return render_template('autoriza.html', nome= nome_usuario)
    
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
