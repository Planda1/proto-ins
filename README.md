# Proto-Ins — Sistema de Gestión de Membresías de Gimnasio

## Descripción

Sistema backend para la gestión de miembros de un gimnasio.  
Permite crear, listar, editar y eliminar miembros, filtrar por estado, plan o DNI, y calcular automáticamente la fecha de vencimiento según el plan contratado (mensual, trimestral o anual).

Tecnologías utilizadas:
- **Backend:** FastAPI
- **ORM / Modelos:** SQLModel
- **Base de datos:** SQLite
- **Templates:** Jinja2

## Requisitos previos

- Python 3.10 o superior
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