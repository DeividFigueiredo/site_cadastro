from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

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
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(100), nullable=False, unique=True)
    unidade = db.Column(db.String, nullable=False)
    status = db.Column(db.String(30), nullable=False)

    # Novos campos para a carteirinha
    empresa = db.Column(db.String(100), nullable=False)
    plano = db.Column(db.String(150), nullable=False)
    codigo_produto = db.Column(db.String(50), nullable=False)
    regra_carencia = db.Column(db.String(50), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    inclusao = db.Column(db.Date, nullable=False)
    validade = db.Column(db.Date, nullable=False)
    fim_cpt = db.Column(db.Date, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Beneficiario{self.nome}>'


class Autorizacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Um número que identifica cada autorização
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Qual usuário fez a autorização (chave estrangeira)
    matricula = db.Column(db.String(100), db.ForeignKey('beneficiario.matricula'), nullable=False)  # Qual beneficiário recebeu a autorização (chave estrangeira)
    data_autorizacao = db.Column(db.DateTime, nullable=False)  # Data da autorização
    status = db.Column(db.String(50), nullable=True)  # Status da autorização (por exemplo, aprovada ou negada)
    senha= db.Column(db.String(20), nullable=True)
    cod_procedimento= db.Column(db.String(20), nullable=False)
    nome_procedimento= db.Column(db.String(50), nullable=False)
    nome_local= db.Column(db.String(50), nullable= False)
    nome_atendente= db.Column(db.String(50), nullable= False)
    
    beneficiario = db.relationship('Beneficiario', backref='autorizacoes')  # Relacionamento com o beneficiário

    def __repr__(self):
        return f'<Autorizacao {self.id}, Beneficiario {self.matricula_beneficiario}>'


# Criando o banco de dados e as tabelas
with app.app_context():
    db.create_all()


    ###rotas de configuração
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
def logoff():
    session.pop('nome_usuario', None)
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

@app.route('/aut_show')
def show():
    autorizacoes= Autorizacao.query.all()
    return str([
        f'Matrícula: {autorizacao.matricula}, Data da Autorização: {autorizacao.data_autorizacao}, '
        f'Status: {autorizacao.status}, Senha: {autorizacao.senha}, Código do Procedimento: {autorizacao.cod_procedimento}, '
        f'Nome do Procedimento: {autorizacao.nome_procedimento}, Local: {autorizacao.nome_local}, '
        f'Atendente: {autorizacao.nome_atendente}' 
        for autorizacao in autorizacoes
    ])

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
        return redirect(url_for('login'))
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

@app.route('/gerar_carteirinha', methods=['GET'])
def gerar_carteirinha():

    beneficiarios = Beneficiario.query()
    
    # Dados do beneficiário (vindos do banco ou requisição)
    nome = request.args.get('nome', 'CRISTIANE TEODORO SEGAL')
    empresa = request.args.get('empresa', 'PLANO PARTICULAR')
    matricula = request.args.get('matricula', '020.021134-00')
    unidade = request.args.get('unidade', 'MHVida - Registro ANS - 412015')
    plano = request.args.get('plano', 'AMACOR CLÁSSICO - 489.363/21-8')
    codigo_produto = request.args.get('codigo_produto', '489363218')
    regra_carencia = request.args.get('regra_carencia', 'COM CARÊNCIA PF')
    nascimento = request.args.get('nascimento', '27/06/1981')
    inclusao = request.args.get('inclusao', '20/09/2023')
    validade = request.args.get('validade', '20/09/2026')
    fim_cpt = request.args.get('fim_cpt', '19/09/2025')
    telefone = request.args.get('telefone', '(21) 3405-9466 (WhatsApp)')

    # Tamanho da carteirinha
    largura, altura = 800, 400
    imagem = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(imagem)

    # Fontes (verifique o caminho para as fontes no seu sistema)
    try:
        fonte_titulo = ImageFont.truetype("arialbd.ttf", 18)  # Fonte em negrito
        fonte_texto = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fonte padrão se a fonte específica não estiver disponível
        fonte_titulo = fonte_texto = ImageFont.load_default()

    # Desenhar as informações
    draw.text((20, 20), nome, font=fonte_titulo, fill="black")  # Nome
    draw.text((20, 50), f"Empresa: {empresa}", font=fonte_texto, fill="black")
    draw.text((20, 75), f"Matrícula: {matricula}", font=fonte_texto, fill="black")
    draw.text((20, 100), f"Unidade: {unidade}", font=fonte_texto, fill="black")
    draw.text((20, 125), f"Plano: {plano}", font=fonte_texto, fill="black")
    draw.text((20, 150), f"Código Produto ANS: {codigo_produto}", font=fonte_texto, fill="black")
    draw.text((20, 175), f"Regra de Carência: {regra_carencia}", font=fonte_texto, fill="black")
    draw.text((20, 200), f"Data de Nascimento: {nascimento}   Inclusão: {inclusao}", font=fonte_texto, fill="black")
    draw.text((20, 225), f"Data de Validade: {validade}   Data Fim CPT: {fim_cpt}", font=fonte_texto, fill="black")
    draw.text((20, 275), f"Titular: {nome}", font=fonte_texto, fill="black")
    draw.text((20, 325), f"ADMINISTRATIVO MH VIDA: {telefone}", font=fonte_texto, fill="black")
    draw.text((20, 350), "VÁLIDO SOMENTE COM DOCUMENTO DE IDENTIFICAÇÃO", font=fonte_texto, fill="black")

    # Salvando a imagem em memória para envio como resposta
    img_io = io.BytesIO()
    imagem.save(img_io, 'JPEG', quality=85)
    img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg', as_attachment=False, download_name="carteirinha.jpg")


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
                session['usuario_id'] = usuario.id
                session['nome_usuario']= usuario.nome
                session['tipo_usuario']= usuario.tipo_usuario
                
                if usuario.tipo_usuario == 'Credenciado':
                    return redirect(url_for('autoriza'))
                
                elif usuario.tipo_usuario == 'Autorizador':
                    return redirect(url_for('autoriza_loc'))
                
                elif usuario.tipo_usuario == 'Amacor':
                    return redirect(url_for('autoriza'))
                
                elif usuario.tipo_usuario == 'Corretor':
                    return redirect(url_for('vendas_home'))
                else:
                    return 'Tipo de Usuario não reconhecido'
                
            else:
                return 'senha inválida'
            
        else:
            return 'usuario não encontrado'
    
    return render_template('login.html')


#paginas de inicio
@app.route('/autoriza')
def autoriza(): 
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if tipo_usuario not in ['Credenciado' or  'Referenciado']:
        Flask ('Acesso negado.')
        return redirect(url_for('login'))

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


#criando autorização.
@app.route('/cria_aut', methods= ['POST', 'GET'])
def cria_aut():

    usuario_id= session.get('usuario_id')
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')
    
    if usuario_id == None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        senha = request.form.get('senha')
        matricula = request.form.get('matricula')
        data_autorizacao_str = request.form.get('data_autorizacao')
        status = request.form.get('status')
        cod_procedimento = request.form.get('cod_procedimento')
        nome_procedimento = request.form.get('nome_procedimento')
        nome_local = request.form.get('nome_local')
        nome_atendente = request.form.get('nome_atendente')


        #converter a data para str
        data_autorizacao= None

        if data_autorizacao_str:
            try:
                data_autorizacao = datetime.strptime(data_autorizacao_str, '%Y-%m-%d').date()
            except ValueError:
                return "Erro: Formato de data invalido."        


        nova_autorizacao = Autorizacao(
            usuario_id=usuario_id,
            matricula=matricula,
            senha=senha,
            data_autorizacao=data_autorizacao,
            status=status,
            cod_procedimento=cod_procedimento,
            nome_procedimento=nome_procedimento,
            nome_local=nome_local,
            nome_atendente=nome_atendente
        )
        db.session.add(nova_autorizacao)
        db.session.commit() 
        
        


    return render_template('cria_aut.html', nome= nome_usuario, tipo_usuario=tipo_usuario)

@app.route('/valida_aut')
def valida_aut():
    autorizacoes= Autorizacao.query.all()

    return render_template('valida_aut.html', autorizacoes=autorizacoes)

@app.route('/verifica_eleg', methods=['GET', 'POST'])
def verifica_eleg():
    beneficiario= None

    if request.method == 'POST':
        matricula= request.form.get('matricula')
        print(f'matricula {matricula}')
        beneficiario= Beneficiario.query.filter_by(matricula=matricula).first()

    return render_template('verifica_eleg.html',beneficiario=beneficiario)

@app.route('/home')
def home():
    tipo_usuario= session.get('tipo_usuario')

    if tipo_usuario == 'Autorizador':
        return redirect(url_for('autoriza_loc'))
    else:
        return redirect(url_for('autoriza'))



##separação de sistemas

@app.route('/vendas_home')
def vendas_home():
    tipo_usuario= session.get('tipo_usuario')
    nome= session.get('nome_usuario')


    return render_template('vendas_home.html', nome=nome, tipo_usuario=tipo_usuario)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001 ,debug=True)
    

