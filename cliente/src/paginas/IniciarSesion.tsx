/**
 * Pantalla de inicio de sesion.
 *
 * Intercambia credenciales por un par de tokens JWT y redirige al panel. Las
 * cuentas de staff son las unicas que pueden administrar usuarios y ventas,
 * porque la API responde 403 al resto.
 */

import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { usarSesion } from '../auth/SesionContext'
import { mensajeDeError } from '../api/client'

export function IniciarSesion() {
  const { ingresar } = usarSesion()
  const navegar = useNavigate()
  const ubicacion = useLocation()
  const destino = (ubicacion.state as { destino?: string } | null)?.destino ?? '/panel'

  const [usuario, setUsuario] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      await ingresar(usuario.trim(), contrasena)
      navegar(destino, { replace: true })
    } catch (fallo) {
      setError(
        mensajeDeError(fallo) === 'La API respondio con el estado 401.'
          ? 'Usuario o contraseña incorrectos.'
          : mensajeDeError(fallo),
      )
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="acceso">
      <form className="formulario" onSubmit={enviar}>
        <h1 className="formulario__titulo">Iniciar sesión</h1>
        <p className="formulario__ayuda">
          Acceso para el equipo de gestión. El catálogo es público y no requiere cuenta.
        </p>

        <label className="campo">
          <span>Usuario</span>
          <input
            type="text"
            value={usuario}
            onChange={(evento) => setUsuario(evento.target.value)}
            autoComplete="username"
            required
          />
        </label>

        <label className="campo">
          <span>Contraseña</span>
          <input
            type="password"
            value={contrasena}
            onChange={(evento) => setContrasena(evento.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {error && <p className="alerta alerta--error">{error}</p>}

        <button type="submit" className="boton boton--naranja boton--ancho" disabled={enviando}>
          {enviando ? 'Verificando...' : 'Ingresar'}
        </button>

        <p className="formulario__pie">
          Las cuentas se crean desde <code>python manage.py createsuperuser</code> o desde
          <code> /admin/</code>.
        </p>
      </form>
    </div>
  )
}
