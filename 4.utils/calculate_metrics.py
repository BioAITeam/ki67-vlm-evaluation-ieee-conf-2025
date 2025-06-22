import csv
import sys
import math
from pathlib import Path
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def calculate_metrics(csv_path: str) -> None:
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    # ── Detect column names ───────────────────────────────────────────────────
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

    pred_col_candidates = ["predict", "predicted", "pred"]
    pred_col = next((c for c in pred_col_candidates if c in fieldnames), None)
    if pred_col is None or "true" not in fieldnames:
        print("Column names not found.\n"
              f"    Found columns: {fieldnames}\n"
               "    Need one of {predict, predicted, pred} and 'true'.")
        sys.exit(1)

    # ── Load data ─────────────────────────────────────────────────────────────
    y_true, y_pred = [], []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                y_true.append(float(row["true"]))
                y_pred.append(float(row[pred_col]))
            except (ValueError, KeyError):
                # Skip rows with missing / invalid numbers
                continue

    if not y_true:
        print(" No valid rows found - check your CSV content.")
        sys.exit(1)

    # ── Compute metrics ───────────────────────────────────────────────────────
    r2 = r2_score(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = math.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)

    # ── Output ────────────────────────────────────────────────────────────────
    print("Metrics")
    print(f"R²   : {r2:.4f}")
    print(f"MSE  : {mse:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"MAE  : {mae:.4f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python 4.utils/calculate_metrics.py <results.csv>\n"
            "Example:\n"
            "  python 4.utils/calculate_metrics.py "
            "5.results/4.5/bcdata/ki67_results.csv"
        )
        sys.exit(1)

    calculate_metrics(sys.argv[1])