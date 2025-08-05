import { useRef, useState } from 'react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

export function Ferrule() {
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);


  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleButtonClick = () => {
    // Simula el clic en el input de archivo
    fileInputRef.current.click();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
  
    // Usar toast.promise para mostrar mensajes de carga y resultados de la promesa
    toast.promise(
      axios.post('http://localhost:8000/api/uploadferrule', formData, {
        headers: {
          'Content-Type': 'multipart/form-data', 
        },
        responseType: 'blob', 
        withCredentials: true 
      }),
      {
        loading: 'Processing...',
        success: 'Complete!',
        error: 'Error',
      }
    ).then((response) => {
      // Verificar si la cabecera 'content-disposition' está presente
      let filename = 'Tequila_Shipments_Details_Ferrule.csv'; // Nombre por defecto
  
      // Crear un enlace de descarga para el archivo recibido
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      
      // Simular un clic en el enlace para iniciar la descarga
      document.body.appendChild(link);
      link.click();
      
      // Limpiar después de la descarga
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    }).catch((error) => {
      console.error('Error uploading file:', error);
    }).finally(() => {
    });
  };


  return (
    <div style={{marginTop:20, marginLeft:30}}>
      <Toaster />
      <p className='title' style={{marginBottom:10}}>Ferrule Program</p>
      <p style={{fontSize:18, fontWeight:'bold'}}>Insert Tequila Shipments Details to add Ferrules </p>
      <p style={{fontSize:15}}>Note: Please remember that the file must be the one you downloaded from tableau today.</p>
      <form className='buttons-top-div' style={{marginTop:10}} onSubmit={handleSubmit}>
        <input 
        type="file"
        ref = {fileInputRef} 
        onChange={handleFileChange}
        accept='.csv'
        style={{display: 'none'}} // Oculta el botón de archivo predeterminado
        />
        <button 
        type='button'
        className='button-120px' 
        onClick={handleButtonClick}>
        Select File
        </button>
        <span style={{marginLeft: 10}}>
          {file ? file.name : 'No file selected'}
        </span>
        <button 
      style={{marginLeft:25}}
      className= 'button-120px' 
      type="submit" >
          Upload
        </button>
      </form>
      
    </div>
  );
};