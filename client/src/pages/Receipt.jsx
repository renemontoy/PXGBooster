import { useRef, useState } from 'react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

export function ValidationReceipt() {
  const [files1, setFiles1] = useState([]); // Para archivos Transfers
  const [files2, setFiles2] = useState([]); // Para archivos IES
  const fileInputRef = useRef(null);
  const fileInputRef2 = useRef(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles1(prev => [...prev, ...selectedFiles]);
    // Limpiar el input para permitir seleccionar el mismo archivo otra vez
    e.target.value = '';
  };

  const handleFileChange2 = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles2(prev => [...prev, ...selectedFiles]);
    // Limpiar el input para permitir seleccionar el mismo archivo otra vez
    e.target.value = '';
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleButtonClick2 = () => {
    fileInputRef2.current.click();
  };

  const removeFile1 = (index) => {
    setFiles1(prev => prev.filter((_, i) => i !== index));
  };

  const removeFile2 = (index) => {
    setFiles2(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files1.length === 0 || files2.length === 0) {
      toast.error('Please select at least one file from each type');
      return;
    }

    const formData = new FormData();
    
    // Agregar todos los archivos de transfers
    files1.forEach((file, index) => {
      formData.append('transfers_files', file);
    });
    
    // Agregar todos los archivos de ies
    files2.forEach((file, index) => {
      formData.append('ies_files', file);
    });

    toast.promise(
      axios.post(`${import.meta.env.VITE_API_URL}/api/uploadreceipt/`, formData, {
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
        let filename = 'Validation.xlsx';
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        
        document.body.appendChild(link);
        link.click();
        
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Limpiar archivos después de enviar
        setFiles1([]);
        setFiles2([]);
      }).catch((error) => {
        console.error('Error uploading file:', error);
      });
    };

  return (
    <div style={{marginTop:20, marginLeft:30}}>
      <Toaster />
      <p className='title' style={{marginBottom:10}}>Validation Receipt</p>
      <p style={{fontSize:18, fontWeight:'bold'}}>Instructions:</p>
      <p style={{fontSize:16}}>-Select one or more Transfers Excel files from Acumatica.</p>
      <p style={{fontSize:16}}>-Select one or more IES Excel Files.</p>
      <form style={{marginTop:10}} onSubmit={handleSubmit}>
        <div className='buttons-top-div'>
          <input 
            type="file"
            ref={fileInputRef} 
            onChange={handleFileChange}
            accept='.xlsx'
            multiple // Permite seleccionar múltiples archivos
            style={{display: 'none'}}
          />
          <button 
            type='button'
            className='button-120px' 
            onClick={handleButtonClick}
          >
            Transfers
          </button>
          <div style={{marginLeft: 10, display: 'inline-block'}}>
            {files1.length === 0 ? 'No files selected' : (
              <div>
                <span>{files1.length} file(s) selected</span>
                <div style={{marginTop: 5}}>
                  {files1.map((file, index) => (
                    <div key={index} style={{display: 'flex', alignItems: 'center', marginBottom: 2}}>
                      <span style={{marginRight: 10}}>{file.name}</span>
                      <button 
                        type="button"
                        onClick={() => removeFile1(index)}
                        style={{
                          background: 'red',
                          color: 'white',
                          border: 'none',
                          borderRadius: '50%',
                          width: '20px',
                          height: '20px',
                          cursor: 'pointer'
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <input 
            type="file"
            ref={fileInputRef2} 
            onChange={handleFileChange2}
            accept='.xlsx'
            multiple // Permite seleccionar múltiples archivos
            style={{display: 'none'}}
          />
          <button 
            style={{marginLeft:10}}
            type='button'
            className='button-120px' 
            onClick={handleButtonClick2}
          >
            IES Files
          </button>
          <div style={{marginLeft: 10, display: 'inline-block'}}>
            {files2.length === 0 ? 'No files selected' : (
              <div>
                <span>{files2.length} file(s) selected</span>
                <div style={{marginTop: 5}}>
                  {files2.map((file, index) => (
                    <div key={index} style={{display: 'flex', alignItems: 'center', marginBottom: 2}}>
                      <span style={{marginRight: 10}}>{file.name}</span>
                      <button 
                        type="button"
                        onClick={() => removeFile2(index)}
                        style={{
                          background: 'red',
                          color: 'white',
                          border: 'none',
                          borderRadius: '50%',
                          width: '20px',
                          height: '20px',
                          cursor: 'pointer'
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <button 
            style={{marginLeft:25}}
            className='button-120px' 
            type="submit"
            disabled={files1.length === 0 || files2.length === 0}
          >
            Upload
          </button>          
        </div>
      </form>
    </div>
  );
};