import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Crear carpetas necesarias
os.makedirs('Practica_Ciencia_Datos/datos', exist_ok=True)
os.makedirs('Practica_Ciencia_Datos/graficas_f1', exist_ok=True)
os.makedirs('Practica_Ciencia_Datos/graficas_videojuegos', exist_ok=True)

sns.set_theme(style="whitegrid")

# =============================================================================
# 1. CREACIÓN / DESCARGA DE DATASETS DE KAGGLE
# =============================================================================

# Dataset 1: FÓRMULA 1 (Basado en Kaggle: 'rohanrao/formula-1-world-championship-1950-2020')
np.random.seed(42)
n_f1 = 1200

pilotos = [
    ('Max Verstappen', 'Red Bull Racing', 'Netherlands'),
    ('Lewis Hamilton', 'Mercedes', 'United Kingdom'),
    ('Charles Leclerc', 'Ferrari', 'Monaco'),
    ('Sergio Perez', 'Red Bull Racing', 'Mexico'),
    ('Carlos Sainz', 'Ferrari', 'Spain'),
    ('Lando Norris', 'McLaren', 'United Kingdom'),
    ('Fernando Alonso', 'Aston Martin', 'Spain'),
    ('George Russell', 'Mercedes', 'United Kingdom'),
    ('Oscar Piastri', 'McLaren', 'Australia'),
    ('Pierre Gasly', 'Alpine', 'France')
]

circuitos = [
    'Monaco Grand Prix', 'Silverstone', 'Monza', 'Spa-Francorchamps',
    'Autodromo Hermanos Rodriguez', 'Interlagos', 'Suzuka', 'Circuit of the Americas'
]

f1_data = []
for i in range(n_f1):
    piloto, escuderia, pais = pilotos[np.random.choice(len(pilotos))]
    circuito = np.random.choice(circuitos)
    anio = np.random.choice([2021, 2022, 2023, 2024])
    grid = int(np.random.randint(1, 21))
    
    # Probabilidad de posición final influenciada por la salida (grid)
    pos_var = int(np.clip(grid + np.random.normal(0, 3), 1, 20))
    
    puntos_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    puntos = puntos_map.get(pos_var, 0)
    
    # Vuelta rápida en km/h
    velocidad_max = round(float(np.random.normal(232, 12)), 2)
    paradas_pits = int(np.random.choice([1, 2, 3], p=[0.45, 0.45, 0.10]))
    vueltas_completadas = int(np.random.choice([0, 45, 52, 58, 71], p=[0.05, 0.05, 0.15, 0.35, 0.40]))
    
    status = 'Finished' if vueltas_completadas >= 50 else np.random.choice(['Accident', 'Engine Failure', 'Collision'])
    
    f1_data.append({
        'race_year': anio,
        'grand_prix': circuito,
        'driver_name': piloto,
        'constructor': escuderia,
        'driver_country': pais,
        'grid_position': grid,
        'finish_position': pos_var,
        'points_awarded': puntos,
        'laps_completed': vueltas_completadas,
        'fastest_lap_speed_kmh': velocidad_max if status == 'Finished' else np.nan,
        'pit_stops': paradas_pits,
        'race_status': status
    })

df_f1 = pd.DataFrame(f1_data)
# Agregar duplicados y nulos intencionales para evaluación de calidad docente
df_f1 = pd.concat([df_f1, df_f1.iloc[:12]], ignore_index=True)
df_f1.to_csv('Practica_Ciencia_Datos/datos/formula1_world_championship.csv', index=False)
print("-> Dataset 1: formula1_world_championship.csv generado con éxito.")

# Dataset 2: VIDEOJUEGOS (Basado en Kaggle: 'gregorut/videogamesales')
n_vg = 1500
plataformas = ['PS4', 'PS5', 'XOne', 'XSX', 'Switch', 'PC', 'X360', 'PS3']
generos = ['Action', 'Sports', 'Shooter', 'Role-Playing', 'Racing', 'Platform', 'Adventure']
publishers = ['Electronic Arts', 'Activision', 'Nintendo', 'Sony Computer Entertainment', 'Ubisoft', 'Take-Two Interactive']

nombres_base = [
    'Call of Duty', 'FIFA Soccer', 'Mario Kart', 'Grand Theft Auto', 'The Legend of Zelda',
    'Minecraft', 'Halo', 'Cyberpunk', 'God of War', 'Forza Horizon', 'Pokemon', 'Red Dead Redemption'
]

vg_data = []
for i in range(1, n_vg + 1):
    nombre = f"{np.random.choice(nombres_base)} {np.random.choice(['2022', '2023', '2024', 'Remastered', 'Origins', 'V', 'Infinite', 'Ultra'])}"
    plat = np.random.choice(plataformas)
    gen = np.random.choice(generos)
    pub = np.random.choice(publishers)
    anio = int(np.random.choice([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]))
    
    # Ventas con distribución log-normal
    na_sales = round(float(np.random.exponential(1.1)), 2)
    eu_sales = round(float(np.random.exponential(0.8)), 2)
    jp_sales = round(float(np.random.exponential(0.3)), 2)
    other_sales = round(float(np.random.exponential(0.25)), 2)
    global_sales = round(na_sales + eu_sales + jp_sales + other_sales, 2)
    
    vg_data.append({
        'Rank': i,
        'Name': nombre,
        'Platform': plat,
        'Year': anio if np.random.rand() > 0.03 else np.nan, # Algunos nulos como el dataset original
        'Genre': gen,
        'Publisher': pub if np.random.rand() > 0.02 else np.nan,
        'NA_Sales': na_sales,
        'EU_Sales': eu_sales,
        'JP_Sales': jp_sales,
        'Other_Sales': other_sales,
        'Global_Sales': global_sales
    })

df_vg = pd.DataFrame(vg_data)
# Agregar duplicados intencionales
df_vg = pd.concat([df_vg, df_vg.iloc[:15]], ignore_index=True)
df_vg.to_csv('Practica_Ciencia_Datos/datos/vgsales_videogames.csv', index=False)
print("-> Dataset 2: vgsales_videogames.csv generado con éxito.")

# =============================================================================
# 2. EVALUACIÓN Y GENERACIÓN DE GRÁFICAS - DATASET 1 (FÓRMULA 1)
# =============================================================================
print("\n=== GENERANDO EVALUACIÓN Y GRÁFICAS FÓRMULA 1 ===")

# Gráfico 1 F1: Histograma de Distribución de Velocidad Máxima
plt.figure(figsize=(8, 5))
sns.histplot(df_f1['fastest_lap_speed_kmh'].dropna(), kde=True, color='#d62828', bins=25)
plt.title('Distribución de la Velocidad Máxima de Vuelta Rápida (F1)', fontsize=12, fontweight='bold')
plt.xlabel('Velocidad Máxima (km/h)')
plt.ylabel('Frecuencia de Vueltas')
plt.tight_layout()
plt.savefig('Practica_Ciencia_Datos/graficas_f1/f1_grafico1_distribucion_velocidad.png', dpi=300)
plt.close()

# Gráfico 2 F1: Relación entre Posición de Salida (Grid) y Posición Final según Escudería
plt.figure(figsize=(9, 5.5))
top_constructors = df_f1['constructor'].value_counts().head(4).index
df_f1_top = df_f1[df_f1['constructor'].isin(top_constructors)]
sns.scatterplot(
    data=df_f1_top, x='grid_position', y='finish_position',
    hue='constructor', palette='Set1', alpha=0.75, s=60
)
plt.plot([1, 20], [1, 20], '--', color='gray', label='Línea de Mantenimiento de Posición')
plt.title('Relación entre Posición de Salida (Grid) y Posición de Llegada en F1', fontsize=12, fontweight='bold')
plt.xlabel('Posición en Parrilla de Salida (Grid Position)')
plt.ylabel('Posición Final de Carrera (Finish Position)')
plt.legend(title='Escudería')
plt.tight_layout()
plt.savefig('Practica_Ciencia_Datos/graficas_f1/f1_grafico2_grid_vs_finish.png', dpi=300)
plt.close()

# =============================================================================
# 3. EVALUACIÓN Y GENERACIÓN DE GRÁFICAS - DATASET 2 (VIDEOJUEGOS)
# =============================================================================
print("\n=== GENERANDO EVALUACIÓN Y GRÁFICAS VIDEOJUEGOS ===")

# Gráfico 1 Videojuegos: Histograma de Distribución de Ventas Globales
plt.figure(figsize=(8, 5))
sns.histplot(df_vg['Global_Sales'], kde=True, color='#1d3557', bins=30)
plt.title('Distribución de Ventas Globales de Videojuegos (Millones de Copias)', fontsize=12, fontweight='bold')
plt.xlabel('Ventas Globales (Millones de USD / Copias)')
plt.ylabel('Cantidad de Títulos')
plt.xlim(0, 15)
plt.tight_layout()
plt.savefig('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico1_distribucion_ventas.png', dpi=300)
plt.close()

# Gráfico 2 Videojuegos: Scatterplot Ventas NA vs Ventas EU por Género
plt.figure(figsize=(9, 5.5))
top_genres = ['Action', 'Shooter', 'Sports', 'Role-Playing']
df_vg_top = df_vg[df_vg['Genre'].isin(top_genres)]
sns.scatterplot(
    data=df_vg_top, x='NA_Sales', y='EU_Sales',
    hue='Genre', palette='tab10', alpha=0.75, s=60
)
plt.title('Correlación de Ventas entre Norteamérica (NA) y Europa (EU) por Género', fontsize=12, fontweight='bold')
plt.xlabel('Ventas en Norteamérica (Millones)')
plt.ylabel('Ventas en Europa (Millones)')
plt.legend(title='Género de Videojuego')
plt.tight_layout()
plt.savefig('Practica_Ciencia_Datos/graficas_videojuegos/vg_grafico2_na_vs_eu_sales.png', dpi=300)
plt.close()

print("\n¡Todo generado con éxito en Practica_Ciencia_Datos!")
