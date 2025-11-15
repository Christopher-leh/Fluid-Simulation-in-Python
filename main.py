#Hauptprogrammm, dass fluid simulation in pygame visualisiert und einstellungen ermöglicht

from fluid_class import FluidSimulation
import numpy as np
from scipy.ndimage import gaussian_filter
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.dropdown import Dropdown
from sys import exit


# Helper Functions
#setzt den wert der textbox gleich dem des sliders
def sync_slider_change(slider, textbox, is_integer=False):

    value = slider.getValue()
    if is_integer:
        textbox.setText(f"{int(value)}")
    else:
        textbox.setText(f"{value:.2f}")

    return value

#überprüft eingabe in textbox und ändert wert des sliders dementsprechend
def sync_textbox_input(textbox, slider, is_integer=False):
    try:
        #leere eingabe
        if textbox.getText() == "":
            value = slider.getValue()
        else:
            value = float(textbox.getText())
            if is_integer:
                value = int(value)

        value = max(slider.min, min(slider.max, value))
        slider.setValue(value)

        if is_integer:
            textbox.setText(f"{int(value)}")
        else:
            textbox.setText(f"{value:.2f}")
    #falsche eingabe
    except (ValueError, TypeError):
        value = slider.getValue()
        if is_integer:
            textbox.setText(f"{int(value)}")
        else:
            textbox.setText(f"{value:.2f}")
    return value


#dichtefeld wird auf ein surface gezeichnet, eingabe von farbwerten ist möglich
def visualisation(surf, density, r, g, b):
    density_mask = density.copy()
    density_mask[density_mask < 1e-10] = 0
    density_mask = np.log1p(density_mask * 10)  #kleinere dichten länger darstellen

    #normalisieren und kleiner extra term um division durch 0 zu verhindern
    normalized = (density_mask - np.min(density_mask)) / (np.max(density_mask) - np.min(density_mask) + 1e-17)
    normalized = np.clip(normalized, 0.0, 1.0)

    #rgb matrizen im benötitgem vormat berechnen
    rgb_1 = (normalized * r).astype(np.uint8)
    rgb_2 = (normalized * g).astype(np.uint8)
    rgb_3 = (normalized * b).astype(np.uint8)

    #mit rgb matrizen auf surface zeichnen
    pygame.surfarray.blit_array(surf, np.stack([rgb_1, rgb_2, rgb_3], axis=-1))


def main():
    #Parameter für die fluidsimulation initialisieren
    N = 200
    dt = 0.3
    visc = 0.001

    # Fluid initialisieren
    fluid = FluidSimulation(N, dt, visc)

    #Pygame initialisieren
    pygame.init()
    width, height = 1100, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fluid Simulation")
    clock = pygame.time.Clock()                                  #clock für fps beschränkung
    try:
        font = pygame.font.Font("assets/Montserrat-Regular.ttf", 20)    #schriftart setzen
    except:
        font = pygame.font.Font(None, 20)                        #wenn nicht möglich standard schriftart

    #Surfaces definieren
    #quadratisches Surface für Simulation
    sim_surf = pygame.Surface((fluid.N, fluid.N))
    sim_surf_rect = pygame.Rect(0, 0, fluid.N * fluid.scaling_factor, fluid.N * fluid.scaling_factor)       #rectangel zum leichteren plazieren

    #Surface am rechten Rand für Einstellungen
    set_surf = pygame.Surface((width - fluid.N * fluid.scaling_factor, height))
    set_surf.fill((20, 20, 20))

    #Info surface das bei hovern über info über der simulation angezeigt wird
    info_surf = pygame.Surface((fluid.N * fluid.scaling_factor - 150, fluid.N * fluid.scaling_factor - 150))
    info_surf_rect = info_surf.get_rect(topleft=(75, 75))
    info_surf.fill("lightgrey")

    #für standort der widgets
    widget_x = width - 160
    widget_y = 20

    #Timestep slider
    timestep_title = font.render("Timestep:", True, "white")                                            #titel des sliders links davon
    timestep_title_rect = timestep_title.get_rect(midright=(widget_x - 15, widget_y + 5))               #rectangel zum leichteren plazieren
    timestep_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0, max=5, step=0.01, initial=1.0) #slider erstellen
    timestep_value = TextBox(                                                                           #textbox zum anzeigen des wertes
        screen, widget_x + 115, widget_y - 10, 40, 30,                                                  #Ort und Größe
        fontSize=15,
        onSubmit=lambda: sync_textbox_input(timestep_value, timestep_slider)                            #bei eingabe slider wert aktualisieren
    )
    timestep_value.setText(f"{timestep_slider.getValue():.2f}")                                            #Textbox-wert setzen

    #Viskosität slider
    widget_y += 40
    visc_title = font.render("Viscosity:", True, "white")
    visc_title_rect = visc_title.get_rect(midright=(widget_x - 15, widget_y + 5))
    visc_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0, max=1.5, step=0.005, initial=0.0)
    visc_value = TextBox(screen, widget_x + 115, widget_y - 10, 40, 30, fontSize=15,
                         onSubmit=lambda: sync_textbox_input(visc_value, visc_slider))
    visc_value.setText(f"{visc_slider.getValue():.3f}")

    #Radius Slider
    widget_y += 40
    radius_title = font.render("Radius:", True, "white")
    radius_title_rect = radius_title.get_rect(midright=(widget_x - 15, widget_y + 5))
    radius_slider = Slider(screen, widget_x, widget_y, 100, 10, min=1, max=100, step=1, initial = 35)
    radius_value = TextBox(screen, widget_x + 115, widget_y - 10, 40, 30, fontSize=15,
                           onSubmit=lambda: sync_textbox_input(radius_value, radius_slider, True))
    radius_value.setText(str(int(radius_slider.getValue())))

    #Speed Slider
    widget_y += 40
    speed_title = font.render("Speed:", True, "white")
    speed_title_rect = speed_title.get_rect(midright=(widget_x - 15, widget_y + 5))
    speed_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0.01, max=2, step=0.001, initial=1.0)
    speed_value = TextBox(screen, widget_x + 115, widget_y - 10, 40, 30, fontSize=15,
                          onSubmit=lambda: sync_textbox_input(speed_value, speed_slider))
    speed_value.setText(f"{speed_slider.getValue():.3f}")

    #Resolution Slider
    widget_y += 40
    res_title = font.render("Resolution:", True, "white")
    res_title_rect = res_title.get_rect(midright=(widget_x - 15, widget_y + 5))
    res_slider = Slider(screen, widget_x, widget_y, 100, 10, min=10, max=500, step=10, initial=300)
    res_value = TextBox(screen, widget_x + 115, widget_y - 10, 40, 30, fontSize=15,
                        onSubmit=lambda: sync_textbox_input(res_value, res_slider, True))
    res_value.setText(str(int(res_slider.getValue())))

    #RGB Slider
    widget_y += 50
    colour_title = font.render("Colour:", True, "white")
    colour_title_rect = res_title.get_rect(midright=(widget_x - 15, widget_y + 5))
    red_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0, max=255, step=5, initial=240, colour=(255, 0, 0))

    widget_y += 20
    green_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0, max=255, step=5, initial=0, colour=(0, 255, 0))

    widget_y += 20
    blue_slider = Slider(screen, widget_x, widget_y, 100, 10, min=0, max=255, step=5, initial=200, colour=(0, 0, 255))

    #Reset Button
    widget_y += 50
    reset_btn = Button(screen, widget_x, widget_y, 100, 30, text="Reset", onRelease=lambda: fluid.clear())

    #Geschwindigkeitsfeld einblenden/ausblenden button
    widget_y += 50
    vel_btn = Button(screen, widget_x, widget_y, 100, 30, text="Velocity", onRelease=lambda: fluid.draw())

    #Info Text zum anzeigen des Info surfaces
    info = font.render("INFO", True, "white")
    info_rect = res_title.get_rect(bottomright=(width + 50, height))

    info_text_lines = [
        "Fluid Simulation Guide",
        "",
        "Controls:",
        "- Left Mouse: Add Fluid Density",
        "- Right Mouse: Create Fluid Movement",
        "",
        "Parameters:",
        "- Timestep: Controls simulation speed",
        "- Viscosity: Fluid resistance to flow",
        "- Radius: Size of interaction area",
        "- Speed: Intensity of fluid movement",
        "- Resolution: Grid size of simulation",
        "",
        "Color Sliders:",
        "Adjust Red, Green, Blue to change",
        "fluid visualization color",
        "",
        "Buttons:",
        "- Reset: Clear simulation",
        "- Velocity: Toggle velocity vectors"
    ]
    #array mit den texten für surface erstellen
    info_text_surface = []
    for line in info_text_lines:
        info_text = font.render(line, True, "black")
        info_text_surface.append(info_text)
    #text auf info surface schreiben
    for i, info_text in enumerate(info_text_surface):
        info_surf.blit(info_text, (10, 10 + i * 25))

    #Parameter für GUI eingabe initialisieren
    left_mouse_down = False
    right_mouse_down = False
    prev_mouse_pos = None
    speed_input_value = speed_slider.getValue()
    radius_percent = radius_slider.getValue() / 1000.0
    radius = max(1, int(fluid.N * radius_percent))

    #Hauptschleife für Pygame
    while True:
        events = pygame.event.get()

        #relevante events überprüfen
        for event in events:
#
            #beim drücken auf x programm schließen
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            #drücken und loslassen der Maus, wenn im simulations surface
            #dann überprüfen ob linke oder rechte maustaste
            if event.type == pygame.MOUSEBUTTONDOWN and sim_surf_rect.collidepoint(pygame.mouse.get_pos()):
                if event.button == 1:
                    left_mouse_down = True
                elif event.button == 3:
                    right_mouse_down = True
                    prev_mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_mouse_down = False
                elif event.button == 3:
                    right_mouse_down = False
                    prev_mouse_pos = None


        #Aktion bei Drücken der linken oder rechten Maustaste
        if left_mouse_down or right_mouse_down:
            x, y = pygame.mouse.get_pos()           #derzeitige position der maus
            x = int(x / fluid.scaling_factor)       #skalieren auf größe der simulation, da das eigentliche Grid nur Nh² pixel groß ist
            y = int(y / fluid.scaling_factor)

            if left_mouse_down:
                fluid.density[x-radius:x+radius+1, y-radius:y+radius+1] = 1.0     #dichte werte an mausposition setzen
                fluid.density = gaussian_filter(fluid.density, sigma=1.0 * fluid.N/150)           #glätten

            #wenn rechtemaustaste gedrückt und die letzte mausposition nicht none ist
            if right_mouse_down and prev_mouse_pos:
                prev_x, prev_y = prev_mouse_pos
                prev_x = int(prev_x / fluid.scaling_factor)         #skalieren auf simulations grid
                prev_y = int(prev_y / fluid.scaling_factor)

                dx = x - prev_x                                     #Richtung der mausbewegung berechnen
                dy = y - prev_y
                speed_factor = np.sqrt(dx**2 + dy**2) * 0.001       #stärke der kraft mit länge der bewegung skalieren
                #kraft bezüglich radius und speed werte im kraftfelder einsetzen
                force_radius = max( 1, radius // 2 )               #kleinerer Radius für die kraft
                fluid.uforce[x-force_radius:x+force_radius+1, y-force_radius:y+force_radius+1] = dy * speed_factor * speed_input_value
                fluid.vforce[x-force_radius:x+force_radius+1, y-force_radius:y+force_radius+1] = dx * speed_factor * speed_input_value

                #glätten
                fluid.uforce = gaussian_filter(fluid.uforce, sigma=0.5)
                fluid.vforce = gaussian_filter(fluid.vforce, sigma=0.5)

                prev_mouse_pos = pygame.mouse.get_pos()

        #Simulationsschritt ausführen
        fluid.step()

        #Dichtefeld des Fluids visualisieren
        visualisation(
            sim_surf,
            fluid.density,
            red_slider.getValue(),
            green_slider.getValue(),
            blue_slider.getValue()
        )

        #simulations surface auf fenstergröße skalieren
        scaled_sim_surf = pygame.transform.scale(sim_surf, (fluid.N * fluid.scaling_factor, fluid.N * fluid.scaling_factor))

        #Geschwindigkeitsfeld zeichnen (wenn angeschaltet)
        if fluid.draw_velocity:
            n = max(1, fluid.N // 40)           #anzahl vektoren gleichbleibend
            for i in range(0, fluid.N, n):      #jeden n-ten vektoren zwischenspeichern
                for j in range(0, fluid.N, n):
                    u = fluid.v[i, j]
                    v = fluid.u[i, j]
                    #zu große vektoren skalieren
                    max_speed = 2.0
                    speed = np.hypot(u, v)
                    if speed > max_speed:
                        u *= max_speed / speed
                        v *= max_speed / speed

                    #start und endpunkt der vektoren, wobei sie um faktor 5 gestreckt werden
                    start_pos = (i * fluid.scaling_factor, j * fluid.scaling_factor)
                    end_pos = (int((i + u * 5) * fluid.scaling_factor), int((j + v * 5) * fluid.scaling_factor))

                    #surface, farbe, start, end, dicke
                    pygame.draw.line(scaled_sim_surf, (0, 239, 255), start_pos, end_pos, 1)

        #Zeichnen des Simulations und Einstellungs surface
        screen.blit(scaled_sim_surf, (0, 0))
        screen.blit(set_surf, (fluid.N * fluid.scaling_factor, 0))

        #überprüfen ob sich der slider wert geändert hat und textbox aktualisieren
        if visc_slider.getValue() != fluid.visc:
            sync_slider_change(visc_slider, visc_value)
        if timestep_slider.getValue() != fluid.dt:
            sync_slider_change(timestep_slider, timestep_value)
        if max(1, int(fluid.N * radius_slider.getValue() / 1000.0)) != radius:
            sync_slider_change(radius_slider, radius_value, True)
        if speed_slider.getValue() != speed_input_value:
            sync_slider_change(speed_slider, speed_value)
        if res_slider.getValue() != fluid.N:
            sync_slider_change(res_slider, res_value, True)


        #Fluid Simulations werte neu setzen
        fluid.visc = visc_slider.getValue()
        radius_percent = radius_slider.getValue() / 1000.0
        radius = max(1, int(fluid.N * radius_percent))
        speed_input_value = speed_slider.getValue()
        fluid.dt = timestep_slider.getValue()

        #bei ändern der Auflösung fluid mit neuem N initialisieren und Surface neu zeichnen da sich scaling_factor ändert
        if fluid.N != int(res_slider.getValue()):
            fluid = FluidSimulation(res_slider.getValue(), dt, visc)
            sim_surf = pygame.Surface((fluid.N, fluid.N))
            sim_surf_rect = pygame.Rect(0, 0, fluid.N * fluid.scaling_factor, fluid.N * fluid.scaling_factor)

        #Texte auf Einsellungs surface zeichnen
        screen.blit(timestep_title, timestep_title_rect)
        screen.blit(visc_title, visc_title_rect)
        screen.blit(radius_title, radius_title_rect)
        screen.blit(speed_title, speed_title_rect)
        screen.blit(res_title, res_title_rect)
        screen.blit(colour_title, colour_title_rect)
        screen.blit(info, info_rect)

        #Info surface zeichnen, wenn maus auf info text ist
        if info_rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(info_surf, info_surf_rect)

        #updaten von events und widgets
        pygame_widgets.update(events)
        pygame.display.update()

        #beschränken der fps
        clock.tick(60)


if __name__ == "__main__":
    main()
