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
    tipo_usuario = db.Column(db.String(50), nullable= False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Criando o banco de dados e as tabelas
with app.app_context():
    db.create_all()

#rotas
@app.route('/')
def index():
    return redirect(url_for('login'))
    
@app.route('/exibe')
def exibir():
    usuarios = Usuario.query.all()
    return str([f'nome: {user.nome}, email: {user.email}, tipo_usuario{user.tipo_usuario}' for user in usuarios])



#cadastro
@app.route('/cadastra', methods= ['GET', 'POST'])
def cadastrar():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario= request.form['tipo_usuario']

        novo_usr = Usuario(nome=nome, email=email, senha=senha, tipo_usuario= tipo_usuario)
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
        usuario= Usuario.query.filter_by(email=email).first()

        if usuario:
            if usuario.senha == senha:
                session['nome_usuario']= usuario.nome
                session['tipo_usuario']= usuario.tipo_usuario
                
                if usuario.tipo_usuario == 'Credenciado':
                    return redirect(url_for('autoriza'))
                
                elif usuario.tipo_usuario == 'Operadora':
                    return redirect(url_for('autoriza_loc'))
                else:
                    return 'Tipo de Usuario não reconhecido'
                
            else:
                return 'senha inválida'
            
        else:
            return 'usuario não encontrado'
    
    return render_template('login.html')


@app.route('/autoriza')
def autoriza(): 
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza.html', nome= nome_usuario, tipo= tipo_usuario)
    
    else:
        return redirect(url_for('login'))

@app.route('/autoriza_loc')
def autoriza_loc():
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza_loc.html', nome= nome_usuario, tipo= tipo_usuario)
    
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
