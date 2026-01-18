# Photo Upload Feature Setup Guide

## Azure Blob Storage Configuration

### Prerequisites
- Azure Storage Account created
- Connection string available

### Setup Steps

#### 1. Get Azure Storage Connection String

1. Navigate to Azure Portal (portal.azure.com)
2. Go to your Storage Account
3. Select "Access keys" from the left menu
4. Copy the "Connection string" value

#### 2. Configure Backend Environment

Edit `/backend-app/.env` file:

```env
# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_account_name;AccountKey=your_account_key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=financial-photos
```

**Note**: The container `financial-photos` will be created automatically if it doesn't exist.

#### 3. Install Backend Dependencies

```bash
cd backend-app
pip install -r requirements.txt
```

New dependencies added:
- `azure-storage-blob==12.19.0` - Azure Blob Storage SDK
- `python-multipart==0.0.6` - File upload support for FastAPI

#### 4. Restart Services

```bash
cd backend-app
docker-compose down
docker-compose up -d --build
```

## Feature Details

### File Upload Constraints
- **Maximum file size**: 10MB
- **Allowed formats**: JPG, JPEG, PNG, GIF, WebP
- **Storage naming**: `{item_id}_{timestamp}.{ext}`
- **Container**: Single container (`financial-photos`) for all photos
- **Access**: Public blob access (photos accessible via URL)

### API Changes

#### POST /items/ (Updated)
- Now accepts `multipart/form-data` instead of JSON
- New optional field: `photo` (file upload)
- All other fields sent as form data

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/items/" \
  -F "name=Grocery Shopping" \
  -F "description=Weekly groceries" \
  -F "category=food" \
  -F "record_type=expense" \
  -F "sum=150.75" \
  -F "photo=@/path/to/receipt.jpg"
```

#### Response Schema (Updated)
```json
{
  "id": 1,
  "name": "Grocery Shopping",
  "description": "Weekly groceries",
  "category": "food",
  "record_type": "expense",
  "sum": "150.75",
  "photo_url": "https://youraccountion.blob.core.windows.net/financial-photos/1_20260111123045.jpg",
  "created_at": "2026-01-11T12:30:45Z",
  "updated_at": "2026-01-11T12:30:45Z"
}
```

### Frontend Changes

#### Create Form
- Added file input for photo upload
- Client-side preview before submission
- File validation (size, format)
- Form encoding changed to `multipart/form-data`

#### Records List
- New "Photo" column in table
- Photo icon with "View" link for records with photos
- Opens full-size image in new browser tab
- "-" displayed for records without photos

## Troubleshooting

### Backend Connection Error
**Error**: `AZURE_STORAGE_CONNECTION_STRING environment variable is not set`

**Solution**: Ensure `.env` file is present in `backend-app/` with correct Azure connection string

### Container Creation Failed
**Error**: `Failed to ensure container exists`

**Solution**: Verify Azure Storage Account permissions and connection string validity

### File Upload Fails
**Errors**: 
- `File size exceeds maximum limit of 10MB`
- `Invalid file type`

**Solution**: Check file meets requirements (max 10MB, JPG/PNG/GIF/WebP format)

### Photo URL Not Working
**Issue**: Photo URL returns 404 or access denied

**Solution**: 
1. Verify container has public blob access
2. Check Azure Storage firewall settings
3. Ensure blob was uploaded successfully

### Docker Container Issues

If containers fail to start after adding Azure features:

```bash
# Rebuild images
cd backend-app
docker-compose build --no-cache

# Restart services
docker-compose up -d

# Check logs
docker-compose logs -f api
docker-compose logs -f frontend
```

## Security Considerations

### Production Recommendations

1. **Connection String Security**
   - Never commit `.env` file to version control
   - Use Azure Key Vault for production secrets
   - Consider Managed Identity for Azure-hosted apps

2. **Container Access**
   - Current: Public blob access (anyone with URL can view)
   - Consider: Private containers with SAS tokens for sensitive data

3. **File Validation**
   - Content type validation implemented
   - File extension validation implemented
   - Consider: Virus scanning for uploaded files

4. **Storage Costs**
   - Monitor blob storage usage
   - Implement lifecycle policies for old files
   - Consider: Thumbnail generation for reduced bandwidth

## Testing the Feature

### 1. Test Backend API

```bash
# Create record with photo
curl -X POST "http://localhost:8000/items/" \
  -F "name=Test Record" \
  -F "record_type=expense" \
  -F "sum=100.00" \
  -F "photo=@test_image.jpg"

# Verify response includes photo_url
```

### 2. Test Frontend

1. Navigate to http://localhost:8001/create
2. Fill in required fields
3. Click "Choose File" and select an image
4. Verify preview appears
5. Submit form
6. Check records list for photo icon
7. Click "View" link to open full-size photo

## Database Migration

If you have existing records in the database, the `photo_url` column will be added automatically on application startup (SQLAlchemy auto-creates tables).

For production with existing data, consider using Alembic migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "Add photo_url to items"

# Apply migration
alembic upgrade head
```

## Azure Costs

Photo storage costs depend on:
- **Storage**: ~$0.02 per GB per month (Hot tier)
- **Operations**: Minimal cost for upload/read operations
- **Bandwidth**: Egress charges for data transfer out of Azure

Estimate: 1000 photos (2MB average) = ~$0.04/month

## Support

For issues related to:
- **Azure Blob Storage**: Check Azure Portal diagnostics
- **File Uploads**: Review FastAPI logs
- **Frontend Display**: Check browser console for errors
