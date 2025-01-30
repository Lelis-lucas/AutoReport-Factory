import pandas as pd
import matplotlib.pyplot as plt
import smtplib 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import  Table, TableStyle
from reportlab.lib import colors
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication 


df = pd.read_csv('equipment_anomaly_data.csv')
print(df.head())

#Validar colunas necessarias 
def validarcolunas(df):
    colunas_necessarias = {'temperature', 'vibration', 'faulty', 'location', 'equipment'}
    if not colunas_necessarias.issubset(df.columns):
        return False 
    else :
        return True

if not validarcolunas(df):
    print('Erro: Verifique as colunas do arquivo')
    exit()


#Criar um dataframe só com registros onde faulty é igual a 1
falhas_1 = df[df['faulty'] == 1]
print(falhas_1.head())

#Criar um dataframe só com registros onde faulty é igual a 0
falhas_0 = df[df['faulty'] == 0]
print(falhas_0.head())

#Temperatura média por tipo de equipamento
temperatura_media_por_equipamento = df.groupby('equipment')['temperature'].mean().round(2) #Agrupa por equipamento e calcula a média da temperatura e arredonda para 2 casas decimais
print('n--- Temperatura média por equipamento ---n')
print(temperatura_media_por_equipamento.to_markdown()) #Imprime a tabela em markdown

 #Comparação de temperatura e vibração quando faulty é 0
plt.figure(figsize=(10, 6))
plt.scatter(df['temperature'], df['vibration'], c='blue', label = 'Normal') 
    #Comparação de temperatura e vibração quando faulty é 1
plt.scatter(falhas_1['temperature'], falhas_1['vibration'], c= 'red', label = 'Falha')
plt.xlabel('Temperatura') #Nomeia o eixo x  
plt.ylabel('Vibração') #Nomeia o eixo y
plt.legend() #Adiciona a legenda ao gráfico
plt.title('Relação Temperatura vs Vibração') #Adiciona o título ao gráfico
plt.grid() #Adiciona a grade ao gráfico
plt.savefig('scatter_temperature_vibration.png') #Salva o gráfico
plt.show() #Mostra o gráfico

    #Grafico de barras com a quantidade de falhas por local
grafico_barra = df.groupby('location')['faulty'].sum().plot(kind='bar', #Pega os valores de faulty, agrupa por local e soma os valores de faulty, em seguida plota um grafico de barras                                                            
xlabel= 'Local', #Nomeia o Eixo X
ylabel='Quantidade de falhas', #Nomeia o Eixo Y
color = ['#2ecc71', '#3498db', '#e74c3c']) #Define as cores das barras
plt.title('Falhas por localização') #Adiciona o título ao gráfico

#Adicionar o valor de cada barra
for i in grafico_barra.patches: #Para cada barra no gráfico
    grafico_barra.annotate(f'{int(i.get_height())}', #Para cada barra, adiciona o valor da altura da barra
                            (i.get_x() + i.get_width() / 2 , i.get_height()), #Posição Y, altura da barra, #Pocição X, metade da largura da barra
                            ha = 'center', va='bottom') #Alinhamento horizontal e vertical
plt.savefig('falhas_por_local.png', bbox_inches = 'tight') #Salva o gráfico em uma imagem e ajusta o tamanho da imagem
plt.show()




#Criar PDF
pdf = canvas.Canvas('Relatorio.pdf', pagesize=A4) #Cria um arquivo PDF
largura, altura = A4 #Define a largura e altura da página


#Adicionar logo
logo = 'logo.png' #Define o caminho da imagem
pdf.drawImage(logo, 2*cm, altura - 4*cm, width = 5*cm, height = 3*cm) #Adiciona a imagem ao PDF
#Titulo do relatório
pdf.setFont('Helvetica-Bold', 24) #Define a fonte e o tamanho
pdf.drawString(2*cm, altura - 6*cm, 'Relatório de Análise de Equipamentos') #Adiciona o título ao PDF

#Rodapé
pdf.setFont('Helvetica', 10) #Define a fonte e o tamanho
pdf.drawString(2*cm, 1*cm, 'Relatório gerado automaticamente por AutoReport Factory') #Adiciona o rodapé ao PDF

pdf.showPage() #Finaliza página atual

#Adicionar gráfico de dispersão
pdf.setFont('Helvetica-Bold', 16) #Define a fonte e o tamanho
pdf.drawString(2*cm, altura - 2*cm, 'Relação Temperatura vs Vibração') #Adiciona o título ao PDF
grafico_dispersao = 'scatter_temperature_vibration.png' #Define o caminho da imagem
largura_imagem_dispercao = 15*cm #Define a largura e altura da imagem/Ajustar tamanho
pdf.drawImage(grafico_dispersao, 2*cm, altura - 12*cm, width = largura_imagem_dispercao, height = 10*cm) #Adiciona a imagem ao PDF
texto = 'Análise: Valores de vibração acima de 2.0 indicam risco potencial.'
pdf.drawString(2*cm, altura - 22*cm, texto) #Adiciona o texto ao PDF
pdf.showPage() #Finaliza página atual

#Adicionar grafico de barras
pdf.setFont('Helvetica-Bold', 16) #Define a fonte e o tamanho
pdf.drawString(2*cm, altura - 10*cm, 'Falhas por localização') #Adiciona o título ao PDF
grafico_barras = 'falhas_por_local.png' #Define o caminho da imagem
largura_imagem_barra = 15*cm #Define a largura e altura da imagem/Ajustar tamanho
pdf.drawImage(grafico_barras, 2*cm, altura - 10*cm, width = largura_imagem_barra, height = 8*cm) #Adiciona a imagem ao PDF
pdf.showPage() #Finaliza página atual

#Adicionar tabela de temperatura média por equipamento
dados_tabela = [['Equipamento', 'Temperatura média (°C)']] #Cabeçalho
for equipamento, temp in temperatura_media_por_equipamento.items(): #Para cada equipamento e temperatura em temperatura_media_por_equipamento
    dados_tabela.append([equipamento, f'{temp:.2f}'])



tabela = Table(dados_tabela, colWidths = [5*cm, 5*cm]) #Cria a tabela
tabela.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0,0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])) #Estilo da tabela
tabela.wrapOn(pdf, 0, 0)
tabela. drawOn(pdf, 2*cm, altura - 20*cm) #Ajuste coordenadas (x, y )
pdf.save() #Salva o PDF

#Criar uma função que envie os emails
def enviar_email(destinatario, assunto, corpo, anexo_pdf):
    #Configuração do servidor SMTP
    servidor_smtp = 'smtp.gmail.com'
    porta = 587 
    email_remetente = 'seu_email@gmail.com'
    senha_app = 'sua_app_senha_google' #Necessario, pois a 2FA está ativada

    #Criar mensagem
    mensagem = MIMEMultipart()
    mensagem['From'] = email_remetente
    mensagem['To'] = ','.join(destinatarios) #join para permitir uma lista de destinatarios

    #Corpo do email
    mensagem.attach(MIMEText(corpo, 'plain'))

    #Anexar PDF 
    with open(anexo_pdf, 'rb') as anexo: 
        parte = MIMEApplication(anexo.read(), Name = 'Relatorio.pdf')
        parte['Content-Disposition'] = f'attachment; filename = "Relatorio.pdf"'
        mensagem.attach(parte)

    #Enviar
    try:
        with smtplib.SMTP(servidor_smtp, porta) as servidor:
            servidor.starttls()
            servidor.login(email_remetente, senha_app)
            servidor.sendmail(email_remetente, destinatarios, mensagem.as_string())
            print('Email enviado com sucesso') 
    except Exception as e:
        print(f'Erro ao enviar email: {str(e)}')


#Enviar email 
destinatarios = ['email_gestores@gmail.com']
assunto = 'Relatório de Análise de Equipamentos'
corpo = '''
Prezados gestores,

Segue em anexo o relatório automático de análise de equipamentos.

Atenciosamente,
Sistema AutoReport Factory
'''
for destinatario in destinatarios:
    enviar_email(
        destinatario=destinatarios,
        assunto=assunto,
        corpo=corpo,
        anexo_pdf='Relatorio.pdf'
    )

    








