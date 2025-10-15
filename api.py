from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_excel_data(file_path):
    """Process the Excel file and return analyzed data"""
    try:
        # Load Excel file and sheets
        f = pd.ExcelFile(file_path)

        # Load Amazon PO sheet
        df1 = pd.read_excel(
            f,
            sheet_name="AmzaonPO",
            dtype={'Purchase Order': str, 'UPC': str}
        )

        # Load Custom Sales Order Register
        df2 = pd.read_excel(
            f,
            sheet_name="CustomSalesOrderRegisterM",
            skiprows=6,
            dtype={'Reference Number': str, 'Item: UPC Code': str, 'SPS UPC': str}
        )

        df3 = pd.read_excel(
            f,
            sheet_name="Mapping",
            skiprows=1,
            dtype={'Reference Number': str, 'SO Item: UPC Code': str}
        )

        control = pd.read_excel(
            f,
            sheet_name="Control",
            skiprows=2,
            dtype={'UPC': str, 'SO Item: UPC Code': str}
        )

        # Group and aggregate Amazon PO data
        df1 = df1.groupby(["Purchase Order", "UPC"], as_index=False).agg({
            'Amazon Invoice ID': 'first',
            'Receive Date': 'min',
            'Quantity': 'sum',
            'Net Receipts': 'sum'
        })

        # Create UPC mapping
        upc_map = dict(zip(control["UPC"], control["SO Item: UPC Code"]))

        # Map SO Reference Number
        df1["SO Reference Number"] = df1["Purchase Order"].where(
            df1["Purchase Order"].isin(df2["Reference Number"])
        )

        # Map SO Item UPC Code
        df1["SO Item: UPC Code"] = df1["UPC"].map(upc_map)

        # Calculate SO Total Revenue
        df1["SO Total Revenue"] = df1.apply(
            lambda row: df2.loc[
                (df2["Reference Number"] == row["SO Reference Number"]) &
                (df2["Item: UPC Code"] == row["SO Item: UPC Code"]),
                "Total Revenue"
            ].sum(),
            axis=1
        )

        # Calculate Variance
        df1['Variance'] = (df1['Net Receipts'] - df1['SO Total Revenue']) / 10
        df1.loc[df1["SO Item: UPC Code"].isna() | (df1["SO Item: UPC Code"] == ""), "Variance"] = 0

        # Calculate Deductions
        df1['Actual Deductions'] = df1['Net Receipts'] / 10
        df1['Expected Deductions'] = df1['SO Total Revenue'] / 10

        # Classification
        df1['Classification'] = df1['Variance'].apply(
            lambda x: 'Disputable' if x > 0 else ('Under-Applied' if x < 0 else 'Confirmed Valid')
        )

        return df1

    except Exception as e:
        print(f"Error processing Excel: {str(e)}")
        print(traceback.format_exc())
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/process-default', methods=['GET'])
def process_default_file():
    """Process the default Excel file in the workspace"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        
        # Convert Receive Date to datetime for proper handling
        df['Receive Date'] = pd.to_datetime(df['Receive Date'], errors='coerce')
        
        # Group by Amazon Invoice ID
        grouped = df.groupby('Amazon Invoice ID').agg({
            'Purchase Order': 'first',
            'UPC': 'first',
            'Receive Date': 'last',  # Keep the last (most recent) date
            'Quantity': 'sum',
            'Net Receipts': 'sum',
            'SO Reference Number': 'first',
            'SO Item: UPC Code': 'first',
            'SO Total Revenue': 'sum',
            'Variance': 'sum',
            'Actual Deductions': 'sum',
            'Expected Deductions': 'sum',
            'Classification': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]  # Most common classification
        }).reset_index()
        
        # Recalculate classification based on summed variance
        grouped['Classification'] = grouped['Variance'].apply(
            lambda x: 'Disputable' if x > 0 else ('Under-Applied' if x < 0 else 'Confirmed Valid')
        )
        
        # Convert DataFrame to JSON-friendly format
        df_copy = grouped.copy()
        
        # Format datetime columns to "Month Day, Year" format (e.g., "Jan 15, 2024")
        if 'Receive Date' in df_copy.columns:
            df_copy['Receive Date'] = df_copy['Receive Date'].apply(
                lambda x: x.strftime('%b %d, %Y') if pd.notna(x) else None
            )
        
        # Replace NaN with None for JSON serialization
        df_copy = df_copy.replace({np.nan: None})
        
        result = {
            'success': True,
            'data': df_copy.to_dict(orient='records'),
            'total_records': len(df_copy),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/upload-and-process', methods=['POST'])
def upload_and_process():
    """Upload and process a new Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .xlsx and .xls allowed'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the file
        df = process_excel_data(file_path)
        
        # Convert DataFrame to JSON-friendly format
        df_copy = df.copy()
        if 'Receive Date' in df_copy.columns:
            df_copy['Receive Date'] = df_copy['Receive Date'].astype(str)
        df_copy = df_copy.replace({np.nan: None})
        
        result = {
            'success': True,
            'filename': filename,
            'data': df_copy.to_dict(orient='records'),
            'total_records': len(df_copy),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics from the default file"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        
        # Calculate summary statistics
        summary = {
            'total_records': int(len(df)),
            'total_variance': float(df['Variance'].sum()),
            'positive_variance': float(df[df['Variance'] > 0]['Variance'].sum()),
            'total_net_receipts': float(df['Net Receipts'].sum()),
            'total_so_revenue': float(df['SO Total Revenue'].sum()),
            'total_actual_deductions': float(df['Actual Deductions'].sum()),
            'total_expected_deductions': float(df['Expected Deductions'].sum()),
            'classification_breakdown': df['Classification'].value_counts().to_dict(),
            'average_variance': float(df['Variance'].mean()),
            'disputable_count': int((df['Classification'] == 'Disputable').sum()),
            'under_applied_count': int((df['Classification'] == 'Under-Applied').sum()),
            'confirmed_valid_count': int((df['Classification'] == 'Confirmed Valid').sum()),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(summary)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/filter', methods=['POST'])
def filter_data():
    """Filter data based on criteria"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        
        # Get filter parameters from request
        filters = request.json or {}
        
        # Apply filters
        if 'classification' in filters and filters['classification']:
            df = df[df['Classification'] == filters['classification']]
        
        if 'min_variance' in filters:
            df = df[df['Variance'] >= float(filters['min_variance'])]
        
        if 'max_variance' in filters:
            df = df[df['Variance'] <= float(filters['max_variance'])]
        
        if 'purchase_order' in filters and filters['purchase_order']:
            df = df[df['Purchase Order'] == filters['purchase_order']]
        
        if 'upc' in filters and filters['upc']:
            df = df[df['UPC'] == filters['upc']]
        
        # Convert to JSON-friendly format
        df_copy = df.copy()
        if 'Receive Date' in df_copy.columns:
            df_copy['Receive Date'] = df_copy['Receive Date'].astype(str)
        df_copy = df_copy.replace({np.nan: None})
        
        result = {
            'success': True,
            'data': df_copy.to_dict(orient='records'),
            'total_records': len(df_copy),
            'filters_applied': filters,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/disputable-items', methods=['GET'])
def get_disputable_items():
    """Get only disputable items"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        df_disputable = df[df['Classification'] == 'Disputable'].copy()
        
        # Convert to JSON-friendly format
        if 'Receive Date' in df_disputable.columns:
            df_disputable['Receive Date'] = df_disputable['Receive Date'].astype(str)
        df_disputable = df_disputable.replace({np.nan: None})
        
        # Sort by variance (highest first)
        df_disputable = df_disputable.sort_values('Variance', ascending=False)
        
        result = {
            'success': True,
            'data': df_disputable.to_dict(orient='records'),
            'total_disputable': len(df_disputable),
            'total_disputable_amount': float(df_disputable['Variance'].sum()),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/monthly-trends', methods=['GET'])
def get_monthly_trends():
    """Get monthly deduction trends grouped by receive date"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        
        # Convert Receive Date to datetime
        df['Receive Date'] = pd.to_datetime(df['Receive Date'], errors='coerce')
        
        # Filter out rows with invalid dates
        df_with_dates = df[df['Receive Date'].notna()].copy()
        
        # Extract year-month for grouping
        df_with_dates['YearMonth'] = df_with_dates['Receive Date'].dt.to_period('M')
        
        # Group by month and sum deductions
        monthly_summary = df_with_dates.groupby('YearMonth').agg({
            'Actual Deductions': 'sum',
            'Expected Deductions': 'sum'
        }).reset_index()
        
        # Convert Period to string for JSON serialization
        monthly_summary['month'] = monthly_summary['YearMonth'].astype(str)
        monthly_summary = monthly_summary.drop('YearMonth', axis=1)
        
        # Round values for cleaner display
        monthly_summary['Actual Deductions'] = monthly_summary['Actual Deductions'].round(2)
        monthly_summary['Expected Deductions'] = monthly_summary['Expected Deductions'].round(2)
        
        # Sort by month
        monthly_summary = monthly_summary.sort_values('month')
        
        result = {
            'success': True,
            'data': monthly_summary.to_dict(orient='records'),
            'total_months': len(monthly_summary),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/variance-by-classification', methods=['GET'])
def get_variance_by_classification():
    """Get variance amounts by classification for chart"""
    try:
        file_path = "AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx"
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Default file not found'}), 404
        
        df = process_excel_data(file_path)
        
        # Split by classification
        confirmed_valid = df.loc[df['Classification'] == 'Confirmed Valid']
        disputable = df.loc[df['Classification'] == 'Disputable']
        under_applied = df.loc[df['Classification'] == 'Under-Applied']
        
        # Calculate amounts for each classification
        values = {
            "Confirmed Valid": float(confirmed_valid.loc[confirmed_valid['Variance'] == 0, 'Actual Deductions'].sum()),
            "Disputable": float(disputable.loc[disputable['Variance'] > 0, 'Variance'].sum()),
            "Under-Applied": float(-under_applied.loc[under_applied['Variance'] < 0, 'Variance'].sum()),
        }
        
        # Create chart data
        chart_data = [
            {"name": "Confirmed Valid", "value": values["Confirmed Valid"]},
            {"name": "Disputable", "value": values["Disputable"]},
            {"name": "Under-Applied", "value": values["Under-Applied"]},
        ]
        
        result = {
            'success': True,
            'data': chart_data,
            'totals': values,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
