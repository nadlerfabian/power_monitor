# Neuimport der benötigten Bibliotheken nach Reset
import numpy as np
import matplotlib.pyplot as plt

# Parameter für die 230V 50Hz Sinuswelle
frequency = 50  # 50 Hz
voltage = 230  # Peak voltage (RMS * sqrt(2) for 230V RMS)
time = np.linspace(0, 0.04, 1000)  # 0.04 seconds (one cycle at 50Hz)

# Sinuswelle berechnen
sin_wave = voltage * np.sin(2 * np.pi * frequency * time)

# Berechnung der Stromkurve für eine rein resistive Last
resistance = 23  # Ohm (entspricht etwa 10A bei 230V RMS)
current = sin_wave / resistance  # Ohm'sches Gesetz: I = U / R

# Diagramm erstellen
plt.figure(figsize=(10, 6))
plt.plot(time * 1000, sin_wave, label="Spannung [V]")  # Spannung
plt.plot(time * 1000, current, label="Strom [A]", linestyle='--', color="red")  # Strom
plt.title("230V 50Hz Sinuswelle mit Stromverlauf (Resistive Last)", fontsize=14)
plt.xlabel("Zeit (ms)", fontsize=12)
plt.ylabel("Amplitude", fontsize=12)
plt.grid(True)
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
plt.legend()
plt.show()
