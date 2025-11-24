import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Specials from './pages/Specials';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

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
      <Footer />
    </Router>
  );
}

export default App;