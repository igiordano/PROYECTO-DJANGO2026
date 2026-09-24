/**
 * Registro y listado de ventas.
 *
 * Los selectores de producto y usuario se alimentan de la API. El formulario
 * envia solo las claves foraneas y el backend devuelve los nombres resueltos en
 * los campos de solo lectura, de modo que la tabla no necesita consultas extra.
 */

import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { formatearMonto, mensajeDeError } from '../api/client'
import { crearVenta, eliminarVenta, listarProductos, listarUsuarios, listarVentas } from '../api/endpoints'
import type { Producto, Usuario, Venta } from '../api/types'
import { Paginacion } from '../componentes/Paginacion'

const TAMANO_PAGINA = 20

function hoy(): string {
  return new Date().toISOString().slice(0, 10)
}

export function Ventas() {
  const [ventas, setVentas] = useState<Venta[]>([])
  const [productos, setProductos] = useState<Producto[]>([])
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(1)

  const [monto, setMonto] = useState('')
  const [fecha, setFecha] = useState(hoy())
  const [formaPago, setFormaPago] = useState('Efectivo')
  const [productoId, setProductoId] = useState('')
  const [usuarioId, setUsuarioId] = useState('')

  const [error, setError] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [guardando, setGuardando] = useState(false)

  const cargarVentas = useCallback(async () => {
    try {
      const respuesta = await listarVentas({ page: pagina })
      setVentas(respuesta.results)
      setTotal(respuesta.count)
      setError(null)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    }
  }, [pagina])

  useEffect(() => {
    void cargarVentas()
  }, [cargarVentas])

  useEffect(() => {
    // Catalogos auxiliares para los selectores del formulario.
    Promise.all([listarProductos(), listarUsuarios()])
      .then(([listaProductos, listaUsuarios]) => {
        setProductos(listaProductos.results)
        setUsuarios(listaUsuarios.results)
      })
      .catch((fallo) => setError(mensajeDeError(fallo)))
  }, [])

  const registrar = async (evento: FormEvent) => {
    evento.preventDefault()
    setGuardando(true)
    setAviso(null)
    setError(null)
    try {
      const creada = await crearVenta({
        monto,
        fecha_venta: fecha,
        forma_de_pago: formaPago.trim(),
        producto: Number(productoId),
        usuario: Number(usuarioId),
      })
      setAviso(`Venta #${creada.id} registrada por ${formatearMonto(creada.monto)}.`)
      setMonto('')
      await cargarVentas()
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setGuardando(false)
    }
  }

  const borrar = async (id: number) => {
    if (!window.confirm(`¿Eliminar la venta #${id}? Esta acción no se puede deshacer.`)) return
    try {
      await eliminarVenta(id)
      setAviso(`Venta #${id} eliminada.`)
      await cargarVentas()
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    }
  }

  return (
    <div className="pila">
      <h1 className="titulo">Ventas</h1>

      {error && <p className="alerta alerta--error">{error}</p>}
      {aviso && <p className="alerta alerta--ok">{aviso}</p>}

      <section className="bloque">
        <h2 className="bloque__titulo">Registrar venta</h2>
        <form className="formulario formulario--grilla" onSubmit={registrar}>
          <label className="campo">
            <span>Monto</span>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={monto}
              onChange={(evento) => setMonto(evento.target.value)}
              required
            />
          </label>
          <label className="campo">
            <span>Fecha de venta</span>
            <input
              type="date"
              max={hoy()}
              value={fecha}
              onChange={(evento) => setFecha(evento.target.value)}
              required
            />
          </label>
          <label className="campo">
            <span>Forma de pago</span>
            <input
              type="text"
              value={formaPago}
              onChange={(evento) => setFormaPago(evento.target.value)}
              placeholder="Efectivo, Tarjeta, Transferencia"
              required
              minLength={3}
            />
          </label>
          <label className="campo">
            <span>Producto</span>
            <select value={productoId} onChange={(evento) => setProductoId(evento.target.value)} required>
              <option value="">Seleccione un producto</option>
              {productos.map((producto) => (
                <option key={producto.id} value={producto.id}>
                  {producto.nombre_producto} — {producto.marca_producto}
                </option>
              ))}
            </select>
          </label>
          <label className="campo">
            <span>Cliente</span>
            <select value={usuarioId} onChange={(evento) => setUsuarioId(evento.target.value)} required>
              <option value="">Seleccione un cliente</option>
              {usuarios.map((usuario) => (
                <option key={usuario.id} value={usuario.id}>
                  {usuario.nombre_usuario} — {usuario.email_usuario}
                </option>
              ))}
            </select>
          </label>
          <div className="campo campo--accion">
            <button type="submit" className="boton boton--naranja boton--ancho" disabled={guardando}>
              {guardando ? 'Guardando...' : 'Registrar venta'}
            </button>
          </div>
        </form>
      </section>

      <section className="bloque">
        <h2 className="bloque__titulo">Historial</h2>
        <div className="tabla-envoltorio">
          <table className="tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Producto</th>
                <th>Cliente</th>
                <th>Forma de pago</th>
                <th className="tabla__numero">Monto</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {ventas.length === 0 ? (
                <tr>
                  <td colSpan={7} className="tabla__vacia">
                    Todavía no hay ventas registradas.
                  </td>
                </tr>
              ) : (
                ventas.map((venta) => (
                  <tr key={venta.id}>
                    <td>{venta.id}</td>
                    <td>{venta.fecha_venta}</td>
                    <td>
                      {venta.producto_nombre} <span className="tenue">({venta.producto_marca})</span>
                    </td>
                    <td>
                      {venta.usuario_nombre} <span className="tenue">({venta.usuario_email})</span>
                    </td>
                    <td>{venta.forma_de_pago}</td>
                    <td className="tabla__numero">{formatearMonto(venta.monto)}</td>
                    <td>
                      <button
                        type="button"
                        className="boton boton--peligro"
                        onClick={() => void borrar(venta.id)}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Paginacion
          pagina={pagina}
          total={total}
          tamano={TAMANO_PAGINA}
          onCambiar={setPagina}
        />
      </section>
    </div>
  )
}
