import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Alert,
  Snackbar,
  CircularProgress,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import FaceIcon from '@mui/icons-material/Face';
import MaskIcon from '@mui/icons-material/Masks';
import WebcamCapture from '../components/WebcamCapture';
import { recognizeFace } from '../services/api';

function Dashboard() {
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [lastCapture, setLastCapture] = useState(null);

  const handleCapture = async (blob, imageSrc) => {
    setLoading(true);
    setLastCapture(imageSrc);

    try {
      const result = await recognizeFace(blob);
      setRecognitionResult(result);

      if (result.success) {
        setSnackbar({
          open: true,
          message: `Welcome ${result.name}! Attendance marked successfully.`,
          severity: 'success',
        });
      } else {
        setSnackbar({
          open: true,
          message: result.message,
          severity: 'warning',
        });
      }
    } catch (error) {
      console.error('Recognition error:', error);
      setSnackbar({
        open: true,
        message: 'Failed to recognize face. Please try again.',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Face Recognition Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Position your face in front of the camera to mark attendance
      </Typography>

      <Grid container spacing={3}>
        {/* Webcam Section */}
        <Grid item xs={12} md={6}>
          <WebcamCapture onCapture={handleCapture} />
          
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress />
            </Box>
          )}
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, minHeight: 400 }}>
            <Typography variant="h6" gutterBottom>
              Recognition Status
            </Typography>

            {!recognitionResult && !lastCapture && (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: 300,
                  color: 'text.secondary',
                }}
              >
                <FaceIcon sx={{ fontSize: 80, mb: 2, opacity: 0.3 }} />
                <Typography variant="body1">
                  Capture an image to start recognition
                </Typography>
              </Box>
            )}

            {lastCapture && (
              <Box sx={{ mb: 3 }}>
                <img
                  src={lastCapture}
                  alt="Last capture"
                  style={{
                    width: '100%',
                    borderRadius: 8,
                    border: '2px solid #e0e0e0',
                  }}
                />
              </Box>
            )}

            {recognitionResult && (
              <Box sx={{ mt: 2 }}>
                {recognitionResult.success ? (
                  <Alert
                    severity="success"
                    icon={<CheckCircleIcon fontSize="inherit" />}
                    sx={{ mb: 2 }}
                  >
                    <Typography variant="h6">
                      {recognitionResult.name}
                    </Typography>
                    <Typography variant="body2">
                      ID: {recognitionResult.person_id}
                    </Typography>
                  </Alert>
                ) : (
                  <Alert
                    severity="warning"
                    icon={<ErrorIcon fontSize="inherit" />}
                    sx={{ mb: 2 }}
                  >
                    {recognitionResult.message}
                  </Alert>
                )}

                {/* Additional Information */}
                <Box sx={{ mt: 2 }}>
                  {recognitionResult.confidence !== null && recognitionResult.confidence !== undefined && (
                    <Chip
                      label={`Confidence: ${(recognitionResult.confidence * 100).toFixed(1)}%`}
                      color="primary"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  )}
                  
                  {recognitionResult.is_live !== null && recognitionResult.is_live !== undefined && (
                    <Chip
                      label={recognitionResult.is_live ? 'Live Person ✓' : 'Liveness Check Failed'}
                      color={recognitionResult.is_live ? 'success' : 'error'}
                      sx={{ mr: 1, mb: 1 }}
                    />
                  )}
                  
                  {recognitionResult.has_mask !== null && recognitionResult.has_mask !== undefined && (
                    <Chip
                      icon={<MaskIcon />}
                      label={recognitionResult.has_mask ? 'Mask Detected' : 'No Mask'}
                      color={recognitionResult.has_mask ? 'warning' : 'default'}
                      sx={{ mb: 1 }}
                    />
                  )}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Dashboard;
