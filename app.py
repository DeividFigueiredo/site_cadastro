from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

app.secret_key= 'chave_super_secreta'

# Configurando o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Criando o banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable= False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Beneficiario(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    nome= db.Column(db.String(100), nullable= False)
    matricula= db.Column(db.String(100), nullable= False, unique= True)
    data_entrada= db.Column(db.DateTime, nullable= False)
    status= db.Column(db.String(30), nullable= False)

    def __repr__(self):
        return f'<Beneficiario{self.nome}>'


class Autorizacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Um número que identifica cada autorização
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Qual usuário fez a autorização (chave estrangeira)
    matricula_beneficiario = db.Column(db.String(100), db.ForeignKey('beneficiario.matricula'), nullable=False)  # Qual beneficiário recebeu a autorização (chave estrangeira)
    data_autorizacao = db.Column(db.DateTime, nullable=False)  # Data da autorização
    status = db.Column(db.String(50), nullable=False)  # Status da autorização (por exemplo, aprovada ou negada)

    beneficiario = db.relationship('Beneficiario', backref='autorizacoes')  # Relacionamento com o beneficiário

    def __repr__(self):
        return f'<Autorizacao {self.id}, Beneficiario {self.matricula_beneficiario}>'


# Criando o banco de dados e as tabelas
with app.app_context():
    db.create_all()


    ###rotas
@app.route('/')
def index():
    return redirect(url_for('login'))

#rotas de exibição    
@app.route('/exibe')
def exibir():
    usuarios = Usuario.query.all()
    return str([f'nome: {user.nome}, email: {user.email}, tipo_usuario{user.tipo_usuario}' for user in usuarios])

@app.route('/exibir_benef')
def exibe():
    beneficiarios= Beneficiario.query.all()
    return str([f'nome: {user.nome}, matricula{user.matricula}, data_entrada:{user.data_entrada}, status:{user.status}'for user in beneficiarios])



#rotas de cadastro
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

@app.route('/cadastro_beneficiario', methods= ['GET','POST'])
def cadastrar_benef():
    if request.method == 'POST':
        nome= request.form['nome']
        matricula= request.form['matricula']
        data_entrada_str= request.form['data_entrada']
        status= request.form['status']

        #converter a dara para string
        data_entrada= datetime.strptime(data_entrada_str,'%Y-%m-%d').date()

        novo_beneficiario= Beneficiario(nome= nome, matricula= matricula, data_entrada=data_entrada, status= status)

        db.session.add(novo_beneficiario)
        db.session.commit()

        return redirect(url_for('autoriza_loc'))

    return render_template('cadastro_beneficiarios.html')


# login.
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


#autorizadores
@app.route('/autoriza')
def autoriza(): 
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza.html', nome= nome_usuario, tipo= tipo_usuario)
    
    else:
        return redirect(url_for('login'))

@app.route('/autoriza_loc', methods= ['GET','POST'])
def autoriza_loc():
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza_loc.html', nome= nome_usuario, tipo= tipo_usuario)
    else:
        return redirect(url_for('login'))
 

if __name__ == '__main__':
    app.run(debug=True)
