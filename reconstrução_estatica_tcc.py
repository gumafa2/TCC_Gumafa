# Importação das bibliotecas necessárias
from scipy.io import loadmat  # Carrega arquivos .mat do MATLAB
import pyeit.mesh as mesh  # Ferramentas de malha do pyEIT
import pyeit.eit.protocol as protocol  # Protocolos de medição do pyEIT
from pyeit.mesh.external import place_electrodes_equal_spacing  # Ferramenta para posicionar eletrodos na malha
import numpy as np  # Biblioteca para cálculo numérico
import pyeit.eit.jac as jac  # Solucionador jacobiano para reconstrução da imagem
import matplotlib.pyplot as plt  # Plotagem de gráficos
from pyeit.visual.plot import create_plot  # Função do pyEIT para criar gráficos
from pathlib import Path  # Manipulação de caminhos de sistema de arquivos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Integração do matplotlib com tkinter
import customtkinter as ctk # Criação da interface do usuário
from PIL import Image, ImageTk # Manipulação e exibição de imagens
import os # Integração com o sistema operacional
import tkinter as tk # Criação da interface do usuário
from tkinter import ttk # Criação da interface do usuário
import subprocess

# Cria janela principal da interface gráfica
window = ctk.CTk()  
window.title("Reconstrução de Imagem EIT")
window.geometry("800x600")

# Configuração inicial do customtkinter
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

frame_seletor = ctk.CTkFrame(window)
frame_seletor.pack(side='top', fill='x', padx=10, pady=5)  

# Função da reconstrução da imagem
def gerar_e_exibir_imagem(data_file_path):

    # Define configurações iniciais baseadas na documentação do dataset 
    skip_2_range = range(33 - 1, 48)  # A indexação do MATLAB começa em 1 e no Python em 0, alem disso é inclusivo no final de um intervalo portanto é necessario subtrair 1 para alinhar a indexação
    dist_exc = 2 + 1  # Define distância entre eletrodos de excitação pois os atuais eletrodos de injeção estão dentro da contagem
    n_electrodes = 16 # Numero de eletrodos do dataset
    counter_clockwise = False # Define a direção do posicionamento dos eletrodos 
    starting_angle = 0 # Ângulo inicial para posicionamento dos eletrodos
    starting_offset = 0 # Deslocamento inicial para posicionamento dos eletrodos
    step_meas = 1  # Define passo para medições adjacentes
    parser_meas = "std"  # Medições começam sempre no primeiro eletrodo
    
    # Carregamento dos dados do dataset
    dataset_directory = Path("eit_dataset") # Define diretório do dataset
    background_file_path = Path(r"C:\Users\gumafa\Desktop\TCC\eit_dataset\data_mat_files\data_mat_files\datamat_1_0.mat")
    background_data_raw = loadmat(background_file_path) # Carrega dados de referência
    data_raw = loadmat(data_file_path)  # Carrega dados do arquivo selecionado
    
    # Remoção os dados onde a excitação e medição se sobrepoem pois o pyEIT não os utiliza
    current_pattern = background_data_raw["CurrentPattern"][:, skip_2_range] != 0
    meas_pattern = background_data_raw["MeasPattern"] != 0
    overlaps = []
    for current_column in current_pattern.T:
        overlaps_column = []
        for meas_column in meas_pattern.T:
            overlap = np.any(np.logical_and(current_column, meas_column))
            overlaps_column.append(overlap)
    
        overlaps.append(overlaps_column)
    
    no_overlaps = np.logical_not(overlaps).T
    
    background_data = background_data_raw["Uel"][:, skip_2_range].T[no_overlaps.T].T
    data = data_raw["Uel"][:, skip_2_range].T[no_overlaps.T].T
    
    # Processo normal de reconstrução de imagem pelo pyEIT
    recon_mesh = mesh.create(n_electrodes, h0=0.05) # Cria malha de reconstrução
    electrode_nodes = place_electrodes_equal_spacing(recon_mesh, n_electrodes=n_electrodes, starting_angle=starting_angle, starting_offset=starting_offset) # Posiciona eletrodos
    recon_mesh.el_pos = np.array(electrode_nodes) # Define posição dos eletrodos na malha
    protocol_obj = protocol.create(n_electrodes, dist_exc=dist_exc, step_meas=step_meas, parser_meas=parser_meas) # Cria objeto de protocolo
    eit = jac.JAC(recon_mesh, protocol_obj) # Cria objeto JAC para reconstrução
    eit.setup(p=0.5, lamb=0.05, method="kotre", jac_normalized=False) # Configura parâmetros do solucionador JAC
    
    solution = np.real(eit.solve(data, background_data)) # Resolve reconstrução e obtém solução real
    
    fig, ax = plt.subplots() # Cria figura e eixo para plotagem
    create_plot(ax, solution, recon_mesh, electrodes=np.array(electrode_nodes)) # Plot da solução
    ax.set_title(f"Reconstrução da Imagem: {Path(data_file_path).stem}") # Título do gráfico
    return fig

# Função para integrar a geração de imagem com a interface

panel_divider = ttk.PanedWindow(orient="horizontal")  # Cria um divisor horizontal
panel_divider.pack(fill="both", expand=True)

# Painel esquerdo para a imagem de referência
left_panel = ctk.CTkFrame(master=panel_divider, fg_color="#ffffff")
left_panel.configure(bg_color='white')
panel_divider.add(left_panel, weight=1)  

# Painel direito para a imagem reconstruida
right_panel = ctk.CTkFrame(master=panel_divider, fg_color="#ffffff")
panel_divider.add(right_panel, weight=1) 

def integrar_com_geracao_de_imagem():
    global right_panel, selecionador_arquivo, mapeamento_arquivos, label_fig2, fig2_imagem # Define variáveis globais
    nome_arquivo_selecionado = selecionador_arquivo.get() # Obtém nome do arquivo selecionado
    if nome_arquivo_selecionado:
        caminho_completo = mapeamento_arquivos[nome_arquivo_selecionado] # Obtém caminho completo do arquivo
        fig = gerar_e_exibir_imagem(caminho_completo) # Gera imagem de EIT
        
        # Limpa canvas anterior e desenha nova figura
        for widget in right_panel.winfo_children():
            widget.destroy()
                
        canvas = FigureCanvasTkAgg(fig, master=right_panel)  # Cria novo canvas para figura
        canvas_widget = canvas.get_tk_widget() 
        canvas_widget.pack(fill='both', expand=True) 
        canvas.draw() 
        
        # Atualiza imagem de referência baseada no arquivo selecionado
        partes_nome = nome_arquivo_selecionado.split('_') # Divide nome do arquivo
        identificacao_arquivo = '_'.join(partes_nome[1:3]).split('.')[0]   # Obtém identificação do arquivo
        fig2_path = f"C:\\Users\\gumafa\\Desktop\\TCC\\fotos\\fantom_{identificacao_arquivo}.jpg" # Constrói caminho da foto
        fig2 = Image.open(fig2_path) # Abre imagem de referência
        resize_fig2 = fig2.resize((350, 350))  # Redimensiona imagem
        fig2_imagem = ImageTk.PhotoImage(resize_fig2) # Converte imagem para formato Tk
       
  # Atualiza a label da imagem de referência
    if 'label_fig2' in globals():
        label_fig2.configure(image=fig2_imagem, bg_color="#ffffff") # Atualiza imagem no label existente
        label_fig2.image = fig2_imagem # Atualiza referência da imagem no label
    else:
        label_fig2 = ctk.CTkLabel(left_panel, image=fig2_imagem, text='',bg_color="#ffffff")  # Cria novo label para imagem no painel esquerdo
        label_fig2.image = fig2_imagem  # Atualiza referência da imagem no label
        label_fig2.place(relx=0.5, rely=0.5, anchor='center')  # Empacota label no painel esquerdo
        
# Define função para listar arquivos .mat em um diretório
def listar_arquivos_dataset(diretorio):
    arquivos = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.mat')]  # Lista arquivos .mat
    return arquivos  # Retorna lista de arquivos

# Define função para criar mapeamento entre nomes de arquivos e seus caminhos completos
def criar_mapeamento_arquivos(diretorio):
    arquivos = os.listdir(diretorio)  # Lista arquivos no diretório
    mapeamento_arquivos = {}  # Cria dicionário para mapeamento
    for arquivo in arquivos:
        if arquivo.endswith('.mat'):  # Verifica se o arquivo é .mat
            mapeamento_arquivos[arquivo] = str(Path(diretorio) / arquivo)  # Adiciona par nome-caminho ao dicionário
    return mapeamento_arquivos 


# Criação de frames para organização da interface
frame_botao = ctk.CTkFrame(window)
frame_botao.pack(side='bottom', fill='x', padx=10, pady=5)  

# Define função para adicionar seletor de arquivo à interface
def adicionar_seletor_arquivo(frame):
    diretorio = r"C:\Users\gumafa\Desktop\TCC\eit_dataset\data_mat_files\data_mat_files"  
    mapeamento_arquivos = criar_mapeamento_arquivos(diretorio)  
    
    label_seletor = ctk.CTkLabel(frame, text="Selecione o arquivo")  
    label_seletor.pack(side='top', fill='x', padx=10, pady=2, anchor='center')  
    selecionador_arquivo = ttk.Combobox(frame, values=list(mapeamento_arquivos.keys()), width=200)
    selecionador_arquivo.pack(side='top', padx=10, pady=5, anchor='center')
    return selecionador_arquivo, mapeamento_arquivos

# Adiciona seletor de arquivo à interface
selecionador_arquivo, mapeamento_arquivos = adicionar_seletor_arquivo(frame_seletor)

# Função para retornar ao menu principal
def retornar_ao_menu_principal():
    window.destroy()  
    subprocess.run(["python", "Interface_Menu_2.py"])  # Abre o menu principal


# Cria botão para iniciar reconstrução e exibição da imagem
botao_gerar = ctk.CTkButton(frame_botao, text="Gerar Imagem", command=integrar_com_geracao_de_imagem)
botao_gerar.pack(side='left', pady=5, anchor='center')  

# Cria botão para retornar ao menu principal
botao_retornar = ctk.CTkButton(frame_botao, text="Voltar", command=retornar_ao_menu_principal)
botao_retornar.pack(side='right', pady=5, anchor='center')  

window.mainloop()  
