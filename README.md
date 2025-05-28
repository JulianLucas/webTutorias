# Plataforma de Tutorías

Conecta estudiantes con tutores en tiempo real.

## Características principales
- Registro e inicio de sesión de usuarios (estudiantes y tutores)
- Creación y edición de perfil de tutor
- Búsqueda de tutores por materia y disponibilidad
- Solicitud y agendamiento de tutorías
- Confirmación de tutoría por parte del tutor
- Videollamada integrada (Jitsi)
- Calificación y reseña del tutor

---

## ¿Cómo ejecutar este proyecto?

### 1. Clona el repositorio
```sh
git clone https://github.com/JulianLucas/webTutorias.git
cd webTutorias
```

### 2. Instala las dependencias
Asegúrate de tener Python 3.8+ instalado y en el PATH.
```sh
pip install -r requirements.txt
```

### 3. Inicializa la base de datos
```sh
python init_db.py
```

### 4. Ejecuta la aplicación
```sh
python run.py
```

Abre tu navegador en [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## Notas
- Para videollamadas, se utiliza un enlace directo a Jitsi Meet (no requiere configuración extra).
- **Toda la plataforma ahora funciona 100% sobre Firebase Firestore.**
    - Usuarios: registro, login y autenticación desde Firestore.
    - Perfiles de tutor: creación, edición, búsqueda y consulta desde Firestore.
    - Tutorías (Booking): creación, confirmación y consulta desde Firestore.
    - Reseñas: guardado, consulta y promedio de calificaciones desde Firestore.
    - Ya no se usa SQLAlchemy ni ninguna base de datos relacional.
    - El backend sigue usando Flask, pero toda la persistencia es en Firestore.

- No uses este servidor en producción sin antes configurar un entorno seguro y WSGI.
- Si tienes dudas o errores, abre un issue o contacta al responsable del repositorio.

