/**
 * Estructura comun de la app: barra de navegacion, contenido y pie.
 *
 * El enlace de acceso al panel solo aparece cuando hay sesion activa; si no,
 * se muestra el boton de inicio de sesion.
 */

import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { usarSesion } from '../auth/SesionContext'

export function Disposicion() {
  const { autenticado, usuario, salir } = usarSesion()
  const navegar = useNavigate()

  const cerrarSesion = () => {
    salir()
    navegar('/')
  }

  return (
    <>
      <header className="barra">
        <div className="barra__interior">
          <Link to="/" className="marca">
            <span className="marca__punto" aria-hidden="true" />
            AutoPartes
          </Link>

          <nav className="navegacion" aria-label="Navegación principal">
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'activo' : '')}>
              Catálogo
            </NavLink>
            {autenticado && (
              <>
                <NavLink to="/panel" className={({ isActive }) => (isActive ? 'activo' : '')}>
                  Panel
                </NavLink>
                <NavLink to="/panel/usuarios" className={({ isActive }) => (isActive ? 'activo' : '')}>
                  Usuarios
                </NavLink>
                <NavLink to="/panel/ventas" className={({ isActive }) => (isActive ? 'activo' : '')}>
                  Ventas
                </NavLink>
              </>
            )}
          </nav>

          <div className="barra__acciones">
            {autenticado ? (
              <>
                <span className="usuario">{usuario}</span>
                <button type="button" className="boton boton--fantasma" onClick={cerrarSesion}>
                  Salir
                </button>
              </>
            ) : (
              <Link to="/ingresar" className="boton boton--naranja">
                Iniciar sesión
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="contenido">
        <Outlet />
      </main>

      <footer className="pie">
        <div className="pie__interior">
          <p>
            <strong>AutoPartes</strong> — catálogo de repuestos y panel de gestión.
          </p>
          <p className="pie__nota">
            Los datos se consultan desde la API REST de Django en <code>/api/v1/</code>. La
            documentación interactiva está disponible en <code>/api/docs/</code>.
          </p>
        </div>
      </footer>
    </>
  )
}
