/**
 * Funciones tipadas por recurso.
 *
 * Cada pantalla llama a estas funciones en lugar de armar URLs a mano, de modo
 * que un cambio de ruta en el backend se corrige en un solo lugar.
 */

import { peticion } from './client'
import type {
  Paginado,
  ParDeTokens,
  Producto,
  ResumenVentas,
  Usuario,
  Venta,
  VentaEntrada,
} from './types'

/** Convierte un objeto de filtros en cadena de consulta, omitiendo vacios. */
export function aQueryString(parametros: Record<string, string | number | undefined>): string {
  const partes = Object.entries(parametros)
    .filter(([, valor]) => valor !== undefined && valor !== '' && valor !== null)
    .map(([clave, valor]) => `${encodeURIComponent(clave)}=${encodeURIComponent(String(valor))}`)
  return partes.length > 0 ? `?${partes.join('&')}` : ''
}

// --- Autenticacion ---------------------------------------------------------

export async function iniciarSesion(usuario: string, contrasena: string): Promise<ParDeTokens> {
  return peticion<ParDeTokens>(
    '/auth/token/',
    {
      method: 'POST',
      body: JSON.stringify({ username: usuario, password: contrasena }),
    },
    { publica: true },
  )
}

// --- Catalogo de productos -------------------------------------------------

export async function listarProductos(filtros: {
  page?: number
  search?: string
  marca?: string
  ordering?: string
} = {}): Promise<Paginado<Producto>> {
  return peticion<Paginado<Producto>>(`/productos/${aQueryString(filtros)}`, {}, { publica: true })
}

export async function crearProducto(datos: {
  nombre_producto: string
  marca_producto: string
}): Promise<Producto> {
  return peticion<Producto>('/productos/', { method: 'POST', body: JSON.stringify(datos) })
}

export async function actualizarProducto(
  id: number,
  datos: { nombre_producto: string; marca_producto: string },
): Promise<Producto> {
  return peticion<Producto>(`/productos/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(datos),
  })
}

export async function eliminarProducto(id: number): Promise<void> {
  return peticion<void>(`/productos/${id}/`, { method: 'DELETE' })
}

// --- Usuarios finales ------------------------------------------------------

export async function listarUsuarios(filtros: { page?: number; search?: string } = {}): Promise<
  Paginado<Usuario>
> {
  return peticion<Paginado<Usuario>>(`/usuarios/${aQueryString(filtros)}`)
}

export async function crearUsuario(datos: {
  nombre_usuario: string
  email_usuario: string
}): Promise<Usuario> {
  return peticion<Usuario>('/usuarios/', { method: 'POST', body: JSON.stringify(datos) })
}

// --- Ventas ----------------------------------------------------------------

export async function listarVentas(filtros: {
  page?: number
  search?: string
  forma_de_pago?: string
  desde?: string
  hasta?: string
} = {}): Promise<Paginado<Venta>> {
  return peticion<Paginado<Venta>>(`/ventas/${aQueryString(filtros)}`)
}

export async function crearVenta(datos: VentaEntrada): Promise<Venta> {
  return peticion<Venta>('/ventas/', { method: 'POST', body: JSON.stringify(datos) })
}

export async function eliminarVenta(id: number): Promise<void> {
  return peticion<void>(`/ventas/${id}/`, { method: 'DELETE' })
}

// --- Reportes --------------------------------------------------------------

export async function resumenVentas(): Promise<ResumenVentas> {
  return peticion<ResumenVentas>('/reportes/ventas/')
}
