import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Upload, Download } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '../ui/button';
import BulkImportModal from '../common/BulkImportModal'; // Need to check if this needs migration too
import { fetchTools } from '../../store/toolsSlice';

const BulkImportToolsNew = ({ onImportComplete }) => {
    const dispatch = useDispatch();
    const [showModal, setShowModal] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleDownloadTemplate = async () => {
        try {
            const response = await fetch('/api/tools/bulk-import/template', {
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
            a.download = 'tool_import_template.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success('Template downloaded successfully');
        } catch (error) {
            console.error('Error downloading template:', error);
            toast.error(error.message || 'Failed to download template');
        }
    };

    const handleImport = async (formData) => {
        setLoading(true);

        try {
            const response = await fetch('/api/tools/bulk-import', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const data = await response.json();

            // Refresh tools list if any tools were imported
            if (data.success_count > 0) {
                dispatch(fetchTools());
            }

            // Show appropriate message
            if (response.ok || response.status === 207) {
                // Success or partial success
                if (data.error_count > 0) {
                    toast.warning(data.message || 'Tools imported with some errors');
                } else {
                    toast.success(data.message || 'Tools imported successfully');
                }

                // Call completion callback if provided
                if (onImportComplete) {
                    onImportComplete(data);
                }

                return data;
            } else {
                // Complete failure - but still return data for results display
                toast.error(data.message || data.error || 'Import failed');

                // Throw error with result data attached
                const error = new Error(data.message || data.error || 'Import failed');
                error.result = data;
                throw error;
            }
        } catch (error) {
            console.error('Error importing tools:', error);

            // If error doesn't have result data, show generic error
            if (!error.result) {
                toast.error(error.message || 'Failed to import tools');
            }

            throw error;
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Button
                variant="outline"
                onClick={() => setShowModal(true)}
                className="gap-2"
            >
                <Upload className="h-4 w-4" />
                Bulk Import Tools
            </Button>

            <BulkImportModal
                show={showModal}
                onHide={() => setShowModal(false)}
                title="Bulk Import Tools"
                importType="tools"
                onImport={handleImport}
                onDownloadTemplate={handleDownloadTemplate}
                loading={loading}
            />
        </>
    );
};

export default BulkImportToolsNew;
