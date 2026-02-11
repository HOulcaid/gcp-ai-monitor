# 🚀 GCP AI Cost Monitor

A lightweight **serverless GCP monitoring dashboard** that lists Compute Engine VM instances and provides **AI-powered cost optimization recommendations** using **Vertex AI Gemini**.

Built to be:
- 🔐 **Unauthenticated (public HTTP endpoint)**
- ⚡ **Serverless (Cloud Functions Gen2)**
- 🧠 **AI-assisted (Gemini)**
- 🛠️ **Easy to deploy with a single shell script**

---

## 🖼️ The Architecture

### Project Structure
![Project Structure](media/tree.png)

### Architecture Diagram
![Architecture Diagram](media/architecture.png)

---

## 📸 Application Screenshots

### Project Summary & VM Inventory and AI Cost Optimization Recommendations
![VM Summary](media/interface.png)

---

## 🧩 How It Works

1. User deploys the app using `deploy.sh`
2. A **Cloud Function (Python 3.11)** is deployed
3. The function:
   - Reads VM metadata via **Compute Engine API**
   - Renders an HTML dashboard
   - Sends VM data to **Vertex AI Gemini**
4. Gemini returns **cost optimization suggestions**
5. Everything is displayed in a clean web UI

---

## 🛠️ Tech Stack

- **Google Cloud Functions (Gen2)**
- **Python 3.11**

### Prerequisites

- GCP project
- `gcloud` CLI installed and authenticated

All required Google Cloud services and IAM permissions are automatically set up by the deployment script.

---
## 🚀 Deployment (1 command)

### Deploy

You can deploy the app using the provided script:
```bash
chmod +x deploy.sh
./deploy.sh
```