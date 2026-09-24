/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL base de la API Django, incluido el prefijo /api/v1. */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
