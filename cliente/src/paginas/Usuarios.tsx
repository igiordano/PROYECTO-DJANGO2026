/**
 * Gestión de usuarios finales (clientes).
 *
 * Requiere sesion de staff: la API responde 401 sin token y 403 a cuentas que
 * no son de staff, ya que estos datos incluyen correos electronicos.
 */

import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { mensajeDeError } from '../api/client'
import { crearUsuario, listarUsuarios } from '../api/endpoints'
import type { Usuario } from '../api/types'
import { Paginacion } from '../componentes/Paginacion'

const TAMANO_PAGINA = 20

export function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(1)
  const [busqueda, setBusqueda] = useState('')
  const [termino, setTermino] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [guardando, setGuardando] = useState(false)

  const [nombre, setNombre] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    const temporizador = setTimeout(() => {
      setTermino(busqueda.trim())
      setPagina(1)
    }, 400)
    return () => clearTimeout(temporizador)
  }, [busqueda])

  const cargar = useCallback(async () => {
    try {
      const respuesta = await listarUsuarios({ page: pagina, search: termino || undefined })
      setUsuarios(respuesta.results)
      setTotal(respuesta.count)
      setError(null)
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    }
  }, [pagina, termino])

  useEffect(() => {
    void cargar()
  }, [cargar])

  const alta = async (evento: FormEvent) => {
    evento.preventDefault()
    setGuardando(true)
    setAviso(null)
    setError(null)
    try {
      const creado = await crearUsuario({
        nombre_usuario: nombre.trim(),
        email_usuario: email.trim(),
      })
      setAviso(`Usuario "${creado.nombre_usuario}" creado correctamente.`)
      setNombre('')
      setEmail('')
      await cargar()
    } catch (fallo) {
      setError(mensajeDeError(fallo))
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="pila">
      <h1 className="titulo">Usuarios</h1>

      {error && <p className="alerta alerta--error">{error}</p>}
      {aviso && <p className="alerta alerta--ok">{aviso}</p>}

      <section className="bloque">
        <h2 className="bloque__titulo">Nuevo usuario</h2>
        <form className="formulario formulario--linea" onSubmit={alta}>
          <label className="campo">
            <span>Nombre</span>
            <input
              type="text"
              value={nombre}
              onChange={(evento) => setNombre(evento.target.value)}
              required
              minLength={2}
            />
          </label>
          <label className="campo">
            <span>Correo electrónico</span>
            <input
              type="email"
              value={email}
              onChange={(evento) => setEmail(evento.target.value)}
              required
            />
          </label>
          <button type="submit" className="boton boton--naranja" disabled={guardando}>
            {guardando ? 'Guardando...' : 'Agregar'}
          </button>
        </form>
      </section>

      <section className="bloque">
        <div className="bloque__cabecera">
          <h2 className="bloque__titulo">Listado</h2>
          <input
            type="search"
            className="entrada-busqueda"
            value={busqueda}
            onChange={(evento) => setBusqueda(evento.target.value)}
            placeholder="Buscar por nombre o correo"
          />
        </div>

        <div className="tabla-envoltorio">
          <table className="tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Correo</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.length === 0 ? (
                <tr>
                  <td colSpan={3} className="tabla__vacia">
                    Sin resultados.
                  </td>
                </tr>
              ) : (
                usuarios.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>{usuario.id}</td>
                    <td>{usuario.nombre_usuario}</td>
                    <td>{usuario.email_usuario}</td>
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
