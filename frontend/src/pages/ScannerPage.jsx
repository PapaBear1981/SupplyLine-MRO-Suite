import { Card, Row, Col } from 'react-bootstrap';
import Scanner from '../components/scanner/Scanner';
import { useHelp } from '../context/HelpContext';
import HelpContent from '../components/common/HelpContent';
import HelpIcon from '../components/common/HelpIcon';

/**
 * Page component for the barcode/QR code scanner
 */
const ScannerPage = () => {
  const { showHelp } = useHelp();

  return (
    <div className="scanner-page">
      {showHelp && (
        <HelpContent title="Barcode & QR Code Scanner" initialOpen={false}>
          <p>This page allows you to scan barcodes and QR codes to quickly access tool and chemical information.</p>
          <ul>
            <li><strong>Camera Scanner:</strong> Click "Start Scanner" to activate your device's camera for scanning.</li>
            <li><strong>Manual Entry:</strong> If scanning doesn't work, you can manually enter the barcode or QR code value.</li>
            <li><strong>Supported Formats:</strong> The scanner supports both traditional barcodes and QR codes.</li>
            <li><strong>Navigation:</strong> After a successful scan, you'll be automatically redirected to the corresponding item's detail page.</li>
          </ul>
        </HelpContent>
      )}

      <div className="d-flex justify-content-between align-items-center mb-4">
        <div className="d-flex align-items-center">
          <h2>Barcode & QR Code Scanner</h2>
          {showHelp && (
            <HelpIcon
              title="Scanner"
              content={
                <>
                  <p>Use this page to scan barcodes and QR codes for quick access to inventory items.</p>
                  <p>You can scan codes using your device's camera or enter the code manually if needed.</p>
                </>
              }
            />
          )}
        </div>
      </div>

      <Row>
        <Col lg={8} className="mx-auto">
          <Scanner />
          
          <Card className="mb-4">
            <Card.Header>
              <h4>Scanner Instructions</h4>
            </Card.Header>
            <Card.Body>
              <h5>How to Use the Scanner</h5>
              <ol>
                <li>Click the "Start Scanner" button to activate your camera.</li>
                <li>Position the barcode or QR code within the scanning area.</li>
                <li>Hold steady until the code is recognized.</li>
                <li>After a successful scan, you'll be redirected to the item's details page.</li>
              </ol>
              
              <h5>Tips for Successful Scanning</h5>
              <ul>
                <li>Ensure good lighting conditions for better scanning results.</li>
                <li>Hold the device steady to avoid blurry images.</li>
                <li>Make sure the entire code is visible in the camera view.</li>
                <li>If scanning fails repeatedly, try the manual entry option.</li>
              </ul>
              
              <h5>Supported Code Types</h5>
              <ul>
                <li><strong>Barcodes:</strong> Standard barcodes used on tools and chemicals.</li>
                <li><strong>QR Codes:</strong> QR codes containing detailed item information.</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ScannerPage;
