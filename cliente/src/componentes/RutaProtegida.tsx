/**
 * Guarda de ruta: exige sesion activa para las pantallas de gestion.
 *
 * Si no hay sesion, redirige a `/ingresar` conservando el destino original para
 * volver alli despues del login. La verificacion real siempre ocurre igual en
 * el servidor (la API responde 401/403), de modo que este guard solo mejora la
 * experiencia y no sustituye al control de acceso.
 */

import { Navigate, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'
import { usarSesion } from '../auth/SesionContext'

export function RutaProtegida({ children }: { children: ReactNode }) {
  const { autenticado } = usarSesion()
  const ubicacion = useLocation()

  if (!autenticado) {
    return <Navigate to="/ingresar" replace state={{ destino: ubicacion.pathname }} />
  }
  return <>{children}</>
}
