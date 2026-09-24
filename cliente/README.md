# App cliente de Autopartes (SPA)

Aplicacion web en React + TypeScript + Vite que consume la API REST Django del
repositorio. Es la app cliente de referencia de la auditoria: catalogo publico,
inicio de sesion con JWT y panel de gestion.

## Requisitos

- Node.js 18 o superior (el proyecto se verifico con Node 22).
- El backend Django corriendo en `http://127.0.0.1:8000`.

## Puesta en marcha

```bash
# 1. Instalar dependencias
cd cliente
npm install

# 2. Configurar la URL de la API
cp .env.example .env

# 3. Ajustar los origenes permitidos en el backend (proyecto/.env o shell)
export DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 4. Levantar el frontend
npm run dev
```

La app queda disponible en `http://127.0.0.1:5173` y consulta la API en
`VITE_API_URL`, por defecto `http://127.0.0.1:8000/api/v1`.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/api/client.ts` | Cliente HTTP: adjunta el token, renueva ante 401 y normaliza errores. |
| `src/api/endpoints.ts` | Una funcion tipada por recurso (`listarProductos`, `crearVenta`, ...). |
| `src/api/types.ts` | Tipos que reflejan los serializers de la API. |
| `src/auth/SesionContext.tsx` | Estado de sesion, ingreso y salida. |
| `src/componentes/` | Disposicion, guarda de ruta y paginacion. |
| `src/paginas/` | Catalogo, ingreso, panel, usuarios y ventas. |

## Rutas de la interfaz

| Ruta | Acceso | Descripcion |
| --- | --- | --- |
| `/` | Publico | Catalogo con busqueda por nombre o marca y paginacion. |
| `/ingresar` | Publico | Intercambio de credenciales por tokens JWT. |
| `/panel` | Sesion | Indicadores de ventas, alta rapida de productos y listado. |
| `/panel/usuarios` | Sesion de staff | Alta y listado de clientes. |
| `/panel/ventas` | Sesion de staff | Registro de ventas y historial. |

## Verificacion

```bash
npm run typecheck   # comprobacion de tipos sin emitir
npm run build       # build de produccion en dist/
```

## Uso de la sesion

Los tokens se guardan en `localStorage` bajo `autopartes.access` y
`autopartes.refresh`. El cliente renueva el token de acceso automaticamente
cuando la API responde 401, de modo que una sesion inactiva no interrumpe al
usuario. Al cerrar sesion se eliminan ambos tokens.

> Nota de seguridad: guardar tokens en `localStorage` es aceptable en esta
> version. Si el sistema se publica en internet, la recomendacion de la
> auditoria es pasar a cookies `HttpOnly` con `Secure` y `SameSite=Lax`,
> emitidas por el backend, para reducir el impacto de un XSS.

## Como habilitar una cuenta de gestion

```bash
cd ../proyecto
python manage.py createsuperuser     # crea una cuenta de staff
# Tambien sirve: python manage.py shell  y luego
# User.objects.create_user('nombre', password='...', is_staff=True)
```

Solo las cuentas con `is_staff=True` pueden administrar usuarios y ventas; el
resto recibe 403 desde la API.
