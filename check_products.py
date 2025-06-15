import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_products():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="ecom_prod_catalog",
            user="vikas",
            password="kalika1667",
            port="5432"
        )
        cursor = connection.cursor()
        # Count total products
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        logger.info(f"Total products in table: {count}")
        
        # Fetch distinct main categories
        cursor.execute("SELECT DISTINCT Main_Category FROM products WHERE Main_Category IS NOT NULL")
        main_categories = [row[0] for row in cursor.fetchall()]
        logger.info(f"Main Categories: {main_categories}")
        
        # Fetch distinct subcategories
        cursor.execute("SELECT DISTINCT Sub_Categories FROM products WHERE Sub_Categories IS NOT NULL")
        sub_categories = [row[0] for row in cursor.fetchall()]
        logger.info(f"Sub Categories: {sub_categories}")
        
        # Sample product data
        cursor.execute("SELECT Item_id, Main_Category, Sub_Categories, Product_Title, Price FROM products LIMIT 5")
        products = cursor.fetchall()
        logger.info("Sample Products:")
        for product in products:
            logger.info(product)
            
    except Exception as e:
        logger.error(f"Error checking products: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    check_products()