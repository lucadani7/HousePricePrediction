from datetime import datetime, timezone

import sklearn
from sklearn.model_selection import cross_val_score, KFold
import json
import joblib

from housepriceprediction.config import RANDOM_STATE, MODELS_DIR
from housepriceprediction.data import load_training_data
from housepriceprediction.features import FORM_FEATURES
from housepriceprediction.modeling import build_final_pipeline, FINAL_LASSO_ALPHA


def main() -> None:
    """Trains the final pipeline on all training data, evaluates via cross-validation,

    and saves both the trained model (model.joblib) and metadata (model.json)
    to the backend models directory.
    """
    print("Loading standardized training data...")
    X, y = load_training_data()

    print("Running 5-fold cross-validation evaluation...")
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    pipeline_for_cv = build_final_pipeline()
    scores = -cross_val_score(
        pipeline_for_cv,
        X,
        y,
        cv=cv,
        scoring="neg_root_mean_squared_log_error",
    )

    mean_rmsle = float(scores.mean())
    std_rmsle = float(scores.std())
    print(f"CV RMSLE: {mean_rmsle:.4f} (+/- {std_rmsle:.4f})")

    print("Training final pipeline on full dataset...")
    final_pipeline = build_final_pipeline()
    final_pipeline.fit(X, y)

    # Ensure models directory exists
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / "model.joblib"
    metadata_path = MODELS_DIR / "model.json"

    print(f"Saving model to {model_path}...")
    joblib.dump(final_pipeline, model_path)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "cv_rmsle_mean": round(mean_rmsle, 4),
        "cv_rmsle_std": round(std_rmsle, 4),
        "final_lasso_alpha": FINAL_LASSO_ALPHA,
        "form_features": list(FORM_FEATURES),
        "n_samples": len(X),
        "sklearn_version": sklearn.__version__,
    }

    print(f"Saving metadata to {metadata_path}...")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print("Training pipeline successfully completed and artifacts saved!")


if __name__ == "__main__":
    main()