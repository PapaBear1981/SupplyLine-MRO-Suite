import { useState, useEffect, useRef } from 'react';
import { Card, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { Html5Qrcode } from 'html5-qrcode';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

/**
 * Scanner component for scanning barcodes and QR codes
 */
const Scanner = () => {
  const [scanning, setScanning] = useState(false);
  const [manualEntry, setManualEntry] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [cameraPermission, setCameraPermission] = useState(null);
  const scannerRef = useRef(null);
  const html5QrCodeRef = useRef(null);
  const navigate = useNavigate();

  // Initialize scanner when component mounts
  useEffect(() => {
    return () => {
      // Clean up scanner when component unmounts
      if (html5QrCodeRef.current) {
        html5QrCodeRef.current.stop().catch(error => {
          console.error("Failed to stop camera:", error);
        });
      }
    };
  }, []);

  // Start scanning
  const startScanner = async () => {
    setError('');
    setSuccess('');

    // Add a timeout to handle cases where camera initialization takes too long
    const timeoutId = setTimeout(() => {
      if (!scanning) {
        setError('Camera initialization timed out. Please try again or use manual entry.');
      }
    }, 10000);

    try {
      // Check if camera permission is granted
      const permissionStatus = await navigator.permissions.query({ name: 'camera' });
      setCameraPermission(permissionStatus.state);

      if (permissionStatus.state === 'denied') {
        setError('Camera permission is required for scanning. Please enable camera access in your browser settings.');
        return;
      }

      if (scannerRef.current && !html5QrCodeRef.current) {
        html5QrCodeRef.current = new Html5Qrcode("scanner");
      }

      const qrCodeSuccessCallback = async (decodedText) => {
        await processScannedCode(decodedText);
      };

      const config = { fps: 10, qrbox: { width: 250, height: 250 } };

      await html5QrCodeRef.current.start(
        { facingMode: "environment" },
        config,
        qrCodeSuccessCallback,
        (errorMessage) => {
          // Don't show QR scan errors to the user, they're too frequent and normal
          console.log(errorMessage);
        }
      );

      setScanning(true);
    } catch (err) {
      console.error("Error starting scanner:", err);
      setError('Failed to start scanner. Please make sure you have a camera connected and have granted permission.');
    } finally {
      clearTimeout(timeoutId);
    }
  };

  // Stop scanning
  const stopScanner = async () => {
    if (html5QrCodeRef.current && scanning) {
      try {
        await html5QrCodeRef.current.stop();
        setScanning(false);
      } catch (err) {
        console.error("Error stopping scanner:", err);
      }
    }
  };

  // Parse scanned code to determine item type and ID
  const parseScannedCode = async (decodedText) => {
    let itemType, itemId;

    try {
      // Try to parse as JSON (QR code)
      const jsonData = JSON.parse(decodedText);

      // Determine item type based on data structure
      if (jsonData.tool_number) {
        itemType = 'tool';
        itemId = jsonData.id;
      } else if (jsonData.part_number) {
        itemType = 'chemical';
        itemId = jsonData.id;
      }
    // eslint-disable-next-line no-unused-vars -- Error intentionally ignored
    } catch (_e) {
      // Not JSON, try to parse as barcode format
      const result = await parseBarcodeFormat(decodedText);
      itemType = result.itemType;
      itemId = result.itemId;
    }

    return { itemType, itemId };
  };

  // Parse barcode format
  const parseBarcodeFormat = async (decodedText) => {
    const parts = decodedText.split('-');

    if (parts.length >= 2) {
      // Check if it's a tool or chemical based on the format
      // For tools: tool_number-serial_number
      // For chemicals: part_number-lot_number-expiration_date

      // Try to find the item by its identifiers
      const response = await api.post('/scanner/lookup', {
        code: decodedText
      });

      if (response.data.item_type && response.data.item_id) {
        return {
          itemType: response.data.item_type,
          itemId: response.data.item_id
        };
      } else {
        throw new Error('Item not found');
      }
    } else {
      throw new Error('Invalid barcode format');
    }
  };

  // Process scanned code
  const processScannedCode = async (decodedText) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Stop scanner after successful scan
      await stopScanner();

      // Try to parse the code and get item type and ID
      const { itemType, itemId } = await parseScannedCode(decodedText);

      if (itemType && itemId) {
        setSuccess(`Found ${itemType} with ID ${itemId}. Redirecting...`);

        // Navigate to the appropriate page immediately
        navigate(`/${itemType}s/${itemId}`);
      } else {
        throw new Error('Could not determine item type or ID');
      }
    } catch (err) {
      console.error("Error processing scan:", err);
      setError(`Failed to process scan: ${err.message || 'Unknown error'}`);
      // Re-enable scanner after error
      startScanner();
    } finally {
      setLoading(false);
    }
  };

  // Handle manual entry
  const handleManualEntry = async (e) => {
    e.preventDefault();

    if (!manualEntry.trim()) {
      setError('Please enter a barcode or QR code value');
      return;
    }

    await processScannedCode(manualEntry.trim());
  };

  return (
    <div className="scanner-container">
      <Card className="mb-4">
        <Card.Header>
          <h4>Barcode & QR Code Scanner</h4>
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          {cameraPermission === 'denied' && (
            <Alert variant="warning">
              Camera access is denied. Please enable camera access in your browser settings to use the scanner.
            </Alert>
          )}

          <div className="text-center mb-4">
            {!scanning ? (
              <Button
                variant="primary"
                onClick={startScanner}
                disabled={loading || cameraPermission === 'denied'}
              >
                Start Scanner
              </Button>
            ) : (
              <Button
                variant="secondary"
                onClick={stopScanner}
                disabled={loading}
              >
                Stop Scanner
              </Button>
            )}
          </div>

          <div
            id="scanner"
            ref={scannerRef}
            role="region"
            aria-label="QR code scanner viewfinder"
            style={{
              width: '100%',
              minHeight: '300px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              display: scanning ? 'block' : 'none'
            }}
          ></div>

          <hr className="my-4" />

          <h5>Manual Entry</h5>
          <p className="text-muted">If scanning doesn't work, you can manually enter the barcode or QR code value:</p>

          <Form onSubmit={handleManualEntry}>
            <Form.Group className="mb-3">
              <Form.Control
                type="text"
                placeholder="Enter barcode or QR code value"
                value={manualEntry}
                onChange={(e) => setManualEntry(e.target.value)}
                disabled={loading}
              />
            </Form.Group>
            <Button
              type="submit"
              variant="primary"
              disabled={loading || !manualEntry.trim()}
            >
              {loading ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                  <span className="ms-2">Processing...</span>
                </>
              ) : (
                'Submit'
              )}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default Scanner;
