/**
 * Catalogo publico de autopartes.
 *
 * Consume `GET /productos/`, que no requiere autenticacion. La busqueda usa el
 * parametro `search` de la API con retardo (debounce) para no saturar el
 * servidor con una peticion por tecla.
 */

import { useEffect, useMemo, useState } from 'react'
import { listarProductos } from '../api/endpoints'
import { mensajeDeError } from '../api/client'
import type { Producto } from '../api/types'
import { Paginacion } from '../componentes/Paginacion'

const TAMANO_PAGINA = 20

export function Catalogo() {
  const [productos, setProductos] = useState<Producto[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(1)
  const [busqueda, setBusqueda] = useState('')
  const [terminoAplicado, setTerminoAplicado] = useState('')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Retardo de 400 ms: solo se consulta la API cuando el usuario deja de escribir.
  useEffect(() => {
    const temporizador = setTimeout(() => {
      setTerminoAplicado(busqueda.trim())
      setPagina(1)
    }, 400)
    return () => clearTimeout(temporizador)
  }, [busqueda])

  useEffect(() => {
    let vigente = true
    setCargando(true)
    setError(null)

    listarProductos({ page: pagina, search: terminoAplicado || undefined })
      .then((respuesta) => {
        if (!vigente) return
        setProductos(respuesta.results)
        setTotal(respuesta.count)
      })
      .catch((fallo) => {
        if (!vigente) return
        setError(mensajeDeError(fallo))
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })

    return () => {
      vigente = false
    }
  }, [pagina, terminoAplicado])

  const marcas = useMemo(
    () => Array.from(new Set(productos.map((producto) => producto.marca_producto))).sort(),
    [productos],
  )

  return (
    <div className="pila">
      <section className="portada">
        <p className="portada__etiqueta">Catálogo general</p>
        <h1 className="portada__titulo">Repuestos con garantía de compatibilidad</h1>
        <p className="portada__texto">
          Busca por nombre o marca. El catálogo se consulta en línea contra la API, de modo que
          cualquier cambio cargado desde el panel aparece de inmediato.
        </p>
        <label className="buscador">
          <span className="buscador__etiqueta">Buscar repuesto</span>
          <input
            type="search"
            value={busqueda}
            onChange={(evento) => setBusqueda(evento.target.value)}
            placeholder="Ej. filtro de aceite, Bosch, frenos..."
          />
        </label>
      </section>

      {error && <p className="alerta alerta--error">{error}</p>}

      {cargando ? (
        <p className="estado">Cargando catálogo...</p>
      ) : productos.length === 0 ? (
        <p className="estado">
          No se encontraron productos{terminoAplicado ? ` para "${terminoAplicado}"` : ''}.
        </p>
      ) : (
        <>
          <p className="resumen-listado">
            {total} producto{total === 1 ? '' : 's'}
            {terminoAplicado ? ` para "${terminoAplicado}"` : ''} — {marcas.length} marca
            {marcas.length === 1 ? '' : 's'} en esta página
          </p>

          <div className="grilla">
            {productos.map((producto) => (
              <article className="tarjeta" key={producto.id}>
                <span className="tarjeta__marca">{producto.marca_producto}</span>
                <h2 className="tarjeta__titulo">{producto.nombre_producto}</h2>
                <p className="tarjeta__meta">Código interno #{producto.id}</p>
              </article>
            ))}
          </div>

          <Paginacion
            pagina={pagina}
            total={total}
            tamano={TAMANO_PAGINA}
            onCambiar={setPagina}
          />
        </>
      )}
    </div>
  )
}
