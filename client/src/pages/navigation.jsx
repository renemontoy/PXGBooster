import Card from "../components/card";
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";
import Slider from 'react-slick';


export function PXG() {
  const cardsData = [
    {
      title: "Adyen",
      imageUrl: "/images/PXG1.jpg",
      route: "/Adyen"
    },
    {
      title: "Shopify",
      imageUrl: "/images/PXG2.jpg",
      route: "/Shopify"
    },
    {
      title: "Global Payments",
      imageUrl: "/images/PXG3.jpg",
      route: "/defect_warranty"
    },
    {
      title: "Canada",
      imageUrl: "/images/PXG4.jpg",
      route: "/Canada"
    },
    {
      title: "Ferrule",
      imageUrl: "/images/PXG5.jpg",
      route: "/Ferrule"
    },
    {
      title: "Defect & Warranty",
      imageUrl: "/images/PXG6.jpg",
      route: "/defect_warranty"
    },
    {
      title: "Spec Check Analysis",
      imageUrl: "/images/PXG7.jpg",
      route: "/defect_warranty"
    }
  ];

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 3, // Muestra 3 tarjetas a la vez
    slidesToScroll: 1,
    centerMode: true,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1
        }
      }
    ]
  };

  return (
    <div style={{
      padding: '5px 0',
      background: 'white',
    }}>
      
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Slider {...sliderSettings}>
          {cardsData.map((card, index) => (
            <div key={index}>
              <Card 
                title={card.title}
                imageUrl={card.imageUrl}
                route={card.route}
              />
            </div>
          ))}
        </Slider>
      </div>
    </div>
  );
};