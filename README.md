# Evaluating Vision Language Models for Ki-67 Index Prediction in Breast Cancer Histopathology Images

This project aims to evaluate the performance of Vision Language Models (VLMs) in calculating the Ki-67 index from histopathological images. This study uses the VLM from OpenAI and BCData database for this purpose.

---

## Project Structure

The project follows a step-by-step workflow, organized into logical directories.

---

## 0. Getting Started: Environment Setup

Before running the project, it's highly recommended to set up a dedicated Python virtual environment to manage dependencies and avoid conflicts with other projects.

### 0.1 Create and Activate Virtual Environment

Follow these steps to create and activate your virtual environment:

1.  **Navigate to the project root directory** in your terminal or command prompt.

2.  **Create the virtual environment** (e.g., named `venv`):

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    - **On Windows:**

    ```bash
    .\venv\Scripts\activate
    ```

    - **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

    You should see `(venv)` prepended to your command prompt, indicating that the virtual environment is active.

### 0.2 Configure your environment variables

1. **Create your personal `.env` file**
   
   Windows (PowerShell / Git Bash)
   ```bash
   cp .env.example .env
   ```

   Windows CMD
   ```bash
   copy .env.example .env
   ```

   macOS / Linux
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your OpenAI key**

   ```dotenv
   # .env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 0.3 Install Dependencies

With your virtual environment activated, install all necessary project dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## 1. Data Access

The first step is to download the BCData. The `1.data_access/` directory contains all the necessary information and scripts to understand the dataset's structure, how to download it, and a sample data. Please refer to the instructions within this folder to obtain the raw data.

---

## 2. Data Processing

The raw BCData requires pre-processing to be suitable for model training and evaluation. The `2.preprocess/` directory contains scripts to handle this. The data comes organized in `1.images` and `2.annotations` folders. The `2.annotations` folder further contains `positive/` and `negative/` subfolders for test data, each with `.h5` files corresponding to image cases (e.g., `0.h5` for `0.png`).

The processing involves two main steps:

### 2.1 Convert Images to JPG

The original images may not be in a universally compatible format. The `1.convert_images.py` script converts the image files to JPG format.

To run this script, simply execute:

structure
```bash
python 2.preprocess/1.convert_images.py <images_src> <processed_dataset>
```

example
```bash
python 2.preprocess/1.convert_images.py 1.data_access/data_sample/1.images/test 1.data_access/data_sample/3.data_processed
```

This script handles the source and destination paths internally.

### 2.2 Generate JSON Annotations

The annotation data is initially stored in separate .h5 files for positive and negative labels. The 2.generate_json.py script extracts this information and consolidates it into a single JSON file for each image, with the following structure:

```json
[
  {
    "x": 286,
    "y": 9,
    "label_id": 1
  },
  {
    "x": 159,
    "y": 36,
    "label_id": 2
  }
]
```

To run this script, you need to provide the paths to the positive annotations directory, the negative annotations directory, and the desired output directory for the combined JSON files.

structure
```bash
python 2.preprocess/2.generate_json.py <positive_dir> <negative_dir> <processed_dataset>
```

example
```bash
python 2.preprocess/2.generate_json.py 1.data_access/data_sample/2.annotations/test/positive 1.data_access/data_sample/2.annotations/test/negative 1.data_access/data_sample/3.data_processed
```

Upon successful execution of both 1.convert_images.py and 2.generate_json.py, all processed images (in JPG format) and their corresponding JSON annotation files will be placed together in a single output folder, effectively creating your processed dataset.

## 3. VLM Processing and Evaluation

The `3.vlm_processing/` directory contains the core logic for evaluating the VLMs. In this stage, the models are used to calculate the Ki-67 proliferation index from the processed images. These predictions are then compared against the actual Ki-67 values extracted from the JSON annotation files generated in the data processing step.

This process generates several important outputs:

- A **CSV file** that provides a detailed breakdown of the evaluation, including the predicted Ki-67 value and the actual Ki-67 value for each image (image,predicted,true).
- A **log file** that mirrors the structure of the CSV.
- An **`llm_responses` file** which stores the complete, raw responses received directly from the VLM.
- A **results graph** that visually compares the model's predictions against the actual values. This graph plots the predicted values on one axis and the actual values on the other, including a line representing the model's overall prediction trend.

For prompting the VLM, `txt` files are included in this directory. 

To run the VLM processing and evaluation, execute the 1.main_openai.py script, providing the path to your processed dataset folder:

structure  
```bash
python 3.vlm_processing/1.main_openai.py <processed_dataset> [<output_parent_dir>]
```

example  
```bash
python 3.vlm_processing/1.main_openai.py 1.data_access/data_sample/3.data_processed 5.results
```

To run the VLM processing for a single image, execute the 2.ki67_single_image.py script, providing the path to image file:

structure  
```bash
python 3.vlm_processing/2.ki67_single_image.py <image_path>
```

example  
```bash
python 3.vlm_processing/2.ki67_single_image.py 1.data_access/data_sample/3.data_processed/8.jpg
```

## 4. Utilities

The `utils/` directory houses a collection of auxiliary scripts designed to support various tasks related to data processing, results analysis, and validation. These scripts provide functionalities that complement the main project workflow.

Here's a breakdown of the available utility scripts:

- ### `calculate_ki_from_json.py`

  This script processes a single JSON annotation file (corresponding to a specific case) and calculates the Ki-67 index. It also returns the counts of immunopositive and immunonegative cells.

  **Usage:**

  structure  
  ```bash
  python 4.utils/calculate_ki_from_json.py <json_path>
  ```

  example  
  ```bash
  python 4.utils/calculate_ki_from_json.py 1.data_access/data_sample/3.data_processed/8.json
  ```

- ### `calculate_metrics.py`

  This utility calculates key evaluation metrics (R-squared, Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and Mean Absolute Error (MAE)) based on the model's results recorded in a CSV file.

  **Output (example):**

  ```
  Metrics
  R²   : val1
  MSE  : val2
  RMSE : val3
  MAE  : val4
  ```

  **Usage:**

  structure  
  ```bash
  python 4.utils/calculate_metrics.py <results.csv>
  ```

  example  
  ```bash
  python 4.utils/calculate_metrics.py 5.results/4.5/bcdata/ki67_results.csv
  ```

- ### `calculate_time_average.py`

  This script is designed to assess the performance efficiency of the model. It takes some representative cases from the dataset, calculates the execution time and the number of tokens used for each, and then provides an average of these values.

  **Usage:**

  structure  
  ```bash
  python 4.utils/calculate_time_average.py <processed_dataset> <output_parent_dir>
  ```

  example  
  ```bash
  python 4.utils/calculate_time_average.py 1.data_access/data_sample/3.data_processed 5.results
  ```

- ### `check_duplicates_in_csv.py`

  This script verifies the integrity of a CSV file by checking for any duplicate entries within it.

  **Usage:**

  structure  
  ```bash
  python 4.utils/check_duplicates_in_csv.py <results.csv>
  ```

  example  
  ```bash
  python 4.utils/check_duplicates_in_csv.py 5.results/4.5/bcdata/ki67_results.csv
  ```

- ### `check_range_in_csv.py`

  This utility ensures data completeness within the results CSV. It checks a specified range of image IDs (e.g., from 0 to 401) to confirm that no images are missing their predicted and real values in the CSV.

  **Usage:**

  structure  
  ```bash
  python 4.utils/check_range_in_csv.py <results.csv> <start_id> <end_id>
  ```

  example  
  ```bash
  python 4.utils/check_range_in_csv.py 5.results/4.5/bcdata/ki67_results.csv 0 25
  ```

- ### `compare_txt_vs_csv.py`

  This script compares the raw `llm_responses.txt` (which holds all model outputs) against the `ki67_results.csv` to identify any instances where the model provided a response that was not successfully logged into the CSV file.

  **Usage:**

  structure  
  ```bash
  python 4.utils/compare_txt_vs_csv.py <results.csv> <llm_responses.txt>
  ```

  example  
  ```bash
  python 4.utils/compare_txt_vs_csv.py 5.results/4.5/bcdata/ki67_results.csv 5.results/4.5/bcdata/llm_responses.txt
  ```

- ### `count_jsons.py`

  A simple utility to count the total number of JSON files present within a given directory.

  **Usage:**
  structure  
  ```bash
  python 4.utils/count_jsons.py <folder_with_jsons>
  ```

  example  
  ```bash
  python 4.utils/count_jsons.py 1.data_access/data_sample/3.data_processed
  ```

- ### `fill_csv_from_txt.py`

  This script helps to rectify the results CSV. It identifies cases from the `llm_responses.txt` that were correctly responded to by the model but, due to extraction errors, were not fully recorded in the initial CSV. It then populates these missing entries into the output CSV.

  **Usage:**

  structure  
  ```bash
  python 4.utils/fill_csv_from_txt.py <results.csv> <llm_responses.txt> <json_folder>
  ```

  example  
  ```bash
  python 4.utils/fill_csv_from_txt.py 5.results/4.5/bcdata/ki67_results.csv 5.results/4.5/bcdata/llm_responses.txt 1.data_access/data_sample/3.data_processed
  ```

- ### `plot_multiple_models.py`

  This script generates a consolidated graph visualizing the results from multiple models. It takes the CSV result files from various models as input (5.results folder) and plots their performance for comparative analysis.

  **Usage:**

  structure  
  ```bash
  python 4.utils/plot_multiple_models.py <results1.csv> [<results2.csv> ...]
  ```

  example (runs the comparison for four stored models)  
  ```bash
  python 4.utils/plot_multiple_models.py 5.results/4.5/bcdata/ki67_results.csv 5.results/gpt-4.1-mini-2025-04-14_results/bcdata/ki67_results.csv 5.results/gpt-4.1-2025-04-14_results/bcdata/ki67_results.csv 5.results/4o_results/bcdata/ki67_results.csv
  ```

  *(If you call the script **without arguments** it will fall back to that same default list.)*

- ### `predict_cells.py`

  This utility performs a prediction for a specific image. It calculates the immunopositive and immunonegative cell counts, along with the Ki-67 index, for a given image.

  **Usage:**

  structure  
  ```bash
  python 4.utils/predict_cells.py <image_path>
  ```

  example  
  ```bash
  python 4.utils/predict_cells.py 1.data_access/data_sample/3.data_processed/8.jpg
  ```

- ### `verify_images_in_csv.py`

  Checks that every image file in a given directory is listed in the image column of a results CSV.  
  Useful for spotting images that were processed but never logged.

  **Usage:**
  structure  
  ```bash
  python 4.utils/verify_images_in_csv.py <image_folder> <results.csv>
  ```

  example  
  ```bash
  python 4.utils/verify_images_in_csv.py 1.data_access/data_sample/3.data_processed 5.results/4.5/bcdata/ki67_results.csv
  ```

## 5. Results

The `5.results` directory is dedicated to storing the outputs. After running the VLM processing and evaluation (Step 3), this folder will contain the generated CSV files, logs, raw LLM responses, and the graphical representations for each model's performance on the Ki-67 index calculation.
