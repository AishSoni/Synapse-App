# 🧠 Synapse

[![GitHub top language](https://img.shields.io/github/languages/top/AishSoni/Synapse-App?style=flat-square)](#)
[![GitHub language count](https://img.shields.io/github/languages/count/AishSoni/Synapse-App?style=flat-square)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](#)

> A unified, multi-platform application designed to bridge your digital workflow across the web, desktop, and browser. 

Synapse acts as the connective tissue for your digital environment. Whether you are capturing data on the go via the browser extension, managing workflows in the desktop client, or syncing everything through the core web application, Synapse ensures a seamless, cross-platform experience.

---

## 🏗️ Repository Structure

This repository is organized into a monorepo structure containing all the clients and backend services required to run Synapse.

| Directory | Description |
| :--- | :--- |
| 📁 `synapse-app/` | The core web application and primary Python backend server. |
| 📁 `synapse-desktop/` | The desktop client application. |
| 📁 `synapse-extension/` | Source code for the core browser extension features. |
| 📁 `chrome-extension/` | Packaged manifest and build files tailored for Google Chrome. |

## 💻 Tech Stack

Synapse leverages a robust and modern technology stack designed for scalability and cross-platform compatibility:

- **Backend / Core Logic:** Python (58.8%) 
- **Frontend / Client UI:** JavaScript (21.0%), TypeScript (4.1%), HTML & CSS
- **Database:** PostgreSQL (PLpgSQL - 3.3%)

---

## ✨ Key Features

- **Cross-Platform Syncing:** Data flows seamlessly between your browser extension, desktop app, and web dashboard.
- **Persistent Storage:** Backed by a powerful PostgreSQL database to ensure your data is secure and reliably stored.
- **Quick Capture:** Use the Chrome extension to instantly funnel information into your Synapse ecosystem without switching contexts.
- **Desktop Integration:** A dedicated desktop environment for deep-focus tasks and local system integrations.

---

## 🚀 Getting Started

Follow these instructions to get a local copy of the Synapse ecosystem up and running.

### Prerequisites

Ensure you have the following installed on your local machine:
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js & npm](https://nodejs.org/en/download/) (for extension and frontend dependencies)
- [PostgreSQL](https://www.postgresql.org/download/)

### 1. Clone the Repository

```bash
git clone [https://github.com/AishSoni/Synapse-App.git](https://github.com/AishSoni/Synapse-App.git)
cd Synapse-App
```

### 2. Backend & Web App Setup (`synapse-app`)

```bash
cd synapse-app

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your environment variables
cp .env.example .env
# Edit .env to include your local PostgreSQL credentials

# Start the application
python main.py # or the respective start command
```

### 3. Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** on (top right corner).
3. Click **Load unpacked**.
4. Select the `chrome-extension/` directory from this repository.
5. The Synapse extension icon should now appear in your browser toolbar!

### 4. Desktop App Setup (`synapse-desktop`)

```bash
cd ../synapse-desktop

# Install desktop client dependencies
npm install

# Run the desktop application in development mode
npm start
```

---

## 📖 Documentation

For deeper dives into specific components, please refer to the markdown files included in the repository root:
- [Vision & Blueprint](vision.md) / [blueprint.md](blueprint.md)
- [System Architecture](SYSTEM_COMPLETE.md)
- [Backend Implementation](BACKEND_COMPLETE.md)
- [Setup & Quickstart](SETUP_GUIDE.md) / [QUICKSTART.md](QUICKSTART.md)
- [Development Plan & Todo](DEVELOPMENT_PLAN.md) / [TODO.md](TODO.md)

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make to Synapse are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with ❤️ by [AishSoni](https://github.com/AishSoni)*
```
