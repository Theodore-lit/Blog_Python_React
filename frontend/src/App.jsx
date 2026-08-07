import React, { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import PrivateRoute from './routes/PrivateRoute.jsx'
import PublicRoute from './routes/PublicRoute.jsx'

// Lazy-loaded pages — chargées uniquement quand la route est visitée
const Home       = lazy(() => import('./pages/Home.jsx'))
const Login      = lazy(() => import('./pages/Login.jsx'))
const Register   = lazy(() => import('./pages/Register.jsx'))
const PostDetail = lazy(() => import('./pages/PostDetail.jsx'))
const PostForm   = lazy(() => import('./pages/PostForm.jsx'))
const Favorites  = lazy(() => import('./pages/Favorites.jsx'))

const App = () => (
  <Suspense fallback={<p style={{ padding: '2rem' }}>Chargement…</p>}>
    <Routes>
      {/* Routes publiques */}
      <Route path="/"            element={<Home />} />
      <Route path="/posts/:id"   element={<PostDetail />} />

      {/* Routes accessibles uniquement non-connecté */}
      <Route element={<PublicRoute />}>
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Routes protégées */}
      <Route element={<PrivateRoute />}>
        <Route path="/posts/new"      element={<PostForm />} />
        <Route path="/posts/:id/edit" element={<PostForm />} />
        <Route path="/favorites"      element={<Favorites />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </Suspense>
)

export default App
