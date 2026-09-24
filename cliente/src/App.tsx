/**
 * Definicion de rutas de la app cliente.
 *
 * Catalogo e ingreso son publicos; panel, usuarios y ventas quedan detras de
 * `RutaProtegida`. La ruta comodin `*` evita pantallas en blanco ante una URL
 * desconocida.
 */

import { Link, Route, Routes } from 'react-router-dom'
import { Disposicion } from './componentes/Disposicion'
import { RutaProtegida } from './componentes/RutaProtegida'
import { Catalogo } from './paginas/Catalogo'
import { IniciarSesion } from './paginas/IniciarSesion'
import { Panel } from './paginas/Panel'
import { Usuarios } from './paginas/Usuarios'
import { Ventas } from './paginas/Ventas'

function NoEncontrada() {
  return (
    <div className="pila">
      <h1 className="titulo">Página no encontrada</h1>
      <p className="estado">
        La dirección solicitada no existe. <Link to="/">Volver al catálogo</Link>.
      </p>
    </div>
  )
}

export function App() {
  return (
    <Routes>
      <Route element={<Disposicion />}>
        <Route index element={<Catalogo />} />
        <Route path="ingresar" element={<IniciarSesion />} />
        <Route
          path="panel"
          element={
            <RutaProtegida>
              <Panel />
            </RutaProtegida>
          }
        />
        <Route
          path="panel/usuarios"
          element={
            <RutaProtegida>
              <Usuarios />
            </RutaProtegida>
          }
        />
        <Route
          path="panel/ventas"
          element={
            <RutaProtegida>
              <Ventas />
            </RutaProtegida>
          }
        />
        <Route path="*" element={<NoEncontrada />} />
      </Route>
    </Routes>
  )
}
