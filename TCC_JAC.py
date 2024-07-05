from __future__ import absolute_import, division, print_function
import matplotlib.pyplot as plt  # Para plotagem de gráficos.
import numpy as np  # Biblioteca para operações matemáticas.
import pyeit.eit.jac as jac  # Importação do solucionador JAC do pyEIT.
import pyeit.mesh as mesh  # Ferramentas de malha do pyEIT.
from pyeit.eit.fem import EITForward  # Ferramenta para simulação FEM.
from pyeit.eit.interp2d import sim2pts  # Ferramenta para interpolação 2D.
from pyeit.mesh.shape import thorax  # Formato pré-definido de tórax para malha.
import pyeit.eit.protocol as protocol  # Protocolos de medição para EIT.
from pyeit.mesh.wrapper import PyEITAnomaly_Circle  # Para criar anomalias na malha.

# Geração da malha
n_el = 16  # Número de eletrodos.
use_customize_shape = False  

if use_customize_shape:
    mesh_obj = mesh.create(n_el, h0=0.1, fd=thorax)
else:
    mesh_obj = mesh.create(n_el, h0=0.1)

# Extração dos nós e elementos da malha.
pts = mesh_obj.node
tri = mesh_obj.element
x, y = pts[:, 0], pts[:, 1]

# Criação de uma anomalia com localização e permissividade aleatórias.
angle = np.random.uniform(0, 2 * np.pi)
radius = np.random.uniform(0, 1)
center_x = radius * np.cos(angle)
center_y = radius * np.sin(angle)
radius = np.random.uniform(0.05, 0.4)
conductivity = np.random.uniform(1, 1000)
anomaly = PyEITAnomaly_Circle(center=[center_x, center_y], r=radius, perm=conductivity)
mesh_new = mesh.set_perm(mesh_obj, anomaly=anomaly)

# Configuração das condições de varredura para a simulação por Elementos Finitos (FEM).
protocol_obj = protocol.create(n_el, dist_exc=8, step_meas=1, parser_meas="std")
fwd = EITForward(mesh_obj, protocol_obj)
v0 = fwd.solve_eit()
v1 = fwd.solve_eit(perm=mesh_new.perm)

# Configuração e utilização do solucionador Jacobiano (JAC) para reconstrução de imagem.
eit = jac.JAC(mesh_obj, protocol_obj)
eit.setup(p=0.5, lamb=0.01, method="kotre", perm=1, jac_normalized=True)
ds = eit.solve(v1, v0, normalize=True)
ds_n = sim2pts(pts, tri, np.real(ds))

# Gráficos para mostrar a forma real da anomalia e a reconstrução de EIT.
fig, axes = plt.subplots(1, 2, constrained_layout=True)
fig.set_size_inches(9, 4)

# Plot da distribuição de permissividade real
ax = axes[0]
delta_perm = mesh_new.perm - mesh_obj.perm
im = ax.tripcolor(x, y, tri, np.real(delta_perm), shading="flat")
ax.set_aspect("equal")

# Plot da reconstrução EIT
ax = axes[1]
im = ax.tripcolor(x, y, tri, ds_n, shading="flat")
for i, e in enumerate(mesh_obj.el_pos):
    ax.annotate(str(i + 1), xy=(x[e], y[e]), color="r")
ax.set_aspect("equal")

# Adição da barra de cores
fig.colorbar(im, ax=axes.ravel().tolist())
plt.show()
