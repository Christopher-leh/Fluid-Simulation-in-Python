#Funktionen, welche zur Lösung der Navier-stokes Gleichung gebraucht werden

import numpy as np
from scipy.ndimage import map_coordinates


#Fügt einem Vektorfeld externe Kräfte hinzu
def add_force(field, dt, force):
        field += dt * force
        return field


#Bewegt ein Dichtefeld entlang eines Geschwindigkeitsfeldes, Semi-Lagrange Advektion
def advect_density(field, u_prev, v_prev, coordinates, dt, Gridsize):
    # Berechnet die Rückwärtsposition von Partikeln (Backtracing)
    Xb = (coordinates[:, :, 0] - dt * u_prev) % Gridsize
    Yb = (coordinates[:, :, 1] - dt * v_prev) % Gridsize

    #interpolieren der Rückwärtsposition auf unser Gitter
    advected = map_coordinates(
    field,
    [Yb.ravel() - 0.5, Xb.ravel() - 0.5],             #brauch 1D input, ravel statt flatten, da es keine kopie erzeugt sondern nur einen view
    order=1,
    mode='wrap'                                           # "wrap" für periodische randbedingung
    ).reshape(field.shape)

    # Sicherstellen, dass keine negativen Werte (negative Dichte) entstehen
    advected = np.clip(advected, 0.0, None)

    return advected


#Bewegt Geschwindigkeitsfeld anhand des letzten Geschwindigkeitsfeldes
#Wie advect_density. nur ohne das beschränken auf positive werte, da negative Geschwindigkeiten notwendig sind
def advect_velocity(field, u_prev, v_prev, coordinates, dt, Gridsize):
    #Bewegt das Feld mit dem Geschwindigkeitsfeld
    Xb = (coordinates[:, :, 0] - dt * u_prev) % Gridsize
    Yb = (coordinates[:, :, 1] - dt * v_prev) % Gridsize

    advected = map_coordinates(
    field,
    [Yb.ravel() - 0.5, Xb.ravel() - 0.5],
    mode='wrap'
    ).reshape(field.shape)

    return advected

#Lösen der Diffusionsgleichung im Frequenzraum
def diffuse(field, viscosity, dt, K_sq):
    field_hat = np.fft.fft2(field)
    # Die Lösung im Frequenzraum entspricht: u_hat / (1 + ν*dt*k²)
    diffused = np.real(np.fft.ifft2(field_hat / (1 + viscosity * dt * K_sq)))
    return diffused


#Projiziert das Geschwindigkeitsfeld auf ein divergenzfreies Feld.
#Dies ist notwendig, um die Inkompressibilitätsbedingung zu erfüllen (Divergenzfreiheit).
#Wird im Frequenzraum glöst, da sich die Gleichung dort sehr stark vereinfacht
def project(u, v, KX, KY, K_sq):

    u_hat = np.fft.fft2(u)
    v_hat = np.fft.fft2(v)

    # Berechne die Divergenz im Frequenzraum wobei ∇ = i*k
    div_hat = 1j * (KX * u_hat + KY * v_hat)
    #mittelwert der Divergenz śoll 0 sein
    div_hat[0, 0] = 0

    # Löse die Poisson-Gleichung im Frequenzraum: Δp = ∇*uv mit Δ = -k²
    p_hat = div_hat / (-K_sq)

    #setze mittelwert des Drucks auf 0, führt zu eindeutiger Lösung
    p_hat[0, 0] = 0

    # Subtrahiere den Gradienten des Drucks u = u_alt - ∇p
    u_hat -= 1j * KX * p_hat
    v_hat -= 1j * KY * p_hat

    return np.real(np.fft.ifft2(u_hat)), np.real(np.fft.ifft2(v_hat))
