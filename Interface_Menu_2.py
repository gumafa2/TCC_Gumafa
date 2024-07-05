# Importação das bibliotecas
import customtkinter as ctk
import subprocess
from PIL import Image, ImageTk

ctk.set_default_color_theme("blue") # Seleção do tema azul do customtkinter


def iniciar_codigo_1(): # Definição da função para chamar o programa correspondente
    menu_principal.withdraw()
    subprocess.run(["python", "reconstrução_estatica_tcc.py"])

def iniciar_codigo_2(): # Definição da função para chamar o programa correspondente
    menu_principal.withdraw()
    subprocess.run(["python", "reconstrução_temporal_tcc.py"])
    
def iniciar_codigo_3(): # Definição da função para chamar o programa correspondente
    menu_principal.withdraw()
    subprocess.run(["python", "roi_contagem.py"])

def sair_do_programa(): # Definição da função de sair do programa
    menu_principal.destroy()

# Criação a janela do menu principal
menu_principal = ctk.CTk()
menu_principal.title("Menu")
menu_principal.geometry("626x470")

# Carregamento da imagem de fundo
background_image = Image.open(r"C:\Users\gumafa\Desktop\art7.png")
background_photo = ImageTk.PhotoImage(background_image)

# Criação um label para a imagem de fundo
background_label = ctk.CTkLabel(menu_principal, image=background_photo,text='')
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Criação um label para o texto
texto_label = ctk.CTkLabel(menu_principal, text="Tomografia por Impedância Elétrica", font=("Roboto", 30), text_color="white",bg_color="#9be2de",fg_color="transparent")
# Ajuste da posição x e y do label
texto_label.place(relx=1.0, rely=0, x=-10, y=30, anchor="ne")

# Altura e largura dos botões
botao_largura = 100
botao_altura = 50

# Calculo para posicionamento dos botões
espaco = 30  
altura_total_botoes = botao_altura * 3 + espaco * 2
posicao_y_inicial = (420 - altura_total_botoes) / 2 + altura_total_botoes * 0.15  

# Posição horizontal dos botões 
posicao_x = 626 - botao_largura - 60  

# Botão para o Código 1
botao_codigo_1 = ctk.CTkButton(menu_principal, text="Análise estática", command=iniciar_codigo_1, bg_color="#9be2de", width=botao_largura, height=botao_altura)
botao_codigo_1.place(x=posicao_x, y=posicao_y_inicial)

# Botão para o Código 2
botao_codigo_2 = ctk.CTkButton(menu_principal, text="Seq. Temporal", command=iniciar_codigo_2, bg_color="#9be2de", width=botao_largura, height=botao_altura)
botao_codigo_2.place(x=posicao_x, y=posicao_y_inicial + botao_altura + espaco)

# Botão para o Código 3
botao_codigo_3 = ctk.CTkButton(menu_principal, text="Dinâmico Pulmonar", command=iniciar_codigo_3, bg_color="#9be2de", width=botao_largura, height=botao_altura)
botao_codigo_3.place(x=posicao_x, y=posicao_y_inicial + 2 * (botao_altura + espaco))

# Botão para sair do aplicativo
botao_sair = ctk.CTkButton(menu_principal, text="Sair", command=sair_do_programa, bg_color="#9be2de", width=botao_largura, height=botao_altura)
botao_sair.place(x=posicao_x, y=posicao_y_inicial + 3 * (botao_altura + espaco))

menu_principal.mainloop()