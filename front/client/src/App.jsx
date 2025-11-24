import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Specials from './pages/Specials';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="content-wrapper">
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/specials" element={<Specials />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
