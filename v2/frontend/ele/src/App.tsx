import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import HomePage from './views/HomePage'
import LessonPage from './views/LessonPage'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/lesson" element={<LessonPage />} />
      </Routes>
    </Router>
  )
}