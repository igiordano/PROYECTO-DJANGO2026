/**
 * Punto de entrada de la app cliente.
 *
 * Monta el arbol de React con el proveedor de sesion y el enrutador. Los
 * estilos se importan como hoja unica para mantener el CSS en un solo archivo.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App } from './App'
import { ProveedorSesion } from './auth/SesionContext'
import './estilos/global.css'

const contenedor = document.getElementById('root')
if (!contenedor) {
  throw new Error('No se encontro el elemento #root en index.html.')
}

createRoot(contenedor).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
