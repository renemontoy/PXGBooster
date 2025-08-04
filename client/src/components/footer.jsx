import styled from 'styled-components';

const Footer = () => {
  return (
    <FooterContainer>
      <p>Created by <span className="highlight">René Montoy</span></p>
    </FooterContainer>
  );
};

// Estilos con Styled Components
const FooterContainer = styled.footer`
  text-align: center;
  padding: 1.5rem;
  background: transparent;
  color: #777;
  font-size: 0.9rem;
  font-family: 'Arial', sans-serif;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto; /* Para pegarlo al fondo */

  .highlight {
    color: black; /* Dorado PXG */
    font-weight: bold;
  }
`;

export default Footer;