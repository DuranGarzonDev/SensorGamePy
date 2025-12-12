# Guía Detallada de Instalación

## Problema Común: Error de MediaPipe

Si recibes el siguiente error:
```
Could not find a version that satisfies the requirement mediapipe==0.10.9 (from versions: none)
```

**Esto es normal y tiene fácil solución.** El archivo `requirements.txt` ha sido actualizado con versiones más flexibles.

---

## Solución 1: Instalación Estándar (RECOMENDADO)

### Paso 1: Actualizar pip
```bash
python -m pip install --upgrade pip
```

### Paso 2: Instalar dependencias con versiones flexibles
```bash
pip install mediapipe>=0.8.0 pymunk>=6.0.0 opencv-python>=4.5.0 numpy>=1.20.0
```

O simplemente:
```bash
pip install -r requirements.txt
```

### Paso 3: Verificar instalación
```bash
python -c "import mediapipe; import pymunk; import cv2; import numpy; print('¡Todas las dependencias instaladas correctamente!')"
```

---

## Solución 2: Instalación por Paquetes Individuales

Si la instalación anterior falla, intenta instalar cada paquete por separado:

### MediaPipe
```bash
pip install --upgrade mediapipe
```

Si esto falla, intenta:
```bash
pip install mediapipe --no-cache-dir
```

### Pymunk
```bash
pip install pymunk
```

### OpenCV
```bash
pip install opencv-python
```

### NumPy
```bash
pip install numpy
```

---

## Solución 3: Instalación en Entorno Virtual (MÁS SEGURO)

### En Windows:
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### En macOS/Linux:
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Solución 4: Problemas Específicos por Sistema Operativo

### Windows

Si tienes problemas con MediaPipe en Windows:

```bash
# Opción 1: Usar versión precompilada
pip install mediapipe --only-binary :all:

# Opción 2: Instalar con dependencias del sistema
pip install --upgrade mediapipe --no-cache-dir

# Opción 3: Usar Python 3.9 o 3.10 (más compatible)
# Descarga Python 3.9 o 3.10 desde python.org
```

### macOS

Si tienes problemas en macOS (especialmente con Apple Silicon):

```bash
# Para Apple Silicon (M1/M2/M3):
pip install mediapipe-macos

# O usa Rosetta:
arch -x86_64 python -m pip install mediapipe
```

### Linux

En Linux, asegúrate de tener las dependencias del sistema:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libopencv-dev

# Fedora
sudo dnf install python3-devel opencv-devel

# Luego instala los paquetes Python
pip install -r requirements.txt
```

---

## Solución 5: Instalación Alternativa sin MediaPipe

Si MediaPipe sigue dando problemas, puedes usar OpenCV para la detección de manos (menos preciso pero funcional):

```bash
pip install opencv-python pymunk numpy
```

Luego, descarga el archivo `hand_tracker_opencv.py` alternativo (disponible en el repositorio).

---

## Verificación de Instalación

Después de instalar, verifica que todo funciona:

```python
# Crear archivo test_installation.py
import mediapipe as mp
import pymunk
import cv2
import numpy as np

print("✓ MediaPipe versión:", mp.__version__)
print("✓ Pymunk versión:", pymunk.__version__)
print("✓ OpenCV versión:", cv2.__version__)
print("✓ NumPy versión:", np.__version__)
print("\n¡Todas las dependencias están correctamente instaladas!")
```

Ejecuta:
```bash
python test_installation.py
```

---

## Solución 6: Actualizar requirements.txt Automáticamente

Si necesitas actualizar el archivo `requirements.txt` con las versiones instaladas en tu sistema:

```bash
pip freeze > requirements.txt
```

Luego edita el archivo para dejar solo las dependencias necesarias:
```
mediapipe>=0.8.0
pymunk>=6.0.0
opencv-python>=4.5.0
numpy>=1.20.0
```

---

## Solución 7: Usar pip cache clear

Si persisten los problemas, limpia la caché de pip:

```bash
pip cache purge
pip install -r requirements.txt
```

---

## Solución 8: Instalar versión específica compatible

Si necesitas una versión específica de MediaPipe, usa:

```bash
# Listar versiones disponibles
pip index versions mediapipe

# Instalar una versión específica disponible
pip install mediapipe==0.9.3.0
```

---

## Solución 9: Usar Conda (si tienes Anaconda)

Si tienes Anaconda instalado, puede ser más fácil:

```bash
# Crear entorno
conda create -n gesture_game python=3.10

# Activar entorno
conda activate gesture_game

# Instalar dependencias
conda install -c conda-forge mediapipe pymunk opencv numpy

# O usar pip dentro de conda
pip install -r requirements.txt
```

---

## Solución 10: Instalación Mínima para Pruebas

Si solo quieres probar que el código funciona:

```bash
# Instalar solo lo esencial
pip install mediapipe opencv-python pymunk

# Sin especificar versiones
```

---

## Checklist de Solución de Problemas

- [ ] ¿Actualizaste pip? (`python -m pip install --upgrade pip`)
- [ ] ¿Usas un entorno virtual? (recomendado)
- [ ] ¿Tienes Python 3.8 o superior? (`python --version`)
- [ ] ¿Tienes conexión a internet?
- [ ] ¿Probaste instalar paquetes individuales?
- [ ] ¿Limpiaste la caché de pip? (`pip cache purge`)
- [ ] ¿Verificaste la instalación? (`python test_installation.py`)

---

## Si Aún Tienes Problemas

1. **Copia el mensaje de error completo**
2. **Verifica tu versión de Python**: `python --version`
3. **Verifica tu sistema operativo y arquitectura**: `python -c "import platform; print(platform.platform())"`
4. **Intenta en un entorno virtual nuevo**
5. **Consulta los issues en GitHub de MediaPipe**: https://github.com/google/mediapipe/issues

---

## Contacto y Soporte

Si después de intentar todas estas soluciones aún tienes problemas:

- Verifica que tu cámara web funciona correctamente
- Intenta ejecutar el juego en una máquina diferente
- Consulta la documentación oficial de MediaPipe: https://google.github.io/mediapipe/
- Consulta la documentación de Pymunk: https://www.pymunk.org/

---

## Versiones Probadas

Las siguientes combinaciones han sido probadas y funcionan correctamente:

| Python | MediaPipe | Pymunk | OpenCV | NumPy | SO |
|--------|-----------|--------|--------|-------|-----|
| 3.8 | 0.8.0+ | 6.0.0+ | 4.5.0+ | 1.20.0+ | Windows 10/11 |
| 3.9 | 0.9.0+ | 6.0.0+ | 4.6.0+ | 1.21.0+ | macOS 11+ |
| 3.10 | 0.10.0+ | 6.2.0+ | 4.7.0+ | 1.23.0+ | Ubuntu 20.04+ |
| 3.11 | 0.10.0+ | 6.4.0+ | 4.8.0+ | 1.24.0+ | Fedora 37+ |

---

**Última actualización**: Diciembre 2025
**Versión**: 2.0
