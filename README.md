# Plataforma de Equilibrio Controlada por Gestos

## Descripción del Proyecto

Este proyecto implementa un juego interactivo que integra **MediaPipe Hands** para la detección de manos en tiempo real y **Pymunk** como motor de física 2D. El objetivo es controlar una plataforma virtual usando gestos de la mano para capturar bolas que caen desde la parte superior de la pantalla.

### Características Principales

- **Detección de Manos en Tiempo Real**: Utiliza MediaPipe Hands para detectar 21 puntos de referencia de la mano
- **Control de Posición**: Mueve la plataforma moviendo tu mano en el espacio
- **Control de Rotación**: Inclina la plataforma rotando tu muñeca
- **Simulación Física Realista**: Implementa gravedad, colisiones, fricción y elasticidad
- **Mecánica de Juego**: Captura bolas en la zona designada para sumar puntos
- **Interfaz Intuitiva**: Visualización en tiempo real con OpenCV

## Requisitos del Sistema

- **Python**: 3.8 o superior
- **Cámara Web**: Necesaria para la captura de video
- **Sistema Operativo**: Windows, macOS o Linux

## Instalación

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Si tienes git
git clone <url-del-repositorio>
cd DuranGarzon_BoadaSalazar

# O simplemente extrae el archivo ZIP
unzip DuranGarzon_BoadaSalazar.zip
cd DuranGarzon_BoadaSalazar
```

### Paso 2: Crear un Entorno Virtual (Recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- **mediapipe**: Librería de Google para detección de manos
- **pymunk**: Motor de física 2D
- **opencv-python**: Procesamiento de video
- **numpy**: Operaciones numéricas

## Cómo Ejecutar

```bash
python main.py
```

### Controles del Juego

| Tecla | Acción |
|-------|--------|
| `L` | Mostrar/Ocultar puntos de referencia de la mano |
| `P` | Pausar/Reanudar el juego |
| `R` | Reiniciar el juego |
| `Q` | Salir del juego |

### Mecánica de Juego

1. **Posicionamiento**: Mueve tu mano para mover la plataforma en el eje X-Y
2. **Rotación**: Rota tu muñeca para inclinar la plataforma
3. **Captura**: Guía las bolas hacia la zona azul de captura en la parte superior
4. **Puntuación**: Cada bola capturada suma 1 punto

## Explicación Técnica: Cálculo de Orientación

### Fundamento Matemático

La orientación (ángulo) de la mano se calcula utilizando dos puntos de referencia clave de MediaPipe:

- **Punto 0 (WRIST)**: La muñeca
- **Punto 9 (MIDDLE_FINGER_MCP)**: La articulación MCP del dedo medio

### Fórmula

```
Vector = (x₉ - x₀, y₉ - y₀)
Ángulo = arctan2(Vector_y, Vector_x)
```

Donde:
- `arctan2` es la función arctangente de dos argumentos
- Retorna un ángulo en radianes en el rango [-π, π]
- El ángulo 0 corresponde a la mano apuntando hacia la derecha
- Ángulos positivos indican rotación contraclockwise

### Implementación en Código

```python
def _calculate_hand_angle(self, landmarks: np.ndarray) -> float:
    """
    Calcula el ángulo de rotación de la mano.
    """
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    
    # Vector desde muñeca hasta dedo medio
    vector = middle_mcp[:2] - wrist[:2]
    
    # Calcular ángulo usando arctan2
    angle = np.arctan2(vector[1], vector[0])
    
    return angle
```

### Ventajas de Este Enfoque

1. **Robustez**: Utiliza dos puntos distantes para mayor estabilidad
2. **Invariancia**: No depende de la escala o posición absoluta
3. **Precisión**: Proporciona un rango completo de rotación (-180° a 180°)
4. **Eficiencia**: Cálculo simple y rápido

## Estructura del Proyecto

```
DuranGarzon_BoadaSalazar/
├── main.py                 # Programa principal y bucle del juego
├── hand_tracker.py         # Clase para detección de manos
├── physics_world.py        # Clase para simulación de física
├── utils.py                # Funciones auxiliares
├── requirements.txt        # Dependencias del proyecto
├── integrantes.txt         # Nombres de los integrantes
└── README.md               # Este archivo
```

### Descripción de Módulos

#### `main.py`
- Clase `GestureBalanceGame`: Integra todo el sistema
- Bucle principal de captura y renderizado
- Gestión de entrada de usuario

#### `hand_tracker.py`
- Clase `HandTracker`: Inicializa y gestiona MediaPipe
- Detección de landmarks
- Cálculo de posición y orientación

#### `physics_world.py`
- Clase `PhysicsWorld`: Gestiona el espacio de Pymunk
- Creación de objetos dinámicos y estáticos
- Simulación de colisiones y gravedad

#### `utils.py`
- Funciones de conversión de coordenadas
- Funciones de suavizado y normalización
- Operaciones matemáticas auxiliares

## Criterios de Evaluación Cumplidos

### 1. Interacción (7 puntos)
✅ Control de posición: La mano controla la posición X-Y de la plataforma
✅ Control de orientación: La rotación de la mano inclina la plataforma

### 2. Física (2 puntos)
✅ Gravedad: Las bolas caen debido a la gravedad
✅ Colisiones: Las bolas rebotan en la plataforma y paredes
✅ Fricción: Implementada en todas las superficies

### 3. Complejidad (2 puntos)
✅ Mecánica de captura: Sistema de puntuación con zona de captura
✅ Generación dinámica: Las bolas se generan continuamente
✅ Interfaz visual: Visualización en tiempo real de landmarks y objetos

## Solución de Problemas

### La cámara no se abre
- Verifica que tu cámara web esté conectada y funcione
- En Linux, puede ser necesario ejecutar con permisos de sudo
- Intenta: `sudo python main.py`

### MediaPipe no detecta la mano
- Asegúrate de que haya buena iluminación
- Coloca tu mano claramente visible frente a la cámara
- Intenta acercarte más a la cámara

### El juego va lento
- Reduce la resolución de la cámara en `main.py`
- Cierra otras aplicaciones que usen mucha CPU
- Verifica que tu GPU esté siendo utilizada

### Error de importación
- Verifica que todas las dependencias estén instaladas: `pip list`
- Reinstala las dependencias: `pip install -r requirements.txt --force-reinstall`

## Referencias

- [MediaPipe Hands Documentation](https://google.github.io/mediapipe/solutions/hands)
- [Pymunk Physics Engine](https://www.pymunk.org/)
- [OpenCV Documentation](https://docs.opencv.org/)

## Notas de Desarrollo

### Mejoras Futuras

1. Agregar diferentes niveles de dificultad
2. Implementar efectos de sonido
3. Agregar más tipos de objetos con diferentes propiedades
4. Crear un sistema de puntuación más complejo
5. Agregar multijugador local

### Optimizaciones Posibles

1. Usar GPU para procesamiento de MediaPipe
2. Implementar caché de modelos
3. Reducir la frecuencia de detección de manos
4. Usar threading para operaciones de I/O

## Licencia

Este proyecto es desarrollado como parte del curso "Sistemas de Interacción Persona-Computador" de la Universidad de La Laguna.

## Autores

- **Juan David Durán Garzón**
- **Ángel Andrés Boada Salazar**

Profesor: Rafael Arnay del Arco
Universidad: Universidad de La Laguna
Año: 2025-2026
