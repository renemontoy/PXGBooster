import { useNavigate, Outlet } from 'react-router-dom';
import Footer from './footer';

const Layout = () => {
  const navigate = useNavigate();


  return (
    <div style={{ 
      display: 'flex',
      flexDirection: 'column',
      minHeight: '98vh',
      margin: 0,
      padding: 0,
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      {/* Header */}
      <header 
        style={{
          padding: '1rem',
          background: '#000',
          cursor: 'pointer',
          textAlign: 'center'
        }}
        onClick={() => navigate('/pxgboost')}
      >
        <h1 style={{ 
          margin: 0, 
          color: '#fff',
          fontSize: '2.5rem',
          letterSpacing: '2px',
          textTransform: 'uppercase'
        }}>
          PXG BOOST
        </h1>
      </header>

      {/* Main (flex-grow: 1 para ocupar todo el espacio disponible) */}
      <main style={{ flex: 1, paddingBottom: '2rem' }}>
        <Outlet />
      </main>

      {/* Footer fijo abajo */}
      <Footer />
    </div>
  );
};

export default Layout;