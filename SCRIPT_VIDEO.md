# Script de Presentación en Video
## Plataforma de Equilibrio Controlada por Gestos

**Duración Total Estimada**: 8-10 minutos
**Equipo**: Juan David Durán Garzón & Ángel Andrés Boada Salazar
**Profesor**: Rafael Arnay del Arco
**Curso**: Sistemas de Interacción Persona-Computador

---

## PARTE 1: INTRODUCCIÓN Y DEMOSTRACIÓN (Juan David)
**Duración**: 2-3 minutos

### Escena 1: Presentación del Proyecto (0:00 - 0:30)

**JUAN**: 
"Hola, soy Juan David Durán Garzón. Junto con mi compañero Ángel Andrés Boada Salazar, presentamos nuestro proyecto final para el curso de Sistemas de Interacción Persona-Computador.

Hemos desarrollado una 'Plataforma de Equilibrio Controlada por Gestos', un juego interactivo que demuestra cómo la detección de manos en tiempo real puede usarse para controlar objetos en un mundo de física 2D.

Este proyecto integra dos tecnologías principales: MediaPipe Hands de Google para la detección de manos, y Pymunk como motor de física."

### Escena 2: Visión General del Juego (0:30 - 1:00)

**JUAN**:
"El objetivo del juego es simple pero desafiante: debes capturar bolas que caen desde la parte superior de la pantalla usando una plataforma que controlas con tu mano.

Tienes dos formas de controlar la plataforma:
1. Moviendo tu mano en el espacio para cambiar la posición X-Y de la plataforma
2. Rotando tu muñeca para inclinar la plataforma

Cada bola que captures en la zona azul de captura suma un punto."

### Escena 3: Demostración en Vivo (1:00 - 2:30)

**JUAN**:
"Permíteme mostrar cómo funciona en la práctica."

[DEMOSTRACIÓN EN VIVO]

**JUAN** (mientras juega):
"Como ves, cuando levanto mi mano, la plataforma se mueve hacia arriba. Cuando la muevo a la derecha, la plataforma se desplaza en esa dirección.

Ahora voy a inclinar mi mano para rotar la plataforma. Observa cómo el ángulo de la plataforma cambia en tiempo real con la rotación de mi muñeca.

Aquí viene una bola... voy a intentar capturarla en la zona azul. ¡Lo logré! El contador de bolas capturadas aumentó a 1.

Como puedes ver, la física es muy realista: las bolas rebotan, se deslizan con fricción, y la gravedad las atrae constantemente hacia abajo."

---

## PARTE 2: EXPLICACIÓN TÉCNICA - MEDIAPIPE (Ángel Andrés)
**Duración**: 2-3 minutos

### Escena 4: Introducción a MediaPipe (2:30 - 3:00)

**ÁNGEL**:
"Ahora voy a explicar cómo funciona la detección de manos. El proyecto utiliza MediaPipe Hands, una librería desarrollada por Google que puede detectar 21 puntos de referencia en la mano con alta precisión.

Estos 21 puntos representan las articulaciones principales de la mano: la muñeca, las articulaciones de cada dedo, y las puntas de los dedos."

[MOSTRAR IMAGEN O DIAGRAMA DE LOS 21 PUNTOS]

### Escena 5: Explicación del Código - hand_tracker.py (3:00 - 4:00)

**ÁNGEL**:
"Veamos el código responsable de la detección. Este es el módulo `hand_tracker.py`.

[MOSTRAR CÓDIGO EN PANTALLA]

```python
class HandTracker:
    def __init__(self, max_num_hands: int = 1, min_detection_confidence: float = 0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
```

La clase `HandTracker` inicializa MediaPipe con los parámetros necesarios. El parámetro `min_detection_confidence` establece el umbral de confianza para detectar una mano.

El método `detect_hand` procesa cada fotograma de la cámara y retorna los 21 puntos de referencia si se detecta una mano."

**ÁNGEL**:
"Lo más importante para nuestro proyecto es que podemos extraer dos piezas de información clave de estos puntos:

1. **Posición**: Usamos la posición de la muñeca (punto 0) como referencia
2. **Orientación**: Calculamos el ángulo de la mano usando la muñeca y el dedo medio"

### Escena 6: Cálculo de la Orientación (4:00 - 4:30)

**ÁNGEL**:
"El cálculo de la orientación es particularmente interesante. Usamos dos puntos: la muñeca (punto 0) y la articulación MCP del dedo medio (punto 9).

[MOSTRAR DIAGRAMA O CÓDIGO]

```python
def _calculate_hand_angle(self, landmarks: np.ndarray) -> float:
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    
    # Vector desde muñeca hasta dedo medio
    vector = middle_mcp[:2] - wrist[:2]
    
    # Calcular ángulo usando arctan2
    angle = np.arctan2(vector[1], vector[0])
    
    return angle
```

Creamos un vector desde la muñeca hasta el dedo medio. Luego usamos la función `arctan2` para calcular el ángulo de este vector. El resultado es un ángulo en radianes entre -π y π, que representa la orientación de la mano."

---

## PARTE 3: EXPLICACIÓN TÉCNICA - PYMUNK (Ángel Andrés)
**Duración**: 2-3 minutos

### Escena 7: Introducción a Pymunk (4:30 - 5:00)

**ÁNGEL**:
"Ahora pasemos a la parte de física. Usamos Pymunk, un motor de física 2D escrito en Python que permite simular comportamientos físicos realistas.

Pymunk maneja:
- Gravedad
- Colisiones entre objetos
- Fricción
- Elasticidad (rebotes)
- Rotación de objetos"

### Escena 8: Estructura del Mundo de Física (5:00 - 6:00)

**ÁNGEL**:
"El módulo `physics_world.py` define la clase `PhysicsWorld` que gestiona todo el mundo de física.

[MOSTRAR CÓDIGO]

```python
class PhysicsWorld:
    def __init__(self, width: int = 800, height: int = 600, gravity: float = -9.81):
        self.space = pymunk.Space()
        self.space.gravity = (0, gravity)
        
        self._create_walls()
        self._create_platform()
```

Creamos un espacio de Pymunk con una gravedad de -9.81 m/s², que es aproximadamente la gravedad de la Tierra. Luego creamos las paredes estáticas que forman los límites del mundo.

La plataforma es un objeto dinámico que puede moverse y rotar. Su posición y ángulo se actualizan en tiempo real basándose en la posición y orientación de la mano detectada."

### Escena 9: Generación de Objetos (6:00 - 6:30)

**ÁNGEL**:
"Las bolas se generan automáticamente en la parte superior del mundo a intervalos regulares.

```python
def spawn_ball(self) -> Optional[Tuple[pymunk.Body, pymunk.Circle]]:
    x = random.uniform(50, self.width - 50)
    y = self.height - 30
    
    radius = 10
    mass = 1.0
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.8
    shape.friction = 0.5
    
    self.space.add(body, shape)
```

Cada bola tiene una masa, un radio, elasticidad (para los rebotes) y fricción. Todas estas propiedades afectan cómo interactúan con el entorno."

### Escena 10: Detección de Capturas (6:30 - 7:00)

**ÁNGEL**:
"El sistema también detecta cuándo una bola entra en la zona de captura.

```python
def _check_caught_balls(self):
    bucket_x_min = self.width * 0.35
    bucket_x_max = self.width * 0.65
    bucket_y_max = 50
    
    for body, shape in self.balls:
        x, y = body.position
        if bucket_x_min <= x <= bucket_x_max and y <= bucket_y_max:
            # Remover bola y sumar punto
            self.balls_caught += 1
```

Cuando una bola entra en el rectángulo definido como zona de captura, se remueve del mundo y se suma un punto al contador."

---

## PARTE 4: INTEGRACIÓN Y DEMOSTRACIÓN FINAL (Juan David & Ángel)
**Duración**: 1-2 minutos

### Escena 11: Módulo Principal (7:00 - 7:30)

**JUAN**:
"El módulo principal `main.py` integra todo: la detección de manos y el mundo de física.

[MOSTRAR CÓDIGO]

```python
class GestureBalanceGame:
    def run(self):
        cap = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = cap.read()
            
            # Detectar mano
            landmarks, angle, position = self.hand_tracker.detect_hand(frame)
            
            # Actualizar plataforma
            self.physics_world.update_platform(position, angle)
            
            # Actualizar física
            self.physics_world.update()
            
            # Renderizar escena
            frame = self._render_scene(frame)
            cv2.imshow("Juego", frame)
```

El bucle principal:
1. Captura un fotograma de la cámara
2. Detecta la mano usando MediaPipe
3. Actualiza la posición y rotación de la plataforma
4. Simula la física
5. Renderiza todo en pantalla"

### Escena 12: Demostración Final y Conclusiones (7:30 - 8:00)

**ÁNGEL**:
"Permíteme hacer una última demostración para mostrar cómo todo funciona junto."

[DEMOSTRACIÓN EN VIVO]

**JUAN**:
"Este proyecto demuestra cómo la tecnología de detección de manos puede usarse de forma creativa para crear experiencias interactivas.

Hemos cumplido con todos los requisitos de la rúbrica:
- Control de posición Y orientación de un objeto dinámico (7 puntos)
- Implementación de física realista con gravedad, colisiones y fricción (2 puntos)
- Funcionalidad creativa más allá del movimiento simple: sistema de captura de puntos (2 puntos)"

**ÁNGEL**:
"El código está bien estructurado en módulos independientes, es fácil de mantener y extensible para futuras mejoras.

Gracias por su atención. ¿Alguna pregunta?"

---

## NOTAS PARA LA GRABACIÓN

### Recomendaciones Técnicas

1. **Iluminación**: Asegúrate de tener buena iluminación para que MediaPipe detecte bien la mano
2. **Fondo**: Un fondo limpio y sin distracciones mejora la calidad de la detección
3. **Cámara**: Usa una cámara de buena calidad si es posible
4. **Micrófono**: Usa un micrófono externo para mejor calidad de audio
5. **Edición**: Edita el video para eliminar silencios y hacer transiciones suaves

### Distribución de Roles

| Sección | Responsable | Duración |
|---------|-------------|----------|
| Introducción | Juan | 0:30 |
| Visión General | Juan | 0:30 |
| Demostración 1 | Juan | 1:30 |
| MediaPipe Intro | Ángel | 0:30 |
| hand_tracker.py | Ángel | 1:00 |
| Cálculo Orientación | Ángel | 0:30 |
| Pymunk Intro | Ángel | 0:30 |
| physics_world.py | Ángel | 1:00 |
| Generación Objetos | Ángel | 0:30 |
| Detección Capturas | Ángel | 0:30 |
| main.py | Juan | 0:30 |
| Demostración Final | Juan & Ángel | 0:30 |

### Puntos Clave a Enfatizar

1. **Integración**: Cómo MediaPipe y Pymunk trabajan juntos
2. **Tiempo Real**: La detección y actualización ocurren en cada fotograma
3. **Matemáticas**: El cálculo del ángulo usando arctan2
4. **Física Realista**: Gravedad, colisiones, fricción
5. **Interfaz Intuitiva**: El usuario no necesita conocimientos técnicos para jugar

### Posibles Preguntas y Respuestas

**P: ¿Por qué usaste arctan2 en lugar de atan?**
R: arctan2 maneja correctamente los cuatro cuadrantes y retorna el ángulo en el rango [-π, π], lo que es más útil para rotaciones.

**P: ¿Cómo manejas la latencia entre la detección y la actualización?**
R: Usamos suavizado de valores para reducir el jitter. Cada valor se interpola gradualmente hacia el objetivo.

**P: ¿Cuál es la frecuencia de fotogramas?**
R: El juego intenta correr a 30-60 FPS dependiendo del hardware disponible.

**P: ¿Cómo se comportan las bolas si la plataforma se mueve rápido?**
R: Pymunk maneja correctamente las colisiones incluso con objetos que se mueven rápido, aunque puede haber pequeñas imprecisiones a velocidades muy altas.

---

## CRONOGRAMA DE GRABACIÓN

1. **Día 1**: Grabar escenas 1-3 (Introducción y demostración)
2. **Día 2**: Grabar escenas 4-6 (MediaPipe)
3. **Día 3**: Grabar escenas 7-10 (Pymunk)
4. **Día 4**: Grabar escenas 11-12 (Integración y conclusión)
5. **Día 5**: Edición y post-producción

---

**Versión Final**: 1.0
**Fecha**: Diciembre 2025
**Duración Total**: 8-10 minutos
