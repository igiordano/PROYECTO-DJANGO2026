/**
 * Tipos compartidos que reflejan exactamente lo que devuelve la API v1.
 *
 * Mantenerlos alineados con `Autopartes/serializers.py` evita errores en
 * tiempo de compilacion cuando el backend cambia.
 */

/** Forma de toda respuesta paginada de Django REST Framework. */
export interface Paginado<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface Producto {
  id: number
  nombre_producto: string
  marca_producto: string
}

export interface Usuario {
  id: number
  nombre_usuario: string
  email_usuario: string
}

/**
 * `monto` llega como numero en los detalles y como cadena en los reportes
 * agregados, porque Django serializa `Decimal` como texto. El tipo lo refleja y
 * `formatearMonto` normaliza la presentacion.
 */
export interface Venta {
  id: number
  monto: number | string
  fecha_venta: string
  forma_de_pago: string
  producto: number
  usuario: number
  producto_nombre: string
  producto_marca: string
  usuario_nombre: string
  usuario_email: string
}

/** Datos que envia el formulario de venta (solo las claves foraneas). */
export interface VentaEntrada {
  monto: string
  fecha_venta: string
  forma_de_pago: string
  producto: number
  usuario: number
}

export interface ResumenVentas {
  total_ventas: number
  monto_total: string
  monto_promedio: string
  por_forma_de_pago: { forma_de_pago: string; cantidad: number; monto: number | string }[]
  por_marca: { marca: string; cantidad: number; monto: number | string }[]
}

export interface ParDeTokens {
  access: string
  refresh: string
}

/** Errores de validacion que devuelve DRF, campo por campo. */
export type ErroresApi = Record<string, string[] | string>
