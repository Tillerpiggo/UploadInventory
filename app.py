import pandas as pd
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/transform_csv', methods=['GET', 'POST'])
def transform_csv():
    # Load the CSV file from the request
    csv_file = request.files['file']
    df = pd.read_csv(csv_file)
    
    # Filter the rows
    df = df[(df['included'] == 'x') | (df['included'] == 'X')]
    
    # Remove unnecessary columns:
    dropped_columns = ['Entry Date', 'Sport', 'URL', 'COMPLETE ONLY IF PACKET OR REEL -->', 'COMPLETE ONLY IF HYBRID PACKET -->']
    for col in dropped_columns:
        if col in df.columns:
            df = df.drop(col, axis=1)
    
    # Rename corresponding columns:
    column_name_mapping = {
        # add id column
        'Brand': 'brand',
        'Model': 'model',
        'Type': 'type_id',
        'Packaging': 'storage_type',
        'Gauge': 'gauge_reel_packet',
        'Thickness': 'thickness_reel_packet',
        'Primary String Type': 'primary_string_type',
        'Primary String Brand': 'primary_string_brand',
        'Primary String Model': 'primary_string_model',
        'Primary String Gauge': 'primary_string_gauge',
        'Primary String Thickness': 'primary_string_thickness',
        'Secondary String Type': 'secondary_string_type',
        'Secondary String Brand': 'secondary_string_brand',
        'Secondary String Model': 'secondary_string_model',
        'Secondary String Gauge': 'secondary_string_gauge',
        'Secondary String Thickness': 'secondary_string_thickness'
        # add blank created_at and updated_at columns
    }
    
    df = df.rename(columns=column_name_mapping)
    
    # 1. Map the 'storage_type' column
    df['storage_type'] = df['storage_type'].map({
        'Hybrid Packet': 'Hybrid',
        'Reel': 'Reel/Packet',
        'Packet': 'Reel/Packet'
    }).fillna(df['storage_type'])
    
    # 2. Insert new columns 'reel_price', 'packet_price', and 'hybrid_price'
    df['reel_price'] = df.apply(lambda row: row['List Price'] if row['storage_type'] == 'Reel/Packet' else None, axis=1)
    df['packet_price'] = df.apply(lambda row: row['List Price'] if row['storage_type'] == 'Reel/Packet' else None, axis=1)
    df['hybrid_price'] = df.apply(lambda row: row['List Price'] if row['storage_type'] == 'Hybrid' else None, axis=1)
    
    # Add 'reel_stock', 'packet_stock', and 'hybrid_stock' columns
    df['reel_stock'] = df.apply(lambda row: 'yes' if row['storage_type'] == 'Reel/Packet' else None, axis=1)
    df['packet_stock'] = df.apply(lambda row: 'yes' if row['storage_type'] == 'Reel/Packet' else None,  axis=1)
    df['hybrid_stock'] = df.apply(lambda row: 'yes' if row['storage_type'] == 'Hybrid' else None, axis=1)
    
    if 'List Price' in df.columns:
        df = df.drop('List Price', axis=1)
    
    column_order = ['brand', 'model', 'type_id', 'storage_type', 'gauge_reel_packet', 'thickness_reel_packet', 'reel_price', 'packet_price', 'hybrid_price', 'reel_stock', 'packet_stock', 'hybrid_stock', 'primary_string_type', 'primary_string_brand', 'primary_string_model', 'primary_string_gauge', 'primary_string_thickness', 'secondary_string_type', 'secondary_string_brand', 'secondary_string_model', 'secondary_string_gauge', 'secondary_string_thickness']
    df = df[column_order]
    
    type_map = {
        'Polyester': 1,
        'Natural Gut': 2,
        'Multifilament': 3,
        'Ultranyl': 4,
        'Monofilament': 5,
        'Kevlar': 6,
        'Synthetic Gut': 7,
        'Undefined': 8,
        '': 8
    }
    def type_to_id(type):
        return type_map[type]
        
    df['type_id'] = df['type_id'].apply(type_to_id)
    
    # add ids
    df.insert(0, 'id', range(1, len(df) + 1))
    
    # Output the transformed CSV file
    output_csv = df.to_csv(index=False)
    response = make_response(output_csv)
    response.headers['Content-Disposition'] = 'attachment; filename=transformed.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

if __name__ == '__main__':
    app.run()
