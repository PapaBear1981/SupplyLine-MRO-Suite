import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Button, Toast, ToastContainer } from 'react-bootstrap';
import BulkImportModal from '../common/BulkImportModal';
import { fetchChemicals } from '../../store/chemicalsSlice';

const BulkImportChemicals = ({ onImportComplete }) => {
  const dispatch = useDispatch();
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', variant: 'success' });

  const showToast = (message, variant = 'success') => {
    setToast({ show: true, message, variant });
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/chemicals/bulk-import/template', {
        method: 'GET',
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to download template');
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'chemical_import_template.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showToast('Template downloaded successfully');
    } catch (error) {
      console.error('Error downloading template:', error);
      showToast(error.message || 'Failed to download template', 'danger');
    }
  };

  const handleImport = async (formData) => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/chemicals/bulk-import', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Import failed');
      }

      // Refresh chemicals list
      dispatch(fetchChemicals());

      // Show success message
      showToast(data.message || 'Chemicals imported successfully');

      // Call completion callback if provided
      if (onImportComplete) {
        onImportComplete(data);
      }

      return data;
    } catch (error) {
      console.error('Error importing chemicals:', error);
      showToast(error.message || 'Failed to import chemicals', 'danger');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="outline-primary"
        onClick={() => setShowModal(true)}
        className="me-2"
      >
        <i className="bi bi-upload me-2"></i>
        Bulk Import Chemicals
      </Button>

      <BulkImportModal
        show={showModal}
        onHide={() => setShowModal(false)}
        title="Bulk Import Chemicals"
        importType="chemicals"
        onImport={handleImport}
        onDownloadTemplate={handleDownloadTemplate}
        loading={loading}
      />

      <ToastContainer position="top-end" className="p-3">
        <Toast
          show={toast.show}
          onClose={() => setToast({ ...toast, show: false })}
          delay={5000}
          autohide
          bg={toast.variant}
        >
          <Toast.Header>
            <strong className="me-auto">
              {toast.variant === 'success' ? 'Success' : 'Error'}
            </strong>
          </Toast.Header>
          <Toast.Body className={toast.variant === 'success' ? 'text-white' : ''}>
            {toast.message}
          </Toast.Body>
        </Toast>
      </ToastContainer>
    </>
  );
};

export default BulkImportChemicals;
