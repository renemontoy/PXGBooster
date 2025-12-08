import { useRef, useState } from 'react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

export function ValidationMS() {
  const [file, setFile] = useState(null);
  const [file2, setFile2] = useState(null);
  const fileInputRef = useRef(null);
  const fileInputRef2 = useRef(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileChange2 = (e) => {
    setFile2(e.target.files[0]);
  };

  const handleButtonClick = () => {
    // Simula el clic en el input de archivo
    fileInputRef.current.click();
  };

  const handleButtonClick2 = () => {
    // Simula el clic en el input de archivo
    fileInputRef2.current.click();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file2', file2);

    toast.promise(
      axios.post(`${import.meta.env.VITE_API_URL}/api/uploadmsmanifest/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data', 
          },
          responseType: 'blob', 
          withCredentials: false 
        }),
        {
          loading: 'Processing...',
          success: 'Complete!',
          error: 'Error',
        }
    ).then((response) => {
          // Verificar si la cabecera 'content-disposition' está presente
          let filename = 'Manifest_MS_Validation.xlsx'; // Nombre por defecto

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
        if (error.response) {
          // El servidor respondió con un código de estado fuera del rango 2xx
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        } else if (error.request) {
          // La solicitud se hizo, pero no se recibió respuesta
          console.error('Request data:', error.request);
        } else {
          // Ocurrió un error al configurar la solicitud
          console.error('Error message:', error.message);
        }
      });
    };

  return (
  
    <div style={{marginTop:20, marginLeft:30}}>
      <Toaster />
      <p className='title' style={{marginBottom:10}}>Validation MS</p>
      <p style={{fontSize:18, fontWeight:'bold'}}>Instructions:</p>
      <p style={{fontSize:16}}>-Select "Saldos por número de parte" Excel file from IES.</p>
      <p style={{fontSize:16}}>-Select MS Manifest.</p>
      <form style={{marginTop:10}} onSubmit={handleSubmit}>
        <div className='buttons-top-div'>
        <input 
        type="file"
        ref = {fileInputRef} 
        onChange={handleFileChange}
        accept='.xlsx'
        style={{display: 'none'}} // Oculta el botón de archivo predeterminado
        />
        <button 
        type='button'
        className='button-120px' 
        onClick={handleButtonClick}>
        IES file
        </button>
        <span style={{marginLeft: 10}}>
          {file ? file.name : 'No file selected'}
        </span>
        <input 
        type="file"
        ref = {fileInputRef2} 
        onChange={handleFileChange2}
        accept='.xlsx'
        style={{display: 'none'}} // Oculta el botón de archivo predeterminado
        />
        <button 
        style={{marginLeft:10}}
        type='button'
        className='button-120px' 
        onClick={handleButtonClick2}>
        Manifest
        </button>
        <span style={{marginLeft: 10}}>
          {file2 ? file2.name : 'No file selected'}
        </span>
        <button 
      style={{marginLeft:25}}
      className= 'button-120px' 
      type="submit" >
          Upload
        </button>          
        </div>
      </form>
      
    </div>
  );
};