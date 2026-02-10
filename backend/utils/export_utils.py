"""
Export Utilities for Attendance System
Export attendance records to CSV and Excel formats
"""

import csv
from io import StringIO, BytesIO
from typing import List, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def export_to_csv(records: List[Tuple]) -> StringIO:
    """
    Export attendance records to CSV format
    
    Args:
        records: List of tuples (id, person_id, name, date, time)
    
    Returns:
        StringIO buffer containing CSV data
    """
    output = StringIO()
    
    try:
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Person ID', 'Name', 'Date', 'Time'])
        
        # Write records
        for record in records:
            writer.writerow(record)
        
        logger.info(f"Exported {len(records)} records to CSV")
        
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        raise
    
    return output


def export_to_excel(records: List[Tuple]) -> BytesIO:
    """
    Export attendance records to Excel format
    
    Args:
        records: List of tuples (id, person_id, name, date, time)
    
    Returns:
        BytesIO buffer containing Excel data
    """
    output = BytesIO()
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(
            records,
            columns=['ID', 'Person ID', 'Name', 'Date', 'Time']
        )
        
        # Write to Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Attendance']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length
        
        output.seek(0)
        
        logger.info(f"Exported {len(records)} records to Excel")
        
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        raise
    
    return output
