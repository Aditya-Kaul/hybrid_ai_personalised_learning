import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ParticleBackground from './components/ParticleBackground';
import HomePage from './views/HomePage';
import LessonPage from './views/LessonPage';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <ParticleBackground />
        <div className="content-wrapper" style={{ position: 'relative', zIndex: 1 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/lesson" element={<LessonPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;