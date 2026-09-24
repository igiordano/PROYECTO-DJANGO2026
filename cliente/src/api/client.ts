/**
 * Cliente HTTP de la API.
 *
 * Responsabilidades:
 * - Resolver la URL base desde `VITE_API_URL`.
 * - Adjuntar el token de acceso en cada peticion autenticada.
 * - Renovar el token de acceso de forma transparente cuando el servidor
 *   responde 401, sin interrumpir al usuario.
 * - Traducir los errores de Django REST Framework a un tipo util para las
 *   pantallas (`ErroresApi`) y a un mensaje legible.
 */

import type { ErroresApi, ParDeTokens } from './types'

const URL_BASE: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://127.0.0.1:8000/api/v1'

const CLAVE_ACCESO = 'autopartes.access'
const CLAVE_REFRESCO = 'autopartes.refresh'

export class ErrorApi extends Error {
  estado: number
  detalle: ErroresApi | null

  constructor(mensaje: string, estado: number, detalle: ErroresApi | null = null) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.estado = estado
    this.detalle = detalle
  }
}

/** Guarda el par de tokens en el almacenamiento local del navegador. */
export function guardarTokens(par: ParDeTokens): void {
  localStorage.setItem(CLAVE_ACCESO, par.access)
  localStorage.setItem(CLAVE_REFRESCO, par.refresh)
}

export function limpiarTokens(): void {
  localStorage.removeItem(CLAVE_ACCESO)
  localStorage.removeItem(CLAVE_REFRESCO)
}

export function tokenDeAcceso(): string | null {
  return localStorage.getItem(CLAVE_ACCESO)
}

export function haySesion(): boolean {
  return Boolean(tokenDeAcceso())
}

/** Convierte la respuesta de error de DRF en un texto para mostrar. */
export function mensajeDeError(error: unknown): string {
  if (error instanceof ErrorApi) {
    if (error.detalle) {
      const partes = Object.entries(error.detalle).map(([campo, valor]) => {
        const texto = Array.isArray(valor) ? valor.join(' ') : String(valor)
        return campo === 'detail' || campo === 'non_field_errors' ? texto : `${campo}: ${texto}`
      })
      if (partes.length > 0) return partes.join(' | ')
    }
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'Ocurrio un error inesperado.'
}

interface OpcionesPeticion {
  /** `true` para peticiones que no deben llevar token (catalogo publico). */
  publica?: boolean
}

async function interpretarRespuesta<T>(respuesta: Response): Promise<T> {
  if (respuesta.status === 204) {
    return undefined as T
  }
  const texto = await respuesta.text()
  const cuerpo = texto ? JSON.parse(texto) : null

  if (!respuesta.ok) {
    const detalle = (cuerpo as ErroresApi) ?? null
    const mensaje =
      detalle && typeof detalle.detail === 'string'
        ? detalle.detail
        : `La API respondio con el estado ${respuesta.status}.`
    throw new ErrorApi(mensaje, respuesta.status, detalle)
  }
  return cuerpo as T
}

/** Intenta renovar el token de acceso con el token de refresco guardado. */
async function renovarToken(): Promise<boolean> {
  const refresco = localStorage.getItem(CLAVE_REFRESCO)
  if (!refresco) return false

  const respuesta = await fetch(`${URL_BASE}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refresco }),
  })

  if (!respuesta.ok) {
    limpiarTokens()
    return false
  }

  const datos = (await respuesta.json()) as Partial<ParDeTokens>
  if (!datos.access) {
    limpiarTokens()
    return false
  }
  // Con ROTATE_REFRESH_TOKENS activo el servidor tambien devuelve un refresco nuevo.
  guardarTokens({ access: datos.access, refresh: datos.refresh ?? refresco })
  return true
}

/**
 * Ejecuta una peticion a la API.
 *
 * Si el servidor responde 401 y hay token de refresco valido, se renueva el
 * acceso y se repite la peticion una sola vez.
 */
export async function peticion<T>(
  ruta: string,
  init: RequestInit = {},
  opciones: OpcionesPeticion = {},
): Promise<T> {
  const construirCabeceras = (): HeadersInit => {
    const cabeceras: Record<string, string> = {
      Accept: 'application/json',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
    }
    if (!opciones.publica) {
      const token = tokenDeAcceso()
      if (token) cabeceras.Authorization = `Bearer ${token}`
    }
    return { ...cabeceras, ...(init.headers as Record<string, string> | undefined) }
  }

  let respuesta = await fetch(`${URL_BASE}${ruta}`, { ...init, headers: construirCabeceras() })

  if (respuesta.status === 401 && !opciones.publica) {
    const renovado = await renovarToken()
    if (renovado) {
      respuesta = await fetch(`${URL_BASE}${ruta}`, { ...init, headers: construirCabeceras() })
    }
  }

  return interpretarRespuesta<T>(respuesta)
}

/** Formatea un monto con separador de miles y dos decimales. */
export function formatearMonto(valor: number | string): string {
  const numero = typeof valor === 'string' ? Number(valor) : valor
  if (Number.isNaN(numero)) return String(valor)
  return numero.toLocaleString('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
  })
}

export { URL_BASE }
