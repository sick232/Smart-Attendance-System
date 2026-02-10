import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Grid,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { getAttendance, getAllPersons, exportToCSV, exportToExcel } from '../services/api';
import { format } from 'date-fns';

function Attendance() {
  const [attendance, setAttendance] = useState([]);
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filters
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [selectedPerson, setSelectedPerson] = useState('');

  useEffect(() => {
    loadPersons();
    loadAttendance();
  }, []);

  const loadPersons = async () => {
    try {
      const data = await getAllPersons();
      setPersons(data);
    } catch (err) {
      console.error('Failed to load persons:', err);
    }
  };

  const loadAttendance = async (filters = {}) => {
    setLoading(true);
    setError(null);

    try {
      const data = await getAttendance(filters);
      setAttendance(data);
    } catch (err) {
      console.error('Failed to load attendance:', err);
      setError('Failed to load attendance records');
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = () => {
    const filters = {};
    
    if (startDate) {
      filters.startDate = format(startDate, 'yyyy-MM-dd');
    }
    
    if (endDate) {
      filters.endDate = format(endDate, 'yyyy-MM-dd');
    }
    
    if (selectedPerson) {
      filters.personId = selectedPerson;
    }

    loadAttendance(filters);
  };

  const handleReset = () => {
    setStartDate(null);
    setEndDate(null);
    setSelectedPerson('');
    loadAttendance();
  };

  const handleExportCSV = async () => {
    try {
      const filters = {};
      if (startDate) filters.startDate = format(startDate, 'yyyy-MM-dd');
      if (endDate) filters.endDate = format(endDate, 'yyyy-MM-dd');
      if (selectedPerson) filters.personId = selectedPerson;

      const blob = await exportToCSV(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `attendance_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export error:', err);
      setError('Failed to export CSV');
    }
  };

  const handleExportExcel = async () => {
    try {
      const filters = {};
      if (startDate) filters.startDate = format(startDate, 'yyyy-MM-dd');
      if (endDate) filters.endDate = format(endDate, 'yyyy-MM-dd');
      if (selectedPerson) filters.personId = selectedPerson;

      const blob = await exportToExcel(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `attendance_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Export error:', err);
      setError('Failed to export Excel');
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Attendance Records
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          View and export attendance records with filters
        </Typography>

        {/* Filters */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>

          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Start Date"
                value={startDate}
                onChange={setStartDate}
                slotProps={{ 
                  textField: { fullWidth: true } 
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="End Date"
                value={endDate}
                onChange={setEndDate}
                slotProps={{ 
                  textField: { fullWidth: true } 
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                select
                label="Person"
                value={selectedPerson}
                onChange={(e) => setSelectedPerson(e.target.value)}
              >
                <MenuItem value="">All Persons</MenuItem>
                {persons.map((person) => (
                  <MenuItem key={person.person_id} value={person.person_id}>
                    {person.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleFilter}
                  fullWidth
                >
                  Apply
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleReset}
                  fullWidth
                >
                  Reset
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Export Buttons */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="success"
            startIcon={<DownloadIcon />}
            onClick={handleExportCSV}
          >
            Export CSV
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<DownloadIcon />}
            onClick={handleExportExcel}
          >
            Export Excel
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => loadAttendance()}
          >
            Refresh
          </Button>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Attendance Table */}
        <Paper elevation={3}>
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Attendance Records
            </Typography>
            <Chip
              label={`${attendance.length} records`}
              color="primary"
            />
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : attendance.length === 0 ? (
            <Alert severity="info" sx={{ m: 2 }}>
              No attendance records found
            </Alert>
          ) : (
            <TableContainer sx={{ maxHeight: 600 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>ID</strong></TableCell>
                    <TableCell><strong>Person ID</strong></TableCell>
                    <TableCell><strong>Name</strong></TableCell>
                    <TableCell><strong>Date</strong></TableCell>
                    <TableCell><strong>Time</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendance.map((record) => (
                    <TableRow
                      key={record.id}
                      hover
                      sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}
                    >
                      <TableCell>{record.id}</TableCell>
                      <TableCell>
                        <Chip label={record.person_id} size="small" />
                      </TableCell>
                      <TableCell>{record.name}</TableCell>
                      <TableCell>{record.date}</TableCell>
                      <TableCell>{record.time}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Box>
    </LocalizationProvider>
  );
}

export default Attendance;
