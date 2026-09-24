/**
 * Contexto de sesion.
 *
 * Mantiene en memoria si hay un usuario autenticado y expone las acciones de
 * ingreso y salida. Los tokens viven en `localStorage` (ver `api/client.ts`),
 * de modo que la sesion sobrevive a una recarga de la pagina.
 */

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { guardarTokens, haySesion, limpiarTokens } from '../api/client'
import { iniciarSesion } from '../api/endpoints'

interface ValorSesion {
  autenticado: boolean
  usuario: string | null
  ingresar: (usuario: string, contrasena: string) => Promise<void>
  salir: () => void
}

const SesionContext = createContext<ValorSesion | null>(null)

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<string | null>(() => localStorage.getItem('autopartes.usuario'))
  const [autenticado, setAutenticado] = useState<boolean>(() => haySesion())

  const ingresar = useCallback(async (nombreUsuario: string, contrasena: string) => {
    const tokens = await iniciarSesion(nombreUsuario, contrasena)
    guardarTokens(tokens)
    localStorage.setItem('autopartes.usuario', nombreUsuario)
    setUsuario(nombreUsuario)
    setAutenticado(true)
  }, [])

  const salir = useCallback(() => {
    limpiarTokens()
    localStorage.removeItem('autopartes.usuario')
    setUsuario(null)
    setAutenticado(false)
  }, [])

  const valor = useMemo(
    () => ({ autenticado, usuario, ingresar, salir }),
    [autenticado, usuario, ingresar, salir],
  )

  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
}

/** Acceso al contexto de sesion; falla si se usa fuera del proveedor. */
export function usarSesion(): ValorSesion {
  const contexto = useContext(SesionContext)
  if (!contexto) {
    throw new Error('usarSesion debe llamarse dentro de ProveedorSesion.')
  }
  return contexto
}
