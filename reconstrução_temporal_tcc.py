import tkinter as tk
from tkinter import ttk
from scipy.io import loadmat
import pyeit.mesh as mesh
import pyeit.eit.protocol as protocol
from pyeit.mesh.external import place_electrodes_equal_spacing
import numpy as np
import pyeit.eit.jac as jac
import matplotlib.pyplot as plt
from pyeit.visual.plot import create_plot
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from PIL import Image, ImageSequence, ImageTk
import imageio
import customtkinter as ctk
import time
import io
import subprocess

# Função da reconstrução da imagem
def gerar_e_exibir_imagem(data_file_path, resize_factor=1.0):
    
    # Define as configurações com base na documentação do dataset
    skip_2_range = range(33 - 1, 48)
    dist_exc = 2 + 1  
    n_electrodes = 16  
    counter_clockwise = False
    starting_angle = 0
    starting_offset = 0
    
    # Configurações de medida
    step_meas = 1  
    parser_meas = "std"  
    
    # Carregamento dos dados do dataset
    background_file_path = Path(r"C:\Users\gumafa\Desktop\TCC\eit_dataset\data_mat_files\data_mat_files\datamat_1_0.mat")
    background_data_raw = loadmat(background_file_path)
    data_raw = loadmat(data_file_path)  
    
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
    recon_mesh = mesh.create(n_electrodes, h0=0.05)
    electrode_nodes = place_electrodes_equal_spacing(recon_mesh, n_electrodes=n_electrodes, starting_angle=starting_angle, starting_offset=starting_offset)
    recon_mesh.el_pos = np.array(electrode_nodes)
    protocol_obj = protocol.create(n_electrodes, dist_exc=dist_exc, step_meas=step_meas, parser_meas=parser_meas)
    eit = jac.JAC(recon_mesh, protocol_obj)
    eit.setup(p=0.5, lamb=0.05, method="kotre", jac_normalized=False)
    
    solution = np.real(eit.solve(data, background_data))
    
    fig, ax = plt.subplots(figsize=(5*resize_factor, 4*resize_factor))
    create_plot(ax, solution, recon_mesh, electrodes=np.array(electrode_nodes))
    ax.set_title(f"Reconstrução da Imagem: {Path(data_file_path).stem}")
    plt.close(fig)  
    return fig

# Função modificada para gerar e exibir mais de uma imagem
def gerar_e_exibir_imagens():
    
    # Limpa o frame de canvas antes de adicionar novos
    for widget in frame_canvas.winfo_children():
        widget.destroy()

    start_time = time.time() # Inicio da contagem temporal
    
    # Define o diretório do dataset
    dataset_directory = Path("eit_dataset/data_mat_files/data_mat_files")
    arquivos = listar_arquivos_dataset(dataset_directory)[1:10]  # Limita a 9 arquivos
    figuras = []  # Lista para armazenar as figuras geradas
    tempos = []
    
    # Inicializa o contador de imagens para calcular a posição no grid
    for arquivo in arquivos:
        data_file_path = dataset_directory / arquivo
        fig = gerar_e_exibir_imagem(data_file_path, resize_factor=0.85)
        figuras.append(fig)
        
        # Captura o tempo decorrido após a criação da imagem
        elapsed_time = time.time() - start_time
        tempos.append(elapsed_time)

    # Verifica o modo selecionado 
    modo_selecionado = modo_seletor.get()
    if modo_selecionado == "Imagens":
        for i, (fig, elapsed_time) in enumerate(zip(figuras, tempos)):
            canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
            canvas_widget = canvas.get_tk_widget()
            
            # Calcula a posição da imagem no grid
            row_position = i // 3
            column_position = i % 3
            canvas_widget.grid(row=row_position * 2, column=column_position, padx=5, pady=5)
            canvas.draw()
            
            # Cria uma label para exibir o tempo decorrido
            time_label = ctk.CTkLabel(frame_canvas, text=f"Tempo: {elapsed_time:.3f} s", font=("Roboto", 10))
            time_label.grid(row=row_position * 2 + 1, column=column_position, padx=1, pady=1)  # Posiciona a label abaixo da imagem
            
    elif modo_selecionado == "GIF":
        criar_e_exibir_gif(figuras)
        
# Função para criar GIF
def criar_e_exibir_gif(figuras):
    imagens = []
    for fig in figuras:
        fig.set_size_inches(16, 12)  
        canvas = FigureCanvasTkAgg(fig)
        canvas.draw()
        buf = io.BytesIO()
        canvas.print_png(buf)
        imagem = Image.open(buf)
        imagens.append(imagem)
    gif_path = "reconstrucao_eit.gif"
    imageio.mimsave(gif_path, imagens, fps=1)
    
    # Exibe o GIF na interface
    gif = Image.open(gif_path)
    gif_frames = [ImageTk.PhotoImage(gif_frame) for gif_frame in ImageSequence.Iterator(gif)]
    
    # Cria um label para exibição do GIF
    gif_label = ctk.CTkLabel(frame_canvas,text='')
    gif_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)
    
    # Label contendo o tempo decorrido
    time_label = ctk.CTkLabel(frame_canvas, text="Tempo: 0 s")
    time_label.grid(row=1, column=0, sticky="ew")
    
    start_time = time.time()
    
    # Função para atualizar o frame do GIF
    def update(ind=0):
        frame = gif_frames[ind]
        gif_label.configure(image=frame)
        ind += 1
        if ind == len(gif_frames):
            ind = 0
        elapsed_time = time.time() - start_time
        time_label.configure(text=f"Tempo: {elapsed_time:.2f} s")
        frame_canvas.after(1000, update, ind)
        
    update()  # Inicia a exibição do GIF
    
# Função para listar os arquivos do dataset
def listar_arquivos_dataset(diretorio):
    arquivos = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.mat')]
    return arquivos

# Cria a janela principal da interface
window = ctk.CTk()
window.title("Reconstrução de Imagem EIT")
window.geometry("890x800")

# Configuração inicial do customtkinter
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")  

# Frame para o seletor de modos
frame_seletor_modo = ctk.CTkFrame(window)
frame_seletor_modo.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=5)

# Frame para o canvas onde as imagens serão exibidas
frame_canvas = ctk.CTkFrame(window)
frame_canvas.pack(fill=ctk.BOTH, expand=True)

# Seletor de modos (Imagens ou GIF)
modo_seletor = ctk.CTkComboBox(frame_seletor_modo, values=["Imagens", "GIF"], state="readonly")
modo_seletor.pack(side=ctk.LEFT, padx=10, pady=5)
modo_seletor.set("Imagens")

# Botão para iniciar a geração e exibição das imagens ou GIF
botao_gerar = ctk.CTkButton(frame_seletor_modo, text="Gerar Imagem", command=gerar_e_exibir_imagens)
botao_gerar.pack(side=ctk.LEFT, padx=10, pady=5)

# Função para retornar ao menu principal
def retornar_ao_menu_principal():
    window.destroy()  
    subprocess.run(["python", "Interface_Menu_2.py"])  


botao_retornar = ctk.CTkButton(frame_seletor_modo, text="Voltar", command=retornar_ao_menu_principal)
botao_retornar.pack(side=ctk.RIGHT, padx=10, pady=5)


window.mainloop()