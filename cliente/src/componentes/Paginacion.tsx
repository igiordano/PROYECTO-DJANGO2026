/**
 * Controles de paginacion para listados.
 *
 * La API pagina de a 20 elementos, de modo que este componente evita que la app
 * descargue tablas completas y muestra el avance del usuario.
 */

interface Props {
  pagina: number
  total: number
  tamano: number
  onCambiar: (pagina: number) => void
}

export function Paginacion({ pagina, total, tamano, onCambiar }: Props) {
  const totalPaginas = Math.max(1, Math.ceil(total / tamano))
  if (totalPaginas <= 1) return null

  return (
    <div className="paginacion">
      <button
        type="button"
        className="boton boton--contorno"
        onClick={() => onCambiar(pagina - 1)}
        disabled={pagina <= 1}
      >
        Anterior
      </button>
      <span className="paginacion__estado">
        Página {pagina} de {totalPaginas} — {total} registros
      </span>
      <button
        type="button"
        className="boton boton--contorno"
        onClick={() => onCambiar(pagina + 1)}
        disabled={pagina >= totalPaginas}
      >
        Siguiente
      </button>
    </div>
  )
}
