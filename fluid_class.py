#Klasse der Simulation für das Fluid, hier werden Werte initialisiert und der Algorithmus definiert

import numpy as np
from fluid_functions import *


class FluidSimulation:

    def __init__(self, N, dt, visc):
        self.N = N               # Gittergröße (Anzahl der Zellen)
        self.dt = dt             # Zeitschritt
        self.visc = visc         # Viskosität
        self.center = N//2     # Mittelpunkt des Gitters
        self.force = 0.0         # Kraftintensität
        self.draw_velocity = False  # für Visualisierung der Vektoren
        self.scaling_factor = 800 / self.N  # Skalierungsfaktor für die Darstellung
        self.shape = (self.N, self.N)   #shape der Felder

        # Grid Setup
        x = (np.arange(self.N) + 0.5)
        y = (np.arange(self.N) + 0.5)
        self.X, self.Y = np.meshgrid(x, y, indexing='xy')
        self.coordinates = np.dstack((self.X, self.Y))      # 3D-Array mit X,Y-Koordinaten

        # Wellenzahlen für Advekt und Projektionsschritt im Frequenzraum
        kx = 2 * np.pi * np.fft.fftfreq(self.N)        #Wellenzahlen
        ky = 2 * np.pi * np.fft.fftfreq(self.N)
        #, d=h
        self.KX, self.KY = np.meshgrid(kx, ky, indexing='xy')
        self.K_sq = (self.KX**2 + self.KY**2).astype(np.float32)    #k² berechnen
        self.K_sq[0, 0] = 1     #teilen durch 0 verhindern


        # Initialisierung der Felder

        self.u = np.zeros(self.shape, dtype=np.float32)
        self.u_prev = np.zeros(self.shape, dtype=np.float32)
        self.v = np.zeros(self.shape, dtype=np.float32)
        self.v_prev = np.zeros(self.shape, dtype=np.float32)
        self.density = np.zeros(self.shape, dtype=np.float32)
        self.density_prev = np.zeros(self.shape, dtype=np.float32)
        self.uforce = np.zeros(self.shape, dtype=np.float32)
        self.vforce = np.zeros(self.shape, dtype=np.float32)

    #Führt einen step der Simulation durch
    def step(self):

        #Speichern von aktuellen Zuständen
        self.u_prev = self.u.copy()
        self.v_prev = self.v.copy()
        self.density_prev = self.density.copy()

        #Advektion von Vektorfeldern
        self.u = advect_velocity(self.u, self.u_prev, self.v_prev,
                       self.coordinates, self.dt, self.N)
        self.v = advect_velocity(self.v, self.u_prev, self.v_prev,
                       self.coordinates, self.dt, self.N)

        #Kräfte hinzufügen
        self.u = add_force(self.u, self.dt, self.uforce)
        self.v = add_force(self.v, self.dt, self.vforce)
        self.uforce *= 0.8      #Kräfte mir der Zeit abschwächen
        self.vforce *= 0.8

        #Diffusion von Vektorfeldern (Viskositätseffekte)
        self.u = diffuse(self.u, self.visc, self.dt, self.K_sq)
        self.v = diffuse(self.v, self.visc, self.dt, self.K_sq)

        #Projektion - Sicherstellen der Divergenzfreiheit
        self.u, self.v = project(self.u, self.v, self.KX, self.KY, self.K_sq)

        #Dichte bewegen und Diffusionsgleichung lösen
        self.density = advect_density(self.density_prev, self.u_prev, self.v_prev,
                           self.coordinates, self.dt, self.N)
        self.density = diffuse(self.density, self.visc* 0.1, self.dt, self.K_sq)        #geringere Diffusion der Dichte : visc*0.1
        self.density *= 0.999         # Langsames Abschwächen der Dichte


    #Setzt alle Felder zurück auf Null (Neustart der Simulation)
    def clear(self):
        self.density = np.zeros(self.shape, dtype=np.float32)
        self.u = np.zeros(self.shape, dtype=np.float32)
        self.v = np.zeros(self.shape, dtype=np.float32)
        self.uforce = np.zeros(self.shape, dtype=np.float32)
        self.vforce = np.zeros(self.shape, dtype=np.float32)

    #Hilfsfunktion für Umschalten der Visualisierung der Geschwindigkeitsfelder
    def draw(self):
        self.draw_velocity = not self.draw_velocity



