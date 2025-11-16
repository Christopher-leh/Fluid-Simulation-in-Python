# 2D Fluid Simulation in Python

This project implements an interactive 2D fluid solver based on the incompressible Navier–Stokes equations.  
The simulation combines **semi-Lagrangian advection**, **FFT-based diffusion**, and an **FFT-based pressure projection**, while a Pygame interface provides real-time interaction and visualization.

---

### 🔹 Algorithm

Each frame, the velocity and density fields are advected using a semi-Lagrangian step with bilinear interpolation.  
User input adds forces directly to the velocity field. Diffusion and the pressure solve are performed in Fourier space, ensuring stability and enforcing incompressibility.  
Density is transported in the same way and lightly damped. With periodic boundaries and these stable update rules, the simulation produces smooth, swirling 2D flow.

---

### 🔹 Pygame Interface

- Adjustable simulation size and scaling  
- Real-time parameter menu (viscosity, timestep, radius, speed, resolution, colour)  
- Interactive mouse input for forcing and density  
- Optional velocity-field visualization  
- Info overlay on hover  

---

### Controls

- **Right Mouse Button** – Add velocity (forces)  
- **Left Mouse Button** – Add density (“smoke”)  

---

## Simulation Examples

<p float="left">
  <img src="assets/fluid1.gif" width="32%" />
  <img src="assets/fluid2.gif" width="32%" />
  <img src="assets/fluid3.gif" width="32%" />
</p>

---

## Installation & Run

1. Install the required packages:
   pip install -r requirements.txt

2. Start the simulation:
   python main.py

The Pygame window will open immediately and can be controlled with the mouse.

---

### References

- Jos Stam – *Stable Fluids* (1999), SIGGRAPH
  https://pages.cs.wisc.edu/~chaol/data/cs777/stam-stable_fluids.pdf
- Jos Stam – *Real-Time Fluid Dynamics for Games* (2003)  
  https://graphics.cs.cmu.edu/nsp/course/15-464/Fall09/papers/StamFluidforGames.pdf  
- Eulerian Grid-Based Fluid Simulation (Seminar Report, Universität Freiburg)  
  https://cg.informatik.uni-freiburg.de/intern/seminar/gridFluids_fluid-EulerParticle.pdf

---

## License  
MIT License
