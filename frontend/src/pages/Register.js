import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  Snackbar,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import WebcamCapture from '../components/WebcamCapture';
import { registerPerson } from '../services/api';

function Register() {
  const [name, setName] = useState('');
  const [personId, setPersonId] = useState('');
  const [capturedImages, setCapturedImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const handleCapture = (blob, imageSrc) => {
    if (capturedImages.length < 10) {
      setCapturedImages([...capturedImages, { blob, imageSrc }]);
      setSnackbar({
        open: true,
        message: `Image ${capturedImages.length + 1} captured successfully!`,
        severity: 'success',
      });
    } else {
      setSnackbar({
        open: true,
        message: 'Maximum 10 images allowed',
        severity: 'warning',
      });
    }
  };

  const handleDeleteImage = (index) => {
    const newImages = capturedImages.filter((_, i) => i !== index);
    setCapturedImages(newImages);
  };

  const handleSubmit = async () => {
    if (!name || !personId) {
      setSnackbar({
        open: true,
        message: 'Please enter name and person ID',
        severity: 'error',
      });
      return;
    }

    if (capturedImages.length < 5) {
      setSnackbar({
        open: true,
        message: 'Please capture at least 5 images',
        severity: 'error',
      });
      return;
    }

    setLoading(true);

    try {
      const imageBlobs = capturedImages.map(img => img.blob);
      const result = await registerPerson(name, personId, imageBlobs);

      setSnackbar({
        open: true,
        message: result.message,
        severity: 'success',
      });

      // Reset form
      setName('');
      setPersonId('');
      setCapturedImages([]);
    } catch (error) {
      console.error('Registration error:', error);
      let errorMessage = 'Failed to register person';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
          errorMessage = detail.map(err => {
            if (typeof err === 'object' && err.msg) {
              return err.msg;
            }
            return String(err);
          }).join('; ');
        } else {
          errorMessage = String(detail);
        }
      }
      
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Register New Person
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Capture 5-10 clear images from different angles for best recognition accuracy
      </Typography>

      <Grid container spacing={3}>
        {/* Form Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Person Information
            </Typography>

            <TextField
              fullWidth
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
              required
            />

            <TextField
              fullWidth
              label="Person ID"
              value={personId}
              onChange={(e) => setPersonId(e.target.value.toLowerCase().replace(/\s/g, '_'))}
              margin="normal"
              required
              helperText="Unique identifier (e.g., emp001, student123)"
            />

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Tips for best results:</strong>
              </Typography>
              <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                <li>Capture images from different angles</li>
                <li>Vary your facial expressions</li>
                <li>Ensure good lighting</li>
                <li>Look directly at the camera</li>
              </ul>
            </Alert>
          </Paper>

          {/* Captured Images List */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Captured Images
              </Typography>
              <Chip
                label={`${capturedImages.length}/10`}
                color={capturedImages.length >= 5 ? 'success' : 'warning'}
              />
            </Box>

            {capturedImages.length === 0 ? (
              <Alert severity="info">
                No images captured yet. Start capturing images using the camera.
              </Alert>
            ) : (
              <List>
                {capturedImages.map((img, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton edge="end" onClick={() => handleDeleteImage(index)}>
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <img
                      src={img.imageSrc}
                      alt={`Capture ${index + 1}`}
                      style={{
                        width: 80,
                        height: 60,
                        objectFit: 'cover',
                        borderRadius: 4,
                        marginRight: 16,
                      }}
                    />
                    <ListItemText
                      primary={`Image ${index + 1}`}
                      secondary={`Captured`}
                    />
                  </ListItem>
                ))}
              </List>
            )}

            <Button
              variant="contained"
              color="primary"
              fullWidth
              sx={{ mt: 2 }}
              onClick={handleSubmit}
              disabled={loading || capturedImages.length < 5 || !name || !personId}
              startIcon={<PersonAddIcon />}
            >
              {loading ? 'Registering...' : 'Register Person'}
            </Button>

            {loading && <LinearProgress sx={{ mt: 2 }} />}
          </Paper>
        </Grid>

        {/* Webcam Section */}
        <Grid item xs={12} md={6}>
          <WebcamCapture onCapture={handleCapture} />
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

export default Register;
