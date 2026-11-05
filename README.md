# Sistema de Gestión de Membresías de Gimnasio

## Descripción

Sistema backend para la gestión de miembros de un gimnasio.  
Permite crear, listar, editar y eliminar miembros, filtrar por estado, plan o DNI, y calcular automáticamente la fecha de vencimiento según el plan contratado (mensual, trimestral o anual).

Tecnologías utilizadas:
- **Backend:** FastAPI
- **ORM / Modelos:** SQLModel
- **Base de datos:** SQLite
- **Templates:** Jinja2

## Requisitos previos

- Python 3.11 o superior
- pip (o uv)
- Base de datos SQLite (se crea automáticamente)

## Instalación

### 1. Clonar el repositorio

```
git clone https://github.com/Planda1/proto-ins.git
cd proto-ins
```
### 2. Crear entorno virtual
```
python -m venv .venv
```
### 3. Activar entorno virtual
#### Linux/macOS
```
source .venv/bin/activate
```

#### Windows
```
.venv\Scripts\activate
```
### 4. Instalar dependencias
Con **PIP**:
```
pip install -r requirements.txt
```
Con **UV**:
```
uv sync
```
### 5. Cargar datos de prueba (Opcional)
```
python seed.py
```
### 6. Levantar el servidor
```
uvicorn main:app --reload
```
- Interfaz web: http://127.0.0.1:8000
- Documentacion de la API: http://127.0.0.1:8000/docs

## Tabla de rutas (Endpoints)
### Rutas de la API

| URL                  | Metodo | Descripcion                                                                   |
|----------------------|--------|-------------------------------------------------------------------------------|
| /members/            | POST   | Crea un miembro nuevo y calcula la fecha de vencimiento segun el plan elegido |
| /members/            | GET    | Lista todos los miembros, permite filtrar por estado, plan o DNI              |
| /members/{member_id} | GET    | Obtiene los datos de un miembro especifico                                    |
| /members/{member_id} | PUT    | Actualiza los datos de un miembro existente                                   |
| /members/{member_id} | DELETE | Elimina un miembro de la base de datos                                        |

### Rutas de la Web
| URL                         | Metodo | Descripcion                                                                   |
|-----------------------------|--------|-------------------------------------------------------------------------------|
| /                           | GET    | Muestra el dashboard con estadisticas                                         |
| /members                    | GET    | Muestra el listado de miembros, tambien puede filtrar por estado, plan o DNI  |
| /members/{member_id}/view   | GET    | Muestra los detalles de un miembro                                            |
| /members_new                | GET    | Muestra el formulario para crear un nuevo miembro                             |
| /members_new                | POST   | Procesa el formulario y guarda el nuevo miembro                               |
| /members/{member_id}/edit   | GET    | Muestra el formulario para editar un miembro                                  |
| /members/{member_id}/edit   | POST   | Procesa el formulario y actualiza el miembro                                  |
| /members/{member_id}/delete | POST   | Elimina un miembro y redirige al listado                                      |