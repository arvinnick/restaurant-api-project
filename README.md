# Restaurant API Project

A Django REST Framework-based API for managing restaurant menus, orders, and user roles. This project provides a complete backend solution for restaurant order management with role-based access control.

## Features

- **Menu Management**: Browse and manage restaurant menu items organized by categories
- **User Authentication**: Secure user registration and authentication with role-based access
- **Shopping Cart**: Add menu items to a cart with quantity management
- **Order Management**: Create, view, and track orders with delivery crew assignment
- **Role-Based Access Control**: 
  - **Customers**: Browse menu, manage cart, create and view their orders
  - **Managers**: Full menu management, order administration, staff assignment
  - **Delivery Crew**: View assigned orders and update delivery status

## Project Structure

```
restaurant-api-project/
├── mainAPI/                 # Main API application
│   ├── models.py           # Database models (Category, MenuItem, Cart, Order, OrderItem)
│   ├── views.py            # API views and endpoints
│   ├── serializers.py      # DRF serializers for data validation and transformation
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin configuration
│   └── migrations/         # Database migrations
├── restaurantAPI/          # Django project configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Pipfile                # Pipenv configuration
└── db.sqlite3             # SQLite database
```

## Core Models

### Category
- `id`: Integer primary key
- `slug`: URL-friendly slug
- `title`: Category name (indexed)

### MenuItem
- `title`: Item name (indexed)
- `price`: Item price (indexed)
- `featured`: Boolean flag for featured items (indexed)
- `category`: Foreign key to Category

### Cart
- `user`: Foreign key to User
- `menuitem`: Foreign key to MenuItem
- `quantity`: Item quantity
- `unit_price`: Price per unit
- `price`: Total price for this cart item
- **Constraint**: Unique combination of user and menuitem

### Order
- `user`: Foreign key to User
- `delivery_crew`: Foreign key to User (nullable, for delivery assignment)
- `status`: Order status (pending/completed)
- `total`: Order total amount
- `date`: Order date (indexed)

### OrderItem
- `order`: Foreign key to Order
- `menuItem`: Foreign key to MenuItem
- `quantity`: Item quantity
- `unit_price`: Price per unit
- `price`: Total price for this order item
- **Constraint**: Unique combination of order and menuItem

## API Endpoints

### Menu Items
- `GET /api/menuitems` - List all menu items
- `POST /api/menuitems` - Create new menu item (Manager only)
- `GET /api/menuitems/{id}` - Get specific menu item
- `PUT /api/menuitems/{id}` - Update menu item (Manager only)
- `DELETE /api/menuitems/{id}` - Delete menu item (Manager only)

### User Management
- `POST /api/users` - User registration
- `GET /api/users/me` - Get current user info
- `GET /api/groups/{group}/users` - List users in group (Manager only)
- `POST /api/groups/{group}/users` - Add user to group (Manager only)
- `DELETE /api/groups/{group}/users/{user_id}` - Remove user from group (Manager only)

### Cart
- `GET /api/cart` - View current user's cart
- `POST /api/cart` - Add item to cart
- `DELETE /api/cart` - Clear entire cart

### Orders
- `GET /api/orders` - Get user's orders
- `POST /api/orders` - Create order from cart (Customer only)
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}` - Add item to order (Customer only)
- `PATCH /api/orders/{id}` - Update order (varies by role)
- `DELETE /api/orders/{id}` - Delete order (Manager only)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/arvinnick/restaurant-api-project.git
cd restaurant-api-project
```

2. Install dependencies using pip:
```bash
pip install -r requirements.txt
```

Or using pipenv:
```bash
pipenv install
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Start the development server:
```bash
python manage.py runserver
```

## Dependencies

- **Django** (~5.0.6) - Web framework
- **Django REST Framework** (~3.15.2) - REST API toolkit
- **djangorestframework-simplejwt** (~5.2.1) - JWT authentication
- **djoser** - User authentication endpoints
- **django-debug-toolbar** (~4.4.2) - Debugging toolbar

## Usage

### Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

### Example Workflow

1. **Register as a customer**:
   ```json
   POST /api/users/
   {
     "username": "john_doe",
     "password": "secure_password"
   }
   ```

2. **View menu items**:
   ```
   GET /api/menuitems/
   ```

3. **Add items to cart**:
   ```json
   POST /api/cart/
   {
     "title": "Burger",
     "quantity": 2
   }
   ```

4. **Create an order**:
   ```
   POST /api/orders/
   ```

## Development

The project uses SQLite for development and includes the Django Debug Toolbar for easier debugging during development.

## License

This project is open source and available under the MIT License.

## Author

Created by arvinnick
