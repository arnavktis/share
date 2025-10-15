# Flask API for Amazon NetSuite PO/SO Analysis

This Flask API provides endpoints for processing and analyzing Amazon Purchase Orders and NetSuite Sales Orders data.

## Setup Instructions

### 1. Install Dependencies

```bash
# Activate your virtual environment
source {venv_name}/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python api.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:00:00"
}
```

---

### 2. Process Default File

**GET** `/api/process-default`

Process the default Excel file (`AMZN_NETSUITE_POs_SOs_Mapping 1.xlsx`) in the workspace.

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "Purchase Order": "PO123456",
      "UPC": "123456789012",
      "Amazon Invoice ID": "INV-001",
      "Receive Date": "2025-01-15",
      "Quantity": 100,
      "Net Receipts": 5000.0,
      "SO Reference Number": "SO123",
      "SO Item: UPC Code": "123456789012",
      "SO Total Revenue": 4800.0,
      "Variance": 20.0,
      "Actual Deductions": 500.0,
      "Expected Deductions": 480.0,
      "Classification": "Disputable"
    }
  ],
  "total_records": 150,
  "timestamp": "2025-10-14T12:00:00"
}
```

---

### 3. Get Summary Statistics

**GET** `/api/summary`

Get aggregated summary statistics from the processed data.

**Response:**

```json
{
  "total_records": 150,
  "total_variance": 1250.5,
  "total_net_receipts": 125000.0,
  "total_so_revenue": 112500.0,
  "total_actual_deductions": 12500.0,
  "total_expected_deductions": 11250.0,
  "classification_breakdown": {
    "Disputable": 45,
    "Under-Applied": 30,
    "Confirmed Valid": 75
  },
  "average_variance": 8.34,
  "disputable_count": 45,
  "under_applied_count": 30,
  "confirmed_valid_count": 75,
  "timestamp": "2025-10-14T12:00:00"
}
```

---

### 4. Get Disputable Items Only

**GET** `/api/disputable-items`

Get only items classified as "Disputable" (sorted by variance, highest first).

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "Purchase Order": "PO123456",
      "UPC": "123456789012",
      "Variance": 150.25,
      "Classification": "Disputable",
      ...
    }
  ],
  "total_disputable": 45,
  "total_disputable_amount": 2500.75,
  "timestamp": "2025-10-14T12:00:00"
}
```

---

### 5. Filter Data

**POST** `/api/filter`

Filter the processed data based on various criteria.

**Request Body:**

```json
{
  "classification": "Disputable",
  "min_variance": 10,
  "max_variance": 100,
  "purchase_order": "PO123456",
  "upc": "123456789012"
}
```

All fields are optional. You can use any combination of filters.

**Response:**

```json
{
  "success": true,
  "data": [...],
  "total_records": 25,
  "filters_applied": {
    "classification": "Disputable",
    "min_variance": 10
  },
  "timestamp": "2025-10-14T12:00:00"
}
```

---

### 6. Upload and Process New File

**POST** `/api/upload-and-process`

Upload a new Excel file and process it.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Field name: `file`
- File types: `.xlsx`, `.xls`
- Max size: 16MB

**Example using cURL:**

```bash
curl -X POST http://localhost:5000/api/upload-and-process \
  -F "file=@/path/to/your/file.xlsx"
```

**Response:**

```json
{
  "success": true,
  "filename": "20251014_120000_your_file.xlsx",
  "data": [...],
  "total_records": 150,
  "timestamp": "2025-10-14T12:00:00"
}
```

---

## Data Fields Explanation

- **Purchase Order**: Amazon PO number
- **UPC**: Universal Product Code
- **Amazon Invoice ID**: Amazon invoice identifier
- **Receive Date**: Date when goods were received
- **Quantity**: Total quantity received
- **Net Receipts**: Total net receipts amount
- **SO Reference Number**: Sales Order reference number
- **SO Item: UPC Code**: Mapped UPC code from Sales Order
- **SO Total Revenue**: Total revenue from Sales Order
- **Variance**: Difference between Net Receipts and SO Total Revenue (divided by 10)
- **Actual Deductions**: Actual deductions (Net Receipts / 10)
- **Expected Deductions**: Expected deductions (SO Total Revenue / 10)
- **Classification**:
  - `Disputable`: Variance > 0 (overpayment)
  - `Under-Applied`: Variance < 0 (underpayment)
  - `Confirmed Valid`: Variance = 0 (exact match)

---

## Using with Next.js Frontend

### Example API Calls

#### 1. Fetch Data in Next.js (App Router)

```typescript
// app/api/data/route.ts or in a client component
export async function GET() {
  const response = await fetch("http://localhost:5000/api/process-default");
  const data = await response.json();
  return Response.json(data);
}
```

#### 2. Client-side Data Fetching

```typescript
"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/api/summary")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Summary</h1>
      <p>Total Records: {data?.total_records}</p>
      <p>Total Variance: ${data?.total_variance}</p>
    </div>
  );
}
```

#### 3. Filter Data

```typescript
const filterData = async (filters: any) => {
  const response = await fetch("http://localhost:5000/api/filter", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(filters),
  });
  return response.json();
};

// Usage
const results = await filterData({
  classification: "Disputable",
  min_variance: 10,
});
```

#### 4. Upload File

```typescript
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:5000/api/upload-and-process", {
    method: "POST",
    body: formData,
  });
  return response.json();
};
```

---

## CORS Configuration

The API is configured with CORS enabled to allow requests from your Next.js frontend. In production, you may want to restrict CORS to specific origins:

```python
# In api.py
CORS(app, origins=['http://localhost:3000', 'https://yourdomain.com'])
```

---

## Error Handling

All endpoints return error responses in the following format:

```json
{
  "error": "Error message",
  "traceback": "Detailed stack trace (only in debug mode)"
}
```

HTTP Status Codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (file not found)
- `500`: Internal Server Error

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Get summary
curl http://localhost:5000/api/summary

# Get disputable items
curl http://localhost:5000/api/disputable-items

# Filter data
curl -X POST http://localhost:5000/api/filter \
  -H "Content-Type: application/json" \
  -d '{"classification": "Disputable"}'
```

### Using Python

```python
import requests

# Get summary
response = requests.get('http://localhost:5000/api/summary')
print(response.json())

# Filter data
response = requests.post('http://localhost:5000/api/filter',
                        json={'classification': 'Disputable'})
print(response.json())
```

---

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (e.g., Gunicorn):

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```

2. **Set environment variables**:

   ```bash
   export FLASK_ENV=production
   ```

3. **Configure CORS properly** for your production domain

4. **Add authentication** if needed

5. **Set up proper logging and monitoring**

---

## Notes

- The default Excel file must have sheets named: `AmzaonPO`, `CustomSalesOrderRegisterM`, `Mapping`, and `Control`
- Uploaded files are stored in the `uploads/` directory with timestamps
- Maximum file upload size is 16MB
- All numeric values are returned as floats for JSON compatibility
- Dates are converted to ISO format strings
