# ML Projects - Machine Learning API with DDD Architecture

A production-ready FastAPI application for training and deploying machine learning models, built with Domain-Driven Design (DDD) architecture and SOLID principles.

## Features

- **Multiple ML Models**: Linear Regression, Logistic Regression, Decision Trees, Random Forests, and more
- **Clean Architecture**: DDD layers (Domain, Application, Infrastructure, Presentation)
- **Type Safety**: Full type hints with Pydantic validation
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Extensible**: Easy to add new model types without modifying existing code
- **Well-Tested**: Following testing best practices (coming soon)

## Supported Models

### Regression
- Linear Regression
- Ridge Regression
- Lasso Regression
- Decision Tree Regressor
- Random Forest Regressor

### Classification
- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier

## Architecture

This project follows **Domain-Driven Design (DDD)** with clean separation of concerns:

```
src/
├── domain/              # Business logic & rules (no dependencies)
│   ├── entities/        # Model (with identity)
│   ├── value_objects/   # ModelMetrics, PredictionResult, ModelType
│   ├── repositories/    # Interfaces (IModelRepository, IMLService)
│   └── exceptions.py    # Domain exceptions
│
├── application/         # Use cases (orchestration)
│   ├── use_cases/       # TrainModel, Predict, GetModel, etc.
│   └── dto/             # Pydantic request/response models
│
├── infrastructure/      # External concerns (implementations)
│   ├── repositories/    # JsonModelRepository
│   └── ml_models/       # SklearnMLService
│
└── presentation/        # HTTP interface
    ├── api/routes/      # FastAPI endpoints
    └── dependencies.py  # Dependency injection
```

**Dependency Flow**: `Presentation → Application → Domain ← Infrastructure`

## Setup

### Prerequisites

- Python 3.10+
- `uv` (recommended) or `pip`

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ml-projects
```

2. **Install dependencies with uv** (recommended)
```bash
# uv will create a virtual environment and install dependencies
uv sync --all-extras
```

**OR** with pip:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -e .
```

3. **Set up environment variables** (optional)
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode

```bash
# With uv
uv run python main.py

# OR activate venv and run
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Usage

### 1. Train a Model

**Request:**
```bash
POST /api/models/train
Content-Type: application/json

{
  "model_type": "linear_regression",
  "X": [[1], [2], [3], [4], [5]],
  "y": [2, 4, 6, 8, 10],
  "model_name": "my_first_model"
}
```

**Response:**
```json
{
  "model_id": "reg_abc123def456",
  "model_type": "linear_regression",
  "model_name": "my_first_model",
  "is_trained": true,
  "trained_at": "2024-01-15T10:30:00",
  "metrics": {
    "r2_score": 1.0,
    "mse": 0.0,
    "rmse": 0.0,
    "mae": 0.0
  },
  "message": "Model trained successfully"
}
```

### 2. Make Predictions

**Request:**
```bash
POST /api/models/predict
Content-Type: application/json

{
  "model_id": "reg_abc123def456",
  "X": [[6], [7], [8]]
}
```

**Response:**
```json
{
  "model_id": "reg_abc123def456",
  "predictions": [12.0, 14.0, 16.0],
  "count": 3
}
```

### 3. Get Model Information

```bash
GET /api/models/reg_abc123def456
```

### 4. List All Models

```bash
GET /api/models
```

### 5. Delete a Model

```bash
DELETE /api/models/reg_abc123def456
```

## Example: Complete Workflow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Train a model
train_response = requests.post(
    f"{BASE_URL}/api/models/train",
    json={
        "model_type": "linear_regression",
        "X": [[1], [2], [3], [4], [5]],
        "y": [2, 4, 6, 8, 10],
        "model_name": "simple_linear"
    }
)
model_id = train_response.json()["model_id"]
print(f"Model trained: {model_id}")

# 2. Make predictions
predict_response = requests.post(
    f"{BASE_URL}/api/models/predict",
    json={
        "model_id": model_id,
        "X": [[6], [7], [8]]
    }
)
predictions = predict_response.json()["predictions"]
print(f"Predictions: {predictions}")

# 3. Get model info
info_response = requests.get(f"{BASE_URL}/api/models/{model_id}")
print(f"Model info: {info_response.json()}")
```

## Project Structure

```
ml-projects/
├── src/
│   ├── domain/                    # Core business logic
│   ├── application/               # Use cases
│   ├── infrastructure/            # Technical implementations
│   └── presentation/              # FastAPI routes
├── tests/                         # Unit & integration tests
├── models/                        # Saved trained models
├── main.py                        # FastAPI application
├── pyproject.toml                 # Project configuration
├── DEVELOPMENT_GUIDELINES.md      # DDD & SOLID best practices
└── README.md                      # This file
```

## Development Guidelines

See [DEVELOPMENT_GUIDELINES.md](DEVELOPMENT_GUIDELINES.md) for:
- DDD best practices
- SOLID principles with examples
- Code organization rules
- Testing guidelines
- Python best practices

## Adding New Models

Thanks to the Open/Closed Principle, adding new models is easy:

1. **Add model type** to `src/domain/value_objects/model_type.py`:
```python
class ModelType(str, Enum):
    # ... existing types
    SVM_CLASSIFIER = "svm_classifier"
```

2. **Add implementation** to `src/infrastructure/ml_models/sklearn_service.py`:
```python
def _create_sklearn_model(self, model_type: ModelType):
    model_map = {
        # ... existing models
        ModelType.SVM_CLASSIFIER: SVC(),
    }
    # ...
```

That's it! No changes needed in domain, application, or presentation layers.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/domain/test_model.py
```

## Contributing

1. Follow the guidelines in `DEVELOPMENT_GUIDELINES.md`
2. Write tests for new features
3. Ensure all tests pass before committing
4. Use type hints for all function signatures
5. Keep layers properly separated (no domain imports in infrastructure details, etc.)

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Pydantic**: Data validation using Python type hints
- **scikit-learn**: Machine learning library
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation (for future features)
- **Joblib**: Model serialization
- **uv**: Fast Python package manager

## License

MIT License - see LICENSE file for details

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Model versioning
- [ ] Batch predictions
- [ ] Model comparison endpoints
- [ ] Cross-validation support
- [ ] Hyperparameter tuning
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Authentication & authorization
- [ ] React frontend

## Contact

For questions or feedback, please open an issue on GitHub.
