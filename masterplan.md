# Masterplan: ArtSense AI Engine
**Version 2.1**
**Focus:** AI/ML-centric with a Web Visualization Layer
**Last Updated:** July 25, 2025

## 1. Project Overview & Philosophy

ArtSense AI is an advanced machine learning engine designed to understand and analyze fine art paintings. The primary goal is to develop and train a suite of sophisticated models capable of artist identification, style classification, and digital forgery detection.

The project's philosophy is **AI-first**. The web application component, while visually polished, serves as the interactive "lab" or "theater" to demonstrate the power and transparency of the core AI engine. Success is measured by the accuracy, insight, and explainability of the models.

## 2. Core AI/ML Engine Strategy

This is the heart of the project. The engine consists of three distinct modeling components, fueled by a unique, custom-curated dataset.

### 2.1. Data Acquisition & Curation

A high-quality, bespoke dataset is the foundation of the engine.
* **Primary Sources:** Programmatic scraping of high-resolution images from **WikiArt.org** and **Google Arts & Culture**.
* **Specialized Sources:** Inclusion of works from **The Metropolitan Museum of Art's collection** and a curated set of prominent **Indian artists** (e.g., Raja Ravi Varma, Amrita Sher-Gil) to create a unique data signature.
* **Process:** A Python script using **Playwright** will automate a web browser to navigate these dynamic, JavaScript-heavy sites. This modern approach is more robust than static scrapers and ensures high-quality data collection. The script will download images and associated metadata (Artist, Title, Style, Period) into a structured format.

### 2.2. Forgery Dataset Synthesis (The Core Innovation)

This is the project's key technical differentiator, moving beyond simple classification.
* **Method A (Baseline):** Collect and label images of known historical forgeries (e.g., works by Han van Meegeren) to learn macro-level stylistic inconsistencies.
* **Method B (Advanced Digital Forgery):** Employ a pre-trained **Generative Adversarial Network (GAN)**, such as StyleGAN, to create a large dataset of "digital forgeries." This process involves feeding the GAN real artworks to produce new, stylistically similar but digitally distinct images. This dataset is crucial for training a model to detect the subtle artifacts, patterns, and tells of AI-generated or digitally manipulated art.

### 2.3. AI Model Architecture

The engine is composed of three specialized models working in concert.

* **Model 1: Artist & Period Classifier**
    * **Strategy:** **Transfer Learning**. This is the industry-standard approach for achieving high performance with maximum efficiency.
    * **Architecture:** We will use a **pre-trained Vision Transformer (ViT)** model (e.g., one initially trained on the ImageNet dataset). This model already possesses a deep understanding of general visual concepts. We will then **fine-tune** this model on our specific art dataset, teaching it the specialized task of classifying artists and periods.
    * **Function:** This will be a multi-output model. A single input image will yield two parallel outputs: a prediction for the artist and a prediction for the creative period/style.

* **Model 2: Forgery Detector**
    * **Architecture:** A lightweight, specialized **Convolutional Neural Network (CNN)**.
    * **Function:** This is a binary classifier trained on the "Forgery Dataset." Its sole purpose is to output a probability score of whether an image is "Authentic" (from the real dataset) or a "Forgery" (from the synthesized dataset).

* **Model 3: Explainable AI (XAI) for Visualization**
    * **Technique:** **Grad-CAM (Gradient-weighted Class Activation Mapping)**.
    * **Function:** This is a crucial diagnostic tool. After the Artist Classifier makes its prediction, Grad-CAM is used to produce a heatmap. This map visually highlights which pixels in the input image were most influential in the model's decision, providing transparency into the "why."

## 3. AI Visualization & Serving Layer

This layer serves one purpose: to provide a clean, intuitive interface for users to interact with the AI Engine and view its results.

* **Architecture:** A "headless" AI engine with a web-based demonstration client. The Python AI logic is kept entirely separate from the web server, communicating via a well-defined internal API. This ensures modularity and mimics a production-grade microservice architecture.
* **Backend (API Server):** **FastAPI (Python)**. Its only job is to provide a REST API endpoint that accepts an image, passes it to the AI Engine for analysis, and returns the resulting JSON report.
* **Frontend (Demonstration Client):** **React**. A single-page application built to realize the "Digital Curator's Desk" concept, providing the UI for uploading images and rendering the analysis from the API.

## 4. Conceptual Data Contract (API Response)

The AI Engine will return the following standardized JSON object. This clean "report" is the contract that decouples the engine from the visualization layer.

```json
{
  "engine_metadata": {
    "model_versions": { "classifier": "ViT_v1.2", "forgery_detector": "CNN_v1.4" },
    "analysis_timestamp": "2025-07-25T12:38:20Z"
  },
  "predictions": {
    "artist": { "name": "Vincent van Gogh", "confidence": 0.92 },
    "period": { "name": "Post-Impressionism", "confidence": 0.88 },
    "authenticity": { "forgery_likelihood": 0.15 }
  },
  "explainability_data": {
    "heatmap_url": "/temp/heatmap_123.jpg" 
  }
}
5. Development Phases (AI-Centric)
Phase 1: Data Curation & Prototyping. The entire focus is on data. Scraping with Playwright, cleaning data, and setting up the GAN pipeline to generate the initial forgery dataset.

Phase 2: Core Engine Development. Training, validating, and fine-tuning the pre-trained ViT and the CNN Forgery Detector. Implementing the Grad-CAM logic. Finalizing the standard JSON output.

Phase 3: Visualization & Integration. Building the lightweight FastAPI server and the React UI. Integrating the two to create the final, demonstrable product.

6. User Experience: "The Digital Curator's Desk"
The UI will follow the detailed concept provided, with the goal of creating a professional and engaging showcase for the AI. Key elements include the engaging loader, the two-column report, and the interactive heatmap toggle, all designed to highlight the engine's capabilities.
