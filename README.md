# Farm Connect 🚜🍃

**Directly connecting local farmers with consumers to promote fresh, sustainable agriculture.**

Farm Connect is a Django-based web application designed to address **SDG 2 (Zero Hunger)** by reducing food wastage and improving market access for small-scale farmers. It provides a seamless platform for farmers to list their produce, for consumers to buy fresh local goods directly, and for administrators to ensure a safe and fair marketplace.

![FarmConnect Dashboard](https://images.unsplash.com/photo-1464226184884-fa280b87c399?q=80&w=1470&auto=format&fit=crop)

## 🚀 Key Features

### 👨‍🌾 For Farmers (Sellers)
- **Advanced Dashboard**: Visual analytics using **Chart.js** showing revenue trends, top products, and order status distribution.
- **Inventory Management**: Create, edit, and delete produce listings with images and stock tracking.
- **Order Management**: Process incoming orders with status updates (Pending -> Confirmed -> Shipped -> Delivered).
- **Profile Customization**: Set farm location and details.

### 🛒 For Consumers (Buyers)
- **Fresh Marketplace**: Smart search and filtering by category (Vegetables, Fruits, Grains, etc.).
- **Smart Cart**: Real-time stock validation to prevent over-ordering.
- **Wishlist**: Save favorite items for later.
- **Order Tracking**: Timeline view of order progress with status updates.

### 🛡️ For Administrators (Moderation)
- **User Management**: Tools to **Ban**, **Warn**, and **Unban** users violating platform policies.
- **Automated Notifications**: System automatically notifies users of account status changes or warnings.
- **Content Moderation**: Review and manage listings and user reports.

## 🔌 Integrations

Farm Connect leverages several powerful integrations to deliver a robust experience:

- **M-Pesa (Daraja API)**: Simulated payment gateway for secure mobile money transactions.
- **Chart.js**: Interactive data visualization for farmer analytics and dashboards.
- **Leaflet.js**: Geospatial mapping for farm locations.
- **Bootstrap 5**: Responsive, modern UI components and layout.
- **Bootstrap Icons**: Comprehensive icon library for visual cues.

## 🛠️ Technology Stack
- **Backend**: Python 3.10+, Django 5.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (Development)
- **Version Control**: Git & GitHub

## 🔐 Environment Variables

To run this project securely, you must configure the following environment variables.
Create a `.env` file in the root directory and add the following:

```env
# Django Security
SECRET_KEY=your_secret_key_here
DEBUG=True

# M-Pesa Configuration (Daraja API)
MPESA_CONSUMER_KEY=your_mpesa_consumer_key
MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
MPESA_PASSKEY=your_mpesa_passkey
MPESA_SHORTCODE=174379
MPESA_BASE_URL=https://sandbox.safaricom.co.ke
MPESA_CALLBACK_URL=https://your-domain.com/api/mpesa/callback/

# Optional: Cloudinary (if used for media)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/WECK-web/FarmConnectEmobilis.git
   cd FarmConnectEmobilis
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   - Create a `.env` file as described above.
   - Update `settings.py` to use `python-decouple` or `os.environ` for keys (Recommended).

5. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   - Main App: `http://127.0.0.1:8000/`
   - Admin Portal: `http://127.0.0.1:8000/portal/users/` (Login required)

## 🧪 Testing

Run duplicate verification scripts to ensure core logic is working:

```bash
# Verify Ban/Warn logic
python verify_ban.py

# Verify Checkout flow
python verify_checkout.py
```

## 🤝 Contribution
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
*Built with ❤️ for a greener future.*
