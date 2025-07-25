ArtSense AI - Detailed Execution Plan
Version 1.0
Objective: A linear, step-by-step guide for building the ArtSense AI project, including the workflow for training on Kaggle.

Phase 1: Project Setup & Data Acquisition
This phase is about laying the foundation. We'll set up our development environment and gather the raw materials (data) for our AI.

Step 1.1: Environment Setup

Goal: Create an isolated and reproducible development environment.

Actions:

Install Python 3.10 or newer.

Create a project directory: mkdir artsense_ai && cd artsense_ai

Create a Python virtual environment: python -m venv venv

Activate the environment: source venv/bin/activate (on macOS/Linux) or .\venv\Scripts\activate (on Windows).

Initialize a Git repository: git init

Step 1.2: Initial Directory Structure

Goal: Organize the project logically from the start.

Actions: Create the following folder structure inside artsense_ai/.

├── data/
│   ├── raw_art/
│   └── raw_forgeries/
├── notebooks/
├── scripts/
├── src/
└── README.md
Step 1.3: Data Scraping

Goal: Scrape a large dataset of artwork images and their metadata.

Tool: Playwright.

Script: Create scripts/scrape_art.py.

Workflow:

The script will take a target website (e.g., WikiArt's page for an artist) as input.

It will use Playwright to launch a browser, navigate to the page, and handle any dynamic content loading.

It will systematically extract links to high-resolution artwork images and their corresponding metadata (Artist, Title, Style, Period).

It will download each image into data/raw_art/ and append the metadata to a central metadata.csv file.

Crucially: Implement respectful scraping practices, such as adding delays between requests and checking the site's robots.txt.

Phase 2: Data Preprocessing & Pipeline Construction
Raw data is messy. This phase is about cleaning it and preparing it for our models.

Step 2.1: Image Standardization

Goal: Create a clean, uniformly sized dataset.

Script: Create scripts/preprocess_images.py.

Libraries: Pillow or OpenCV.

Workflow:

The script reads the metadata.csv.

For each image in data/raw_art/, it will perform resizing to a fixed dimension (e.g., 256x256 pixels) to create a uniform dataset.

The processed images will be saved to a new data/processed_art/ directory. This separates raw downloads from model-ready data.

Step 2.2: PyTorch/TensorFlow Dataset Class

Goal: Create an efficient data-loading pipeline for training.

Script: Create src/dataset.py.

Workflow:

Define a custom ArtDataset class that inherits from PyTorch's Dataset or uses TensorFlow's tf.data API.

The class constructor will load the metadata.csv and a list of processed image paths.

The __getitem__ method will:

Load a single processed image from disk.

Apply data augmentation transformations on-the-fly (e.g., random horizontal flips, slight rotations).

Apply model-specific transformations: convert the image to a tensor and normalize it using the standard ImageNet mean and standard deviation values.

This class will feed perfectly prepared data to the model during training.

Phase 3: Core AI Model Development & Training (on Kaggle)
This is the main event: building our neural networks using Kaggle's free GPU resources.

Step 3.1: Prepare Data for Kaggle

Goal: Package the local dataset for upload to Kaggle.

Workflow:

Compress the entire data/processed_art/ directory and the metadata.csv file into a single .zip archive.

On Kaggle, navigate to the "Datasets" section and create a new, private dataset.

Upload the .zip archive to this new dataset.

Step 3.2: The Training Notebook on Kaggle

Goal: Write and execute the training script within a Kaggle Notebook to leverage their free GPU.

Platform: Kaggle Notebooks (with GPU accelerator enabled).

Workflow:

Create a new Kaggle Notebook.

Attach your newly uploaded art dataset to the notebook. Kaggle will mount it, making the data accessible.

In the first cells, install any specific libraries needed: !pip install huggingface_hub transformers

In subsequent cells, define your ArtDataset class and your ArtClassifierModel class (the ViT model architecture from src/dataset.py and src/model.py).

Implement the training loop that loads data, trains the model for a number of epochs, and validates its performance.

After the loop completes, save the final, best-performing model weights to the notebook's output directory (e.g., /kaggle/working/art_classifier_v1.pth).

Step 3.3: Retrieve Trained Model

Goal: Download the trained model from Kaggle to your local machine.

Workflow:

After the notebook has finished running, go to the notebook's "Data" tab and find the "Output" section.

Download the saved model weights file (.pth).

Place this downloaded file into the models/ directory on your local project.

Step 3.4: Forgery Model Training

Goal: Train the separate forgery detection model.

Workflow: Repeat steps 3.1 through 3.3 for the simpler CNN model, using the GAN-generated and known forgeries dataset. Save the final weights as forgery_detector_v1.pth and download it to your local models/ folder.

Phase 4: Inference Engine & API Server
With trained models downloaded locally, we now build the engine to use them and expose it via an API.

Step 4.1: The Inference Function

Goal: Create a single, reusable function that produces a full analysis for one image.

Script: Create src/inference.py.

Workflow:

The function will accept a path to an input image.

It will load the saved model weights from your local models/ directory.

It will apply the exact same preprocessing (resize, normalize) but without data augmentation.

It will pass the image through the models to get predictions.

It will run the Grad-CAM algorithm on the classifier's output to generate the heatmap.

It will assemble all this information into the final AnalysisReport JSON object and return it.

Step 4.2: The API Server

Goal: Expose the inference function through a web API.

Script: Create src/main.py.

Framework: FastAPI.

Workflow:

Create a FastAPI app instance.

Define a single endpoint, e.g., POST /analyze.

This endpoint will accept an image file upload. It will save the file temporarily, call the main inference function, receive the JSON report, and return it to the client.

Phase 5: Frontend Client Development
The final phase is building the user interface to interact with our API.

Step 5.1: React App Setup

Goal: Initialize the frontend project.

Action: In the project root, run npx create-react-app frontend.

Libraries: Install Axios for making API calls.

Step 5.2: UI Component Implementation

Goal: Build the UI based on "The Digital Curator's Desk" design.

Workflow: Create a library of React components for the uploader, the results columns, the confidence bars, the gauge chart, and the heatmap display.

Step 5.3: API Integration

Goal: Connect the UI to the backend API.

Workflow:

Write the state management logic to handle the application's states (e.g., idle, loading, success, error).

On image upload, create a FormData object, use Axios to POST it to the http://127.0.0.1:8000/analyze endpoint.

While waiting for the response, display the engaging "Lab" loading state.

When the JSON response is received, update the state and render the results in the appropriate components.
