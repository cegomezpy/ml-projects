# Development Guidelines

This document outlines the best practices, design principles, and coding standards for this project.

## Table of Contents
1. [DDD Best Practices](#ddd-best-practices)
2. [SOLID Principles](#solid-principles)
3. [Code Organization](#code-organization)
4. [Python Best Practices](#python-best-practices)
5. [Testing Guidelines](#testing-guidelines)

---

## DDD Best Practices

### 1. **Ubiquitous Language**
- Use business terminology throughout the codebase
- Class names should reflect domain concepts: `Model`, `TrainingSession`, `PredictionResult`
- Avoid technical jargon in domain layer: `ModelTrainer` not `SklearnWrapper`

### 2. **Bounded Contexts**
- Each ML model type (linear regression, logistic regression, etc.) is a separate bounded context
- Keep models isolated with their own entities and value objects
- Share only through well-defined interfaces

### 3. **Entities vs Value Objects**
```python
# Entity - Has identity, mutable
class Model:
    def __init__(self, model_id: str, model_type: str):
        self.model_id = model_id  # Identity
        self.model_type = model_type
        self.trained_at: Optional[datetime] = None

# Value Object - No identity, immutable
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelMetrics:
    r2_score: float
    mse: float
    mae: float
```

### 4. **Repository Pattern**
- **Domain layer**: Define repository interfaces (contracts)
- **Infrastructure layer**: Implement concrete repositories
- Always depend on abstractions, not implementations

```python
# ✅ GOOD - Domain defines interface
class IModelRepository(ABC):
    @abstractmethod
    def save(self, model: Model) -> None:
        pass

# ✅ GOOD - Infrastructure implements it
class FileModelRepository(IModelRepository):
    def save(self, model: Model) -> None:
        joblib.dump(model, f"{model.model_id}.pkl")
```

### 5. **Aggregate Roots**
- `Model` is an aggregate root
- Access `TrainingSession` only through `Model`
- Enforce invariants within the aggregate

### 6. **Domain Services**
- Use when logic doesn't belong to a single entity
- Example: `ModelComparisonService` to compare multiple models

---

## SOLID Principles

### S - Single Responsibility Principle
**Each class should have only ONE reason to change**

```python
# ❌ BAD - Multiple responsibilities
class ModelService:
    def train(self, X, y): ...
    def save_to_database(self): ...
    def send_notification(self): ...

# ✅ GOOD - Separated concerns
class TrainModelUseCase:
    def execute(self, X, y): ...

class ModelRepository:
    def save(self, model): ...

class NotificationService:
    def notify(self, event): ...
```

### O - Open/Closed Principle
**Open for extension, closed for modification**

```python
# ✅ GOOD - Use polymorphism
class MLModel(ABC):
    @abstractmethod
    def train(self, X, y): ...
    @abstractmethod
    def predict(self, X): ...

class LinearRegressionModel(MLModel):
    def train(self, X, y): ...
    def predict(self, X): ...

class LogisticRegressionModel(MLModel):
    def train(self, X, y): ...
    def predict(self, X): ...

# Adding new models doesn't modify existing code
```

### L - Liskov Substitution Principle
**Subtypes must be substitutable for their base types**

```python
# ✅ GOOD - All regression models behave consistently
def train_any_model(model: MLModel, X, y):
    model.train(X, y)  # Works with any MLModel subclass
    return model.predict(X)
```

### I - Interface Segregation Principle
**Don't force clients to depend on methods they don't use**

```python
# ❌ BAD - Fat interface
class IMLModel(ABC):
    @abstractmethod
    def train(self, X, y): ...
    @abstractmethod
    def cross_validate(self, X, y, folds): ...  # Not all models need this
    @abstractmethod
    def grid_search(self, params): ...  # Not all models need this

# ✅ GOOD - Segregated interfaces
class ITrainable(ABC):
    @abstractmethod
    def train(self, X, y): ...

class ICrossValidatable(ABC):
    @abstractmethod
    def cross_validate(self, X, y, folds): ...

# Use only what you need
class SimpleModel(ITrainable):
    def train(self, X, y): ...

class AdvancedModel(ITrainable, ICrossValidatable):
    def train(self, X, y): ...
    def cross_validate(self, X, y, folds): ...
```

### D - Dependency Inversion Principle
**Depend on abstractions, not concretions**

```python
# ❌ BAD - Direct dependency on implementation
class TrainModelUseCase:
    def __init__(self):
        self.repository = FileModelRepository()  # Concrete class

# ✅ GOOD - Depend on abstraction
class TrainModelUseCase:
    def __init__(self, repository: IModelRepository):
        self.repository = repository  # Abstract interface

# Inject dependency
use_case = TrainModelUseCase(repository=FileModelRepository())
# Easy to swap: use_case = TrainModelUseCase(repository=DatabaseModelRepository())
```

---

## Code Organization

### Layer Dependencies
```
Presentation → Application → Domain ← Infrastructure
```

**Rules:**
1. ✅ Presentation can depend on Application
2. ✅ Application can depend on Domain
3. ✅ Infrastructure implements Domain interfaces
4. ❌ Domain NEVER depends on outer layers
5. ❌ Application NEVER depends on Infrastructure or Presentation

### Import Guidelines
```python
# ✅ GOOD - Inner layers
from domain.entities.model import Model
from domain.repositories.i_model_repository import IModelRepository

# ❌ BAD - Domain importing from infrastructure
from infrastructure.ml_models.sklearn_linear_regression import SklearnLinearRegression
```

---

## Python Best Practices

### 1. **Type Hints Always**
```python
# ✅ GOOD
def train_model(X: np.ndarray, y: np.ndarray) -> ModelMetrics:
    ...

# ❌ BAD
def train_model(X, y):
    ...
```

### 2. **Dataclasses for DTOs and Value Objects**
```python
from dataclasses import dataclass

@dataclass
class TrainModelRequest:
    X: list[list[float]]
    y: list[float]
    model_type: str
```

### 3. **Pydantic for Validation**
```python
from pydantic import BaseModel, Field, validator

class TrainModelRequest(BaseModel):
    X: list[list[float]] = Field(..., min_items=1)
    y: list[float] = Field(..., min_items=1)
    model_type: str

    @validator('X', 'y')
    def check_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Cannot be empty')
        return v
```

### 4. **Use Enums for Constants**
```python
from enum import Enum

class ModelType(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    DECISION_TREE = "decision_tree"
```

### 5. **Error Handling**
```python
# Domain exceptions
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class InsufficientDataError(DomainException):
    """Raised when training data is insufficient"""
    pass

# Use specific exceptions
if len(X) < 2:
    raise InsufficientDataError("Need at least 2 samples to train")
```

---

## Testing Guidelines

### 1. **Test Pyramid**
```
      /\
     /  \    Unit Tests (70%)
    /____\
   /      \  Integration Tests (20%)
  /________\
 /          \ E2E Tests (10%)
/____________\
```

### 2. **Unit Test Example**
```python
# tests/unit/domain/test_model.py
import pytest
from domain.entities.model import Model

def test_model_creation():
    model = Model(model_id="test_1", model_type="linear_regression")
    assert model.model_id == "test_1"
    assert model.trained_at is None

def test_model_requires_training_before_prediction():
    model = Model(model_id="test_1", model_type="linear_regression")
    with pytest.raises(ValueError, match="not trained"):
        model.predict([[1, 2]])
```

### 3. **Test Naming Convention**
```
test_<unit>_<scenario>_<expected_result>

Examples:
- test_model_with_insufficient_data_raises_error
- test_prediction_with_trained_model_returns_result
- test_repository_save_creates_file
```

### 4. **Mock External Dependencies**
```python
from unittest.mock import Mock

def test_use_case_calls_repository():
    # Arrange
    mock_repo = Mock(spec=IModelRepository)
    use_case = TrainModelUseCase(repository=mock_repo)

    # Act
    use_case.execute(X=[[1], [2]], y=[1, 2])

    # Assert
    mock_repo.save.assert_called_once()
```

---

## Dependency Injection

### Use FastAPI's Depends
```python
# presentation/dependencies.py
from fastapi import Depends
from infrastructure.repositories.model_repository import ModelRepository

def get_model_repository() -> IModelRepository:
    return ModelRepository()

def get_train_use_case(
    repository: IModelRepository = Depends(get_model_repository)
) -> TrainModelUseCase:
    return TrainModelUseCase(repository=repository)

# presentation/api/routes/model.py
@router.post("/train")
async def train(
    request: TrainModelRequest,
    use_case: TrainModelUseCase = Depends(get_train_use_case)
):
    return use_case.execute(request.X, request.y)
```

---

## Code Review Checklist

Before committing code, verify:

- [ ] Follows DDD layer boundaries
- [ ] Respects SOLID principles
- [ ] Has type hints
- [ ] Includes docstrings for public methods
- [ ] Has unit tests (minimum 80% coverage)
- [ ] No business logic in presentation layer
- [ ] No infrastructure code in domain layer
- [ ] Uses dependency injection
- [ ] Error handling with specific exceptions
- [ ] Validated with Pydantic where appropriate

---

## Example: Complete Flow

```python
# 1. DOMAIN - Interface
class IModelRepository(ABC):
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> Model:
        pass

# 2. INFRASTRUCTURE - Implementation
class SklearnModelRepository(IModelRepository):
    def train(self, X: np.ndarray, y: np.ndarray) -> Model:
        sklearn_model = LinearRegression()
        sklearn_model.fit(X, y)
        # ... save model
        return Model(...)

# 3. APPLICATION - Use Case
class TrainModelUseCase:
    def __init__(self, repository: IModelRepository):
        self.repository = repository

    def execute(self, X: list, y: list) -> ModelMetrics:
        # Validate, convert, orchestrate
        X_array = np.array(X)
        y_array = np.array(y)
        model = self.repository.train(X_array, y_array)
        return ModelMetrics(...)

# 4. PRESENTATION - Controller
@router.post("/train")
async def train(
    request: TrainModelRequest,
    use_case: TrainModelUseCase = Depends()
):
    try:
        metrics = use_case.execute(request.X, request.y)
        return {"metrics": metrics}
    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Additional Resources

- **DDD**: "Domain-Driven Design" by Eric Evans
- **Clean Architecture**: "Clean Architecture" by Robert C. Martin
- **Python**: PEP 8, PEP 484 (Type Hints)
- **FastAPI**: https://fastapi.tiangolo.com/

---

**Remember**: These are guidelines, not rigid rules. Use judgment and prioritize:
1. **Readability** over cleverness
2. **Simplicity** over premature abstraction
3. **Testability** over complex architectures
4. **Domain clarity** over technical perfection
