# 🏫 Campus Mart

**Campus Mart** is a university-exclusive online marketplace that enables students, faculty, and campus staff to **buy, sell, rent, and exchange services** within their academic community.

The platform is designed around the unique needs of campus life, providing a **localized, trusted, and convenient marketplace** for second-hand goods, academic resources, electronics, dorm essentials, and peer-to-peer services.

---

## 🚀 Why Campus Mart?

General marketplaces are designed for large public communities, which can make transactions between students inconvenient and less trustworthy.

Campus Mart focuses specifically on university communities by:

* 🔐 Restricting access to verified institutional users
* 🏫 Keeping transactions within the campus community
* 📚 Providing categories relevant to student life
* 💬 Enabling direct communication between buyers and sellers
* 📍 Supporting convenient on-campus exchanges
* 💡 Allowing students to offer skills and services to their peers

---

## ✨ Key Features

### 🛍️ Peer-to-Peer Marketplace

Users can create listings and buy, sell, or rent items such as:

* 📚 Textbooks and academic resources
* 🔬 Lab equipment
* 💻 Laptops and electronics
* 🪑 Dormitory essentials
* 🚲 Vehicle and bike accessories
* 🎒 Other campus-related items

---

### 🔐 Campus-Only Verification

Campus Mart is designed to maintain a trusted campus environment through institutional verification.

Users can register using:

* University-issued email addresses
* Official institutional authentication
* Email verification workflows

This helps ensure that marketplace participants belong to the relevant university community.

---

### 🎓 Student Services & Skill Exchange

Campus Mart is not limited to physical products.

Students can also offer services and skills such as:

* 📖 Peer tutoring
* 💻 Programming assistance
* 🎨 Graphic design
* 🛠️ Device and technical setup
* 🔧 Repair services
* 🎥 Photography and editing
* ✍️ Freelance work

> Services should comply with university policies and applicable academic-integrity rules.

---

### 🔎 Category Filtering & Search

Listings can be organized into categories such as:

| Category               | Examples                                   |
| ---------------------- | ------------------------------------------ |
| 📚 Academic Resources  | Textbooks, notes, calculators              |
| 💻 Electronics         | Laptops, monitors, accessories             |
| 🏠 Dorm Goods          | Furniture, appliances, storage             |
| 🚗 Vehicle Accessories | Helmets, bike accessories, car accessories |
| 🧑‍💻 Skill Services   | Tutoring, design, programming, repairs     |

Users can search and filter listings based on category, price, availability, and other relevant attributes.

---

### 💬 In-App Messaging

An integrated messaging system allows users to communicate directly.

Buyers and sellers can:

* Ask questions about listings
* Negotiate prices
* Confirm availability
* Discuss rental details
* Coordinate pickup locations
* Finalize transaction arrangements

---

### 📍 Safe Campus Transactions

Since the marketplace is designed around a university community, users can coordinate exchanges at mutually agreed **safe on-campus locations**.

Examples include:

* University libraries
* Student centers
* Designated common areas
* Other approved campus locations

---

## 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      Frontend       │
                         │ HTML / CSS / JS     │
                         │ React / Vue /       │
                         │ Tailwind CSS        │
                         └──────────┬──────────┘
                                    │
                                    │ REST API / WebSocket
                                    ▼
                         ┌─────────────────────┐
                         │       Backend       │
                         │ Node.js / FastAPI / │
                         │ Django              │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
             │ PostgreSQL/ │ │     Auth    │ │  Messaging  │
             │  MongoDB    │ │ JWT + Email │ │ WebSockets  │
             └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🧑‍💻 Technology Stack

The project can be implemented using the following technologies:

### Frontend

* HTML5
* CSS3
* Tailwind CSS
* JavaScript
* React.js or Vue.js

The frontend is designed to be responsive and accessible on both **desktop and mobile devices**.

### Backend

Possible backend implementations include:

* Node.js
* Python
* FastAPI
* Django

The backend provides APIs for authentication, listings, search, user profiles, and communication.

### Database

Possible database technologies:

* PostgreSQL
* MongoDB

The database stores information such as:

* User profiles
* Listings
* Categories
* Item information
* Rental details
* Conversations
* Messages

### Authentication & Security

Security mechanisms may include:

* JWT-based authentication
* Institutional email verification
* Password hashing
* Input validation
* Input sanitization
* Authorization middleware
* Secure API endpoints

---

## 📂 Example Project Structure

```text
campus-mart/
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── assets/
│   └── ...
│
├── backend/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── middleware/
│   ├── services/
│   └── ...
│
├── database/
│   ├── migrations/
│   └── seed/
│
├── README.md
├── .env.example
└── ...
```

---

## 🔄 Typical User Flow

```text
Register
   │
   ▼
Verify Institutional Email
   │
   ▼
Create / Complete Profile
   │
   ▼
Browse Marketplace
   │
   ├───────────────┐
   ▼               ▼
Buy / Rent     Sell / List
   │               │
   └───────┬───────┘
           ▼
     Start Chat
           │
           ▼
Negotiate / Confirm
           │
           ▼
Campus Pickup / Service
```

---

## 📋 Core Modules

### 1. User Management

Handles:

* Registration
* Login
* Email verification
* User profiles
* Authentication
* Authorization

### 2. Marketplace Listings

Users can:

* Create listings
* Upload item images
* Set prices
* Specify item condition
* Edit listings
* Remove listings
* Mark items as sold or rented

### 3. Search & Filtering

Users can find relevant listings using:

* Keyword search
* Category filtering
* Price range
* Listing type
* Availability

### 4. Messaging

Provides communication between marketplace users through:

* One-to-one conversations
* Real-time messages
* Listing-specific communication
* Transaction coordination

### 5. Services Marketplace

Allows students to advertise skills and services while keeping them within the campus marketplace.

---

## 🔒 Security Considerations

Campus Mart is designed with security and user privacy in mind.

Important security measures include:

* Institutional email verification
* Secure password storage
* JWT authentication
* Role-based authorization
* Server-side input validation
* Input sanitization
* Protection against unauthorized API access
* Rate limiting for sensitive endpoints
* Secure handling of user-generated content

Sensitive information should not be exposed through public listing pages or APIs.

---

## 🌟 Future Enhancements

Possible future improvements include:

* ⭐ Ratings and reviews
* ❤️ Wishlist and favorites
* 🔔 Notifications
* 📱 Progressive Web App (PWA)
* 🖼️ AI-powered image classification
* 🤖 AI-assisted listing descriptions
* 🔍 Semantic search
* 🧠 Personalized recommendations
* 💳 Optional payment integration
* 📍 Campus map integration
* 🚨 Report/block functionality
* 🛡️ Automated fraud and spam detection
* 📊 Admin dashboard and marketplace analytics

---

## 🎯 Project Goals

Campus Mart aims to create a **trusted digital marketplace for university communities** by combining:

**Campus Verification + Local Marketplace + Student Services + Communication**

The goal is to make it easier for students and campus members to reuse resources, discover affordable products, exchange skills, and conduct transactions within their university ecosystem.

---

## 🤝 Contributing

Contributions are welcome.

To contribute:

```bash
# Clone the repository
git clone <repository-url>

# Enter the project directory
cd campus-mart

# Create a new branch
git checkout -b feature/your-feature

# Make your changes
# Test your changes

# Commit
git add .
git commit -m "Add your feature"

# Push
git push origin feature/your-feature
```

Then open a Pull Request describing your changes.

---

## 👥 Contributors

* [@AdithyaND12](https://github.com/AdithyaND12) — Owner / Maintainer
* [@Apeksha-9683](https://github.com/Apeksha-9683) — Collaborator
* [@ankush-cloud3](https://github.com/ankush-cloud3) — Collaborator
* [@amrutashivakumarcs25-a11y](https://github.com/amrutashivakumarcs25-a11y) — Collaborator

---

## ⚙️ Environment Variables

Create a `.env` file for configuration values such as:

```env
DATABASE_URL=
JWT_SECRET=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USERNAME=
EMAIL_PASSWORD=
```

Never commit secrets, passwords, API keys, or production credentials to the repository.

---

## 📌 Disclaimer

Campus Mart is intended for use within university communities. Users should follow their institution's rules regarding marketplace transactions, services, academic integrity, safety, and acceptable use.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 💡 Vision

> **One campus. One trusted marketplace.**

Campus Mart aims to turn the university into a connected ecosystem where students can **buy what they need, sell what they no longer use, rent resources, and exchange skills with their peers.**
