import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';

const Card = ({ title, imageUrl, route }) => {
  const navigate = useNavigate();

  return (
    <StyledWrapper>
      <div
        className="card"
        onClick={() => navigate(route)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && navigate(route)}
      >
        <div
          className="card-image"
          style={{ backgroundImage: `url("${imageUrl}")` }}
        />
        <h3 className="card-title">{title}</h3>
      </div>
    </StyledWrapper>
  );
};

Card.propTypes = {
  title: PropTypes.string.isRequired,
  imageUrl: PropTypes.string.isRequired,
  route: PropTypes.string.isRequired,
};

const StyledWrapper = styled.div`
  .card {
    width: clamp(350px, 25vw, 340px); /* Mínimo:250px, Ideal:25% del ancho de ventana, Máximo:300px */
    height: clamp(450px, 35vw, 440px);
    /* Resto de tus estilos... */
  }
    border-radius: 5px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
    margin: 0 15px; /* Espacio entre tarjetas */

    &:hover {
      transform: scale(1.013);
      box-shadow: 0 15px 30px rgba(0,0,0,0.4);
    }
  }

  .card-image {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
  }

  .card-title {
    position: absolute;
    bottom: 40px;
    left: 0;
    right: 0;
    color: white;
    text-align: center;
    font-size: 1.5rem;
    font-weight: bold;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }
`;

export default Card;