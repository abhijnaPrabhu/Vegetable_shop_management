import sqlite3
from datetime import date, datetime


def get_connection():
    connection = sqlite3.connect('vegetable_shop.db')
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vegetables (
            vegetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            unit TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stock (
            stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vegetable_id INTEGER NOT NULL,
            stock_date TEXT NOT NULL,
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (vegetable_id)
            REFERENCES vegetables(vegetable_id),

            UNIQUE (vegetable_id, stock_date)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            vegetable_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            price REAL NOT NULL,
            subtotal REAL NOT NULL,

            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),

            FOREIGN KEY (vegetable_id)
                REFERENCES vegetables(vegetable_id)
        )
    ''')

    connection.commit()
    connection.close()


def add_vegetable(name,unit):

    connection=get_connection()
    cursor=connection.cursor()

    cursor.execute(
        '''
        INSERT INTO vegetables (name,unit) VALUES (?,?)
        ''',
        (name,unit)
    )
    connection.commit()
    connection.close()

def get_vegetables():

    connection=get_connection()
    cursor=connection.cursor()

    cursor.execute(
        '''
        SELECT vegetable_id, name,unit,active
        FROM vegetables
        ORDER BY name
        
        '''
    )

    vegetables=cursor.fetchall()
    connection.close()

    return vegetables

def update_vegetable(vegetable_id,name,unit):

    connection=get_connection()
    cursor=connection.cursor()

    cursor.execute(
        '''
        UPDATE vegetables
        SET name=?,unit=?
        WHERE vegetable_id=?
        ''',
        (name,unit,vegetable_id)
    )

    connection.commit()
    connection.close()

def set_vegetable_active(vegetable_id, active):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        '''
        UPDATE vegetables
        SET active = ?
        WHERE vegetable_id = ?
        ''',
        (active, vegetable_id)
    )

    connection.commit()
    connection.close()

def set_daily_stock(vegetable_id,price,available):

    connection=get_connection()
    cursor=connection.cursor()

    today=date.today().isoformat()

    cursor.execute(
        '''
         INSERT INTO daily_stock (
            vegetable_id,
            stock_date,
            price,
            available
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(vegetable_id, stock_date)
        DO UPDATE SET
            price = excluded.price,
            available = excluded.available

        ''',
        (
            vegetable_id,
            today,
            price,
            available
        )
    )

    connection.commit()
    connection.close()


def get_today_stock():

    connection = get_connection()
    cursor = connection.cursor()

    today = date.today().isoformat()

    cursor.execute(
        '''
        SELECT
            v.vegetable_id,
            v.name,
            v.unit,
            ds.price,
            ds.available
        FROM vegetables v

        LEFT JOIN daily_stock ds
        ON v.vegetable_id = ds.vegetable_id
        AND ds.stock_date = ?

        WHERE v.active = 1

        ORDER BY v.name
        ''',
        (today,)
    )

    rows = cursor.fetchall()

    connection.close()

    return rows

def get_available_vegetables_today():

    connection=get_connection()
    cursor=connection.cursor()

    today=date.today().isoformat()

    cursor.execute(
        '''
        SELECT 
            ds.stock_id,
            v.vegetable_id,
            v.name,
            v.unit,
            ds.price
        FROM daily_stock ds

        JOIN vegetables v
        ON ds.vegetable_id=v.vegetable_id

        WHERE ds.stock_date=?
        AND ds.available=1
        AND v.active=1

        ORDER BY v.name
        ''',
        (today,)
    )

    rows=cursor.fetchall()
    connection.close()
    return rows

def place_order(customer_name,cart):
    customer_name=customer_name.strip()

    if not customer_name:
        raise ValueError('Customer name is required')

    if not cart:
        raise ValueError('Cart cannot be empty')


    conn=get_connection()
    cursor=conn.cursor()

    try:
        total_amount=0
        order_items=[]

        for item in cart:
            stock_id=item['stock_id']
            quantity=float(item['quantity'])
            selected_unit=item['selected_unit']

            cursor.execute('''
                SELECT d.vegetable_id,d.price,v.unit
                FROM daily_stock AS d
                JOIN vegetables AS v
                    on d.vegetable_id =v.vegetable_id 
                WHERE d.stock_id=?
                    AND d.available=1
                    AND v.active=1

            ''',(stock_id,))

            stock=cursor.fetchone()

            if stock is None:
                raise ValueError("An item is no longer available")

            vegetable_id,price,base_unit=stock

            if base_unit in ('kg','grams'):
                if selected_unit=='kg':
                    if quantity<1:
                        raise ValueError('Minimum quantity is 500 grams')
                    quantity_in_kg=quantity

                elif selected_unit=='grams':
                    if quantity<500:
                        raise ValueError("Minimum quantity is 500 grams")
                    quantity_in_kg=quantity/1000

                else:
                    raise ValueError('Invalid weight unit')

                subtotal=price*quantity_in_kg

            else:
                raise ValueError('Unsupported vegetable unit')

            total_amount+=subtotal

            order_items.append((
                vegetable_id,
                quantity,
                selected_unit,
                price,
                round(subtotal,2)
            ))

            total_amount=round(total_amount,2)

            cursor.execute('''
                INSERT INTO orders
                 (customer_name,order_date, total_amount)
                VALUES(?,?,?)
            ''',(
                customer_name,
                datetime.now().isoformat(timespec="seconds"),
                total_amount
            ))

            order_id=cursor.lastrowid

            for vegetable_id ,quantity,unit,price,subtotal in order_items:
                cursor.execute('''
                    INSERT INTO order_items
                        (order_id,vegetable_id,quantity,unit,price,subtotal)
                    VALUES(?,?,?,?,?,?)
                ''',(
                    order_id,vegetable_id,quantity,unit,price,subtotal
                ))

            conn.commit()
            return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_orders():
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute('''
            SELECT 
                order_id,customer_name,order_date,total_amount,status
            FROM orders
            WHERE status IN ('Pending','Preparing')
            ORDER BY order_date ASC,order_id ASC
        ''')

        orders=cursor.fetchall()
        return orders
    
    finally:
        conn.close()

def get_order_items(order_id):
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute('''
            SELECT 
                v.name,oi.quantity,oi.unit,oi.price,oi.subtotal
            FROM order_items AS oi
            JOIN vegetables AS v
                ON oi.vegetable_id=v.vegetable_id
            WHERE oi.order_id=?
            ORDER BY oi.item_id ASC
        ''',(order_id,))

        return cursor.fetchall()

    finally:
        conn.close()

def update_order_status(order_id,new_status):
    allowed_statuses=('Preparing','Completed')

    if new_status not in allowed_statuses:
        raise ValueError('Invalid order status')

    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute('''
            UPDATE orders
            SET status=?
            WHERE order_id=?
                AND (
                    (status='Pending' AND ? = 'Preparing')
                    OR
                    (status='Preparing' AND ? = 'Completed')
                )
        ''',(new_status,order_id,new_status,new_status))

        if cursor.rowcount!=1:
            raise ValueError('Order not found or invalid status change')

        conn.commit()

    finally:
        conn.close()

def get_order_history():
    conn=get_connection()
    cursor=conn.cursor()

    try:
        cursor.execute('''
            SELECT 
                order_id,customer_name,order_date,total_amount,
                status
            FROM orders
            ORDER BY order_date DESC, order_id DESC
        ''')

        orders=cursor.fetchall()
        return orders

    finally:
        conn.close()



create_tables()