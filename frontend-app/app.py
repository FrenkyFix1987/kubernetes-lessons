"""Flask web application for financial tracking."""
import os
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Backend API configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
API_ITEMS_URL = f"{BACKEND_URL}/items/"

# Categories and record types
CATEGORIES = ['food', 'car', 'rent']
RECORD_TYPES = ['income', 'expense']


@app.route('/')
def index():
    """Display list of financial records with filtering."""
    # Get filter parameters from query string
    category = request.args.get('category')
    record_type = request.args.get('record_type')
    
    # Build query parameters
    params = {}
    if category and category in CATEGORIES:
        params['category'] = category
    if record_type and record_type in RECORD_TYPES:
        params['record_type'] = record_type
    
    try:
        # Fetch items from backend API
        response = requests.get(API_ITEMS_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        items = data.get('items', [])
        total = data.get('total', 0)
        
        # Calculate totals
        total_income = sum(float(item['sum']) for item in items if item['record_type'] == 'income')
        total_expense = sum(float(item['sum']) for item in items if item['record_type'] == 'expense')
        balance = total_income - total_expense
        
        return render_template(
            'index.html',
            items=items,
            total_count=total,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            categories=CATEGORIES,
            record_types=RECORD_TYPES,
            selected_category=category,
            selected_record_type=record_type
        )
    except requests.exceptions.ConnectionError:
        flash('Error: Unable to connect to backend API. Please ensure the backend service is running.', 'error')
        return render_template(
            'index.html',
            items=[],
            total_count=0,
            total_income=0,
            total_expense=0,
            balance=0,
            categories=CATEGORIES,
            record_types=RECORD_TYPES,
            selected_category=category,
            selected_record_type=record_type
        )
    except requests.exceptions.Timeout:
        flash('Error: Backend API request timed out. Please try again later.', 'error')
        return render_template(
            'index.html',
            items=[],
            total_count=0,
            total_income=0,
            total_expense=0,
            balance=0,
            categories=CATEGORIES,
            record_types=RECORD_TYPES,
            selected_category=category,
            selected_record_type=record_type
        )
    except requests.exceptions.RequestException as e:
        flash(f'Error: Failed to fetch records from backend. {str(e)}', 'error')
        return render_template(
            'index.html',
            items=[],
            total_count=0,
            total_income=0,
            total_expense=0,
            balance=0,
            categories=CATEGORIES,
            record_types=RECORD_TYPES,
            selected_category=category,
            selected_record_type=record_type
        )


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new financial record."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category')
        record_type = request.form.get('record_type')
        sum_value = request.form.get('sum', '').strip()
        photo = request.files.get('photo')
        
        # Validate form data
        errors = []
        
        if not name:
            errors.append('Name is required.')
        elif len(name) > 255:
            errors.append('Name must not exceed 255 characters.')
        
        if not record_type or record_type not in RECORD_TYPES:
            errors.append('Valid record type (income/expense) is required.')
        
        if category and category not in CATEGORIES:
            errors.append('Invalid category selected.')
        
        if not sum_value:
            errors.append('Amount is required.')
        else:
            try:
                sum_decimal = Decimal(sum_value)
                if sum_decimal <= 0:
                    errors.append('Amount must be greater than zero.')
            except (InvalidOperation, ValueError):
                errors.append('Invalid amount format. Please enter a valid number.')
        
        # Validate photo if provided
        if photo and photo.filename:
            # Check file size (10MB limit)
            photo.seek(0, 2)  # Seek to end
            file_size = photo.tell()
            photo.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:
                errors.append('Photo size must not exceed 10MB.')
            
            # Check file extension
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            file_ext = os.path.splitext(photo.filename)[1].lower() # pHoTo.JpG
            if file_ext not in allowed_extensions:
                errors.append(f'Invalid photo format. Allowed: {", ".join(allowed_extensions)}')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'create.html',
                categories=CATEGORIES,
                record_types=RECORD_TYPES,
                form_data=request.form
            )
        
        # Prepare multipart form data for API
        form_data = {
            'name': name,
            'record_type': record_type,
            'sum': sum_value
        }
        
        # Add optional fields
        if description:
            form_data['description'] = description
        if category:
            form_data['category'] = category
        
        files = {}
        if photo and photo.filename:
            # Reset file pointer and prepare for upload
            photo.seek(0)
            files['photo'] = (photo.filename, photo.stream, photo.content_type)
        
        try:
            # Send POST request with multipart/form-data
            response = requests.post(
                API_ITEMS_URL, 
                data=form_data,
                files=files if files else None,
                timeout=30  # Longer timeout for file uploads
            )
            response.raise_for_status()
            
            flash(f'Successfully created {record_type} record: {name}', 'success')
            return redirect(url_for('index'))
            
        except requests.exceptions.ConnectionError:
            flash('Error: Unable to connect to backend API. Please ensure the backend service is running.', 'error')
        except requests.exceptions.Timeout:
            flash('Error: Backend API request timed out. Please try again later.', 'error')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                # Validation error from backend
                try:
                    error_detail = e.response.json()
                    if 'detail' in error_detail:
                        if isinstance(error_detail['detail'], list):
                            for error in error_detail['detail']:
                                msg = error.get('msg', 'Validation error')
                                field = error.get('loc', [])[-1] if error.get('loc') else 'field'
                                flash(f'Validation error in {field}: {msg}', 'error')
                        else:
                            flash(f'Validation error: {error_detail["detail"]}', 'error')
                    else:
                        flash('Validation error from backend.', 'error')
                except:
                    flash('Validation error from backend.', 'error')
            else:
                flash(f'Error: Failed to create record. Status code: {e.response.status_code}', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error: Failed to create record. {str(e)}', 'error')
        
        return render_template(
            'create.html',
            categories=CATEGORIES,
            record_types=RECORD_TYPES,
            form_data=request.form
        )
    
    # GET request - show form
    return render_template(
        'create.html',
        categories=CATEGORIES,
        record_types=RECORD_TYPES,
        form_data={}   )


@app.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
