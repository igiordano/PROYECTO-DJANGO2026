/**
 * Panel del equipo de gestion.
 *
 * Muestra el reporte agregado de ventas (`GET /reportes/ventas/`) y una vista
 * rapida del catalogo con alta de productos, que es la operacion mas frecuente.
 */

import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { mensajeDeError, formatearMonto } from '../api/client'
import { crearProducto, listarProductos, resumenVentas } from '../api/endpoints'
import type { Producto, ResumenVentas } from '../api/types'

export function Panel() {
  const [resumen, setResumen] = useState<ResumenVentas | null>(null)
  const [productos, setProductos] = useState<Producto[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [nombre, setNombre] = useState('')
  const [marca, setMarca] = useState('')
  const [aviso, setAviso] = useState<string | null>(null)
  const [guardando, setGuardando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const [datosResumen, lista] = await Promise.all([
        resumenVentas(),
        listarProductos({ ordering: '-id' }),
      ])
      setResumen(datosResumen)
      setProductos(lista.results)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const altaProducto = async (evento: FormEvent) => {
    evento.preventDefault()
    setGuardando(true)
    setAviso(null)
    setError(null)
    try {
      const creado = await crearProducto({
        nombre_producto: nombre.trim(),
        marca_producto: marca.trim(),
      })
      setAviso(`Producto "${creado.nombre_producto}" creado correctamente.`)
      setNombre('')
      setMarca('')
      await cargar()
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setGuardando(false)
    }
  }

  if (cargando) return <p className="estado">Cargando panel...</p>

  return (
    <div className="pila">
      <h1 className="titulo">Panel de gestión</h1>

      {error && <p className="alerta alerta--error">{error}</p>}
      {aviso && <p className="alerta alerta--ok">{aviso}</p>}

      {resumen && (
        <section className="indicadores">
          <article className="indicador">
            <span className="indicador__etiqueta">Ventas registradas</span>
            <strong className="indicador__valor">{resumen.total_ventas}</strong>
          </article>
          <article className="indicador">
            <span className="indicador__etiqueta">Facturación total</span>
            <strong className="indicador__valor">{formatearMonto(resumen.monto_total)}</strong>
          </article>
          <article className="indicador">
            <span className="indicador__etiqueta">Ticket promedio</span>
            <strong className="indicador__valor">{formatearMonto(resumen.monto_promedio)}</strong>
          </article>
        </section>
      )}

      {resumen && resumen.por_marca.length > 0 && (
        <section className="bloque">
          <h2 className="bloque__titulo">Ventas por marca</h2>
          <ul className="lista-simple">
            {resumen.por_marca.map((fila) => (
              <li key={fila.marca}>
                <span>{fila.marca}</span>
                <span>
                  {fila.cantidad} venta{fila.cantidad === 1 ? '' : 's'} —{' '}
                  {formatearMonto(fila.monto)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="bloque">
        <h2 className="bloque__titulo">Alta rápida de producto</h2>
        <form className="formulario formulario--linea" onSubmit={altaProducto}>
          <label className="campo">
            <span>Nombre del producto</span>
            <input
              type="text"
              value={nombre}
              onChange={(evento) => setNombre(evento.target.value)}
              placeholder="Ej. Filtro de aceite"
              required
              minLength={2}
            />
          </label>
          <label className="campo">
            <span>Marca</span>
            <input
              type="text"
              value={marca}
              onChange={(evento) => setMarca(evento.target.value)}
              placeholder="Ej. Bosch"
              required
              minLength={2}
            />
          </label>
          <button type="submit" className="boton boton--naranja" disabled={guardando}>
            {guardando ? 'Guardando...' : 'Agregar'}
          </button>
        </form>
      </section>

      <section className="bloque">
        <h2 className="bloque__titulo">Últimos productos cargados</h2>
        <div className="tabla-envoltorio">
          <table className="tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Producto</th>
                <th>Marca</th>
              </tr>
            </thead>
            <tbody>
              {productos.map((producto) => (
                <tr key={producto.id}>
                  <td>{producto.id}</td>
                  <td>{producto.nombre_producto}</td>
                  <td>{producto.marca_producto}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
