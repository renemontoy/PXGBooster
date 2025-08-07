import { useRef, useState } from 'react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

export function Spec() {
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const [week, setWeek] = useState('');


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
    formData.append('weekfront', week);

  
    // Usar toast.promise para mostrar mensajes de carga y resultados de la promesa
    toast.promise(
      axios.post(`${import.meta.env.VITE_API_URL}/api/uploadspec/`, formData, {
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
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'Spec Check Analysis.pdf'; // Nombre por defecto

        if (contentDisposition) {
            // Maneja casos con comillas y encoding (RFC 5987)
            const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?/i);
            if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1]
                .replace(/['"]/g, '')
                .replace(/\s+/g, '_'); // Reemplaza espacios por _
            }
        }
  
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
      <p className='title' style={{marginBottom:10}}>Spec Check Analysis</p>
      <p style={{fontSize:18, fontWeight:'bold'}}>Instructions: </p>
      <p style={{fontSize:15}}>-Select the Dock Audit Excel file.</p>
      <p style={{fontSize:15}}>-Insert the desired week.</p>
      <p style={{fontSize:15}}>-Click Upload to generate the Spec Check Analysis report.</p>


      <form onSubmit={handleSubmit}>
        <div>
         <div className='buttons-top-div'>
          <label>Week</label> 
          <input 
          className='input'
          style={{marginLeft:7,marginBottom:10, marginTop:-2.8}}
          type="number"
          value={week}
          onChange={(e) => setWeek(e.target.value)}
          />
        </div>
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
        Spec File
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
        </div>          
        </div>
      </form>
      
    </div>
  );
};