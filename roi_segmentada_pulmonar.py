import os
import numpy as np
import matplotlib.pyplot as plt
from pyeit.mesh.external import load_mesh, place_electrodes_equal_spacing
from pyeit.visual.plot import create_mesh_plot, create_plot
import pyeit.eit.protocol as protocol
from pyeit.eit.jac import JAC
from pyeit.eit.fem import EITForward

def main():
    simulation_mesh_filename = (
        "mesha06_bumpychestslice_radiological_view_both_lungs_1_0-3.ply"
    )
    n_electrodes = 16

    current_dir = os.path.dirname(os.path.abspath(__file__))
    sim_mesh = load_mesh(os.path.join(current_dir, simulation_mesh_filename))
    electrode_nodes = place_electrodes_equal_spacing(sim_mesh, n_electrodes=16)
    sim_mesh.el_pos = np.array(electrode_nodes)

    fig, ax = plt.subplots()
    create_mesh_plot(
        ax, sim_mesh, electrodes=electrode_nodes, coordinate_labels="radiological"
    )

    protocol_obj = protocol.create(
        n_electrodes, dist_exc=int(n_electrodes / 2), step_meas=1, parser_meas="std"
    )
    fwd = EITForward(sim_mesh, protocol_obj)
    vh = fwd.solve_eit(perm=1)
    vi = fwd.solve_eit(perm=sim_mesh.perm)

    pyeit_obj = JAC(sim_mesh, protocol_obj)
    pyeit_obj.setup(p=0.5, lamb=0.001, method="kotre", perm=1, jac_normalized=False)

    ds_sim = pyeit_obj.solve(vi, vh, normalize=False)
    solution = np.real(ds_sim)

    fig, ax = plt.subplots()
    create_plot(
        ax,
        solution,
        pyeit_obj.mesh,
        electrodes=electrode_nodes,
        coordinate_labels="radiological",
    )

    threshold = -1  
    lung_regions = solution > threshold

    # Destaque dos pulmões
    ax.tripcolor(
        pyeit_obj.mesh.node[:, 0],
        pyeit_obj.mesh.node[:, 1],
        pyeit_obj.mesh.element,
        lung_regions,
        shading='flat',
        cmap='Blues',
        alpha=0.3
    )

    plt.show()

if __name__ == "__main__":
    main()
    