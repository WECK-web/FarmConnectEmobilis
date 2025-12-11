# Farm Connect 🚜🍃

**Directly connecting local farmers with consumers to promote fresh, sustainable agriculture.**

Farm Connect is a Django-based web application designed to address **SDG 2 (Zero Hunger)** by reducing food wastage and improving market access for small-scale farmers. It provides a seamless platform for farmers to list their produce and for consumers to buy fresh, local goods directly.

## 🚀 Key Features

### 👨‍🌾 For Farmers (Sellers)
- **Dashboard**: specialized analytics showing total listings, sales logs, and revenue.
- **Inventory Management**: Create, edit, and delete produce listings (with images, prices, and stock units).
- **Order Tracking**: View incoming orders and their status.
- **Direct Messaging**: Receive inquiries directly from potential buyers.

### 🛒 For Consumers (Buyers)
- **Fresh Marketplace**: Browse and search listings by category (Vegetables, Fruits, Grains, etc.).
- **Smart Cart**: Add items to cart with real-time stock validation (prevents over-ordering).
- **Checkout System**: Secure checkout process that automatically updates inventory.
- **Order History**: Track past purchases and view order status.

### 🔐 Security & UX
- **Role-Based Access**: Strict separation between Farmers and Consumers (e.g., Farmers cannot buy their own goods).
- **Secure Authentication**: Robust login/register system with profile management.
- **Modern UI**: Fully responsive design using **Bootstrap 5**, featuring a Hero section, modern cards, and dynamic interactions.

## 🛠️ Technology Stack
- **Backend**: Python, Django 5
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (Dev)
- **Version Control**: Git & GitHub

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/WECK-web/FarmConnectEmobilis.git
   cd FarmConnectEmobilis
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` in your browser.

## 🤝 Contribution
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
*Built with ❤️ for a greener future.*
