import boto3
import psycopg2
from botocore.exceptions import ClientError
import argparse
from urllib.parse import urlparse # Import urlparse for handling URLs

# AWS S3 configuration (replace with your credentials)
AWS_ACCESS_KEY_ID = 'AKIARQYYYCJW3DU4CXMU'
AWS_SECRET_ACCESS_KEY = 'wq0v+T7PhY2OwEn5D3JeRjS1TfCg8rc0MIyhOsnV'
BUCKET_NAME = 'kalika-ecom'
AWS_REGION = 'us-east-1'  # e.g., 'us-east-1'
S3_FOLDER = 'kalika-images/'
S3_BASE_URL = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{S3_FOLDER}"

# Database configuration (replace with your database details)
DB_HOST = 'localhost'
DB_NAME = 'ecom_prod_catalog'
DB_USER = 'vikas'
DB_PASSWORD = 'kalika1667'
DB_PORT = '5432'

def get_s3_images():
    """Fetch all image paths from the specified S3 bucket folder."""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_FOLDER)
        
        if 'Contents' not in response:
            print(f"No objects found in s3://{BUCKET_NAME}/{S3_FOLDER}")
            return []
        
        # Extract image names (removing the folder prefix)
        images = [obj['Key'].replace(S3_FOLDER, '') for obj in response['Contents'] if obj['Key'] != S3_FOLDER]
        return images
    except ClientError as e:
        print(f"Error accessing S3: {e}")
        return []

def get_db_products():
    """Fetch product details (name, description, image_url) from the products table."""
    products = []
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        # Assuming your products table has 'product_name', 'description', and 'image_url'
        cursor.execute("SELECT product_name, description, image_url FROM products")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            product_name, description, image_url = row
            full_image_path = None
            if image_url:
                # Construct the full S3 URL if the image_url is just a filename
                if not (image_url.startswith('http://') or image_url.startswith('https://') or image_url.startswith('s3://')):
                    full_image_path = S3_BASE_URL + image_url
                elif image_url.startswith('s3://'): # If it's an S3 URI, convert to HTTP URL
                    parsed = urlparse(image_url)
                    bucket = parsed.netloc
                    key = parsed.path.lstrip('/')
                    full_image_path = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{key}"
                else: # Assume it's already a full HTTP/HTTPS URL
                    full_image_path = image_url

            products.append({
                'product_name': product_name,
                'description': description,
                'image_url': full_image_path
            })
        return products
    except psycopg2.Error as e:
        print(f"Error accessing PostgreSQL: {e}")
        return []

def generate_product_html(products):
    """Generates an HTML string to display product details with images."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product Catalog</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
            .container { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
            .product-card {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            .product-card img {
                max-width: 100%;
                height: 200px; /* Fixed height for consistency */
                object-fit: contain; /* Ensures the whole image is visible */
                border-bottom: 1px solid #eee;
                margin-bottom: 10px;
                background-color: #f8f8f8; /* Light background for images */
            }
            .product-card h3 {
                margin-top: 0;
                color: #333;
            }
            .product-card p {
                font-size: 0.9em;
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>Our Products</h1>
        <div class="container">
    """

    for product in products:
        image_src = product['image_url'] if product['image_url'] else 'https://via.placeholder.com/200?text=No+Image'
        product_name = product['product_name'] if product['product_name'] else 'No Name'
        description = product['description'] if product['description'] else 'No description available.'

        html_content += f"""
            <div class="product-card">
                <img src="{image_src}" alt="{product_name}">
                <h3>{product_name}</h3>
                <p>{description}</p>
            </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """
    return html_content

def main():
    print("Fetching product details from PostgreSQL...")
    products = get_db_products()
    print(f"Found {len(products)} products in the database.")

    if products:
        print("Generating HTML report...")
        html_output = generate_product_html(products)
        output_filename = "product_catalog.html"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"HTML catalog generated successfully: {output_filename}")
        print(f"You can open '{output_filename}' in your web browser to view the catalog.")
    else:
        print("No products found to display.")

if __name__ == "__main_": # Changed to avoid immediate execution if you want to keep the original logic
    # This block is for your original image matching logic
    # To run the original matching logic, change this back to __main__
    # For now, we'll focus on the UI generation
    main() # Call the new main function

# If you want to keep your original matching logic, you can do this:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match S3 images with database image URLs or generate a product catalog.")
    parser.add_argument('--mode', type=str, choices=['match', 'ui'], default='ui',
                        help="Choose 'match' to compare S3 and DB images, or 'ui' to generate a product catalog HTML.")
    args = parser.parse_args()

    if args.mode == 'match':
        print("Fetching images from S3...")
        s3_images = get_s3_images()
        print(f"Found {len(s3_images)} images in S3 bucket.")

        # For matching, we still need raw image names from DB
        db_raw_image_urls = []
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            cursor = conn.cursor()
            cursor.execute("SELECT image_url FROM products")
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                url = row[0]
                if url:
                    if url.startswith('s3://'):
                        parsed = urlparse(url)
                        path = parsed.path.lstrip('/')
                        image_name = path.split('/')[-1]
                    else:
                        image_name = url.split('/')[-1]
                    db_raw_image_urls.append(image_name)
        except psycopg2.Error as e:
            print(f"Error accessing PostgreSQL for raw image URLs: {e}")
            db_raw_image_urls = []

        print(f"Found {len(db_raw_image_urls)} image URLs in database for matching.")

        print("\nMatching images...")
        matched, unmatched_s3, unmatched_db = match_images(s3_images, db_raw_image_urls)

        print("\n=== Matching Results ===")
        print(f"Matched images ({len(matched)}):")
        for img in matched:
            print(f"- {img}")

        print(f"\nImages in S3 but not in database ({len(unmatched_s3)}):")
        for img in unmatched_s3:
            print(f"- {img}")

        print(f"\nImages in database but not in S3 ({len(unmatched_db)}):")
        for img in unmatched_db:
            print(f"- {img}")
    elif args.mode == 'ui':
        main() # Call the UI generation main function

def match_images(s3_images, db_images):
    """Match S3 images with database image_urls."""
    matched = []
    unmatched_s3 = []
    unmatched_db = []

    # Convert lists to sets for faster comparison
    s3_set = set(s3_images)
    db_set = set(db_images)

    # Find matches and unmatched items
    matched = s3_set.intersection(db_set)
    unmatched_s3 = s3_set - db_set
    unmatched_db = db_set - s3_set

    return list(matched), list(unmatched_s3), list(unmatched_db)