import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import StopIcon from '@mui/icons-material/Stop';

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: 'user',
};

function WebcamCapture({ onCapture, autoCapture = false, captureInterval = 2000 }) {
  const webcamRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        // Convert base64 to blob
        fetch(imageSrc)
          .then(res => res.blob())
          .then(blob => {
            onCapture(blob, imageSrc);
          })
          .catch(err => {
            console.error('Capture error:', err);
            setError('Failed to capture image');
          });
      }
    }
  }, [onCapture]);

  const startAutoCapture = useCallback(() => {
    setIsActive(true);
    intervalRef.current = setInterval(() => {
      capture();
    }, captureInterval);
  }, [capture, captureInterval]);

  const stopAutoCapture = useCallback(() => {
    setIsActive(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const handleUserMediaError = useCallback((err) => {
    console.error('Webcam error:', err);
    setError('Failed to access webcam. Please ensure camera permissions are granted.');
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 2, position: 'relative' }}>
      <Box sx={{ position: 'relative', borderRadius: 2, overflow: 'hidden', bgcolor: '#000' }}>
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          onUserMediaError={handleUserMediaError}
          style={{ width: '100%', display: 'block', transform: 'scaleX(-1)' }}
        />
        
        {/* Live indicator */}
        {isActive && (
          <Box
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
              bgcolor: 'error.main',
              color: 'white',
              px: 2,
              py: 0.5,
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'white',
                animation: 'pulse 1.5s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.3 },
                },
              }}
            />
            <Typography variant="caption" fontWeight="bold">
              LIVE
            </Typography>
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
        {autoCapture ? (
          <>
            <Button
              variant="contained"
              color="primary"
              onClick={startAutoCapture}
              disabled={isActive}
              startIcon={<CameraAltIcon />}
            >
              Start Auto Capture
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={stopAutoCapture}
              disabled={!isActive}
              startIcon={<StopIcon />}
            >
              Stop
            </Button>
          </>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={capture}
            startIcon={<CameraAltIcon />}
            fullWidth
          >
            Capture Photo
          </Button>
        )}
      </Box>
    </Paper>
  );
}

export default WebcamCapture;
