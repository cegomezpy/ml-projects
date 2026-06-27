# Claude Instructions for ML Projects

This file contains permanent instructions for working on this ML Projects codebase.

## Core Principles

**ALWAYS follow the guidelines defined in [DEVELOPMENT_GUIDELINES.md](../DEVELOPMENT_GUIDELINES.md)**

This project uses **Domain-Driven Design (DDD)** architecture with **SOLID principles**. Every code change MUST adhere to these standards.

## Mandatory Rules

### 1. DDD Architecture - Layer Boundaries

**NEVER violate layer dependencies:**

```
✅ ALLOWED:
Presentation → Application → Domain ← Infrastructure

❌ FORBIDDEN:
- Domain importing from Application, Infrastructure, or Presentation
- Application importing from Infrastructure or Presentation
- Infrastructure importing from Presentation
```

**Before writing ANY code:**
1. Identify which layer it belongs to
2. Verify it only depends on allowed layers
3. Use interfaces (abstractions) from Domain, not concrete implementations

### 2. SOLID Principles - Non-Negotiable

#### Single Responsibility Principle
- ✅ Each class has ONE reason to change
- ❌ Never create "god classes" or "utility classes" with multiple responsibilities
- **Example**: `TrainModelUseCase` only trains models, nothing else

#### Open/Closed Principle
- ✅ Extend behavior through inheritance/composition, not modification
- ❌ Never modify existing classes to add new features
- **Example**: Add new ML models by extending `ModelType` enum and adding to factory, not by modifying existing model code

#### Liskov Substitution Principle
- ✅ All implementations of an interface must be substitutable
- ❌ Never break contracts defined in abstract classes/interfaces
- **Example**: Any `IMLService` implementation must work with any use case

#### Interface Segregation Principle
- ✅ Create focused, specific interfaces
- ❌ Never force classes to implement methods they don't use
- **Example**: Separate `ITrainable` from `ICrossValidatable` if not all models support both

#### Dependency Inversion Principle
- ✅ ALWAYS depend on abstractions (interfaces), NEVER on concretions
- ❌ Never instantiate concrete implementations directly in use cases
- **Example**: `TrainModelUseCase` depends on `IMLService`, not `SklearnMLService`

### 3. Code Organization Rules

#### Entities vs Value Objects
- **Entities** (have identity): `Model` - can be compared by ID
- **Value Objects** (no identity): `ModelMetrics`, `PredictionResult` - immutable, compared by value
- ✅ Use `@dataclass(frozen=True)` for value objects
- ✅ Entities should have private attributes with property accessors

#### Repository Pattern
- ✅ Domain defines repository INTERFACES (what operations are needed)
- ✅ Infrastructure provides IMPLEMENTATIONS (how to execute them)
- ❌ Never put implementation details in repository interfaces

#### Use Cases
- ✅ Each use case orchestrates ONE business flow
- ✅ Use cases coordinate domain entities and call repositories
- ❌ Never put business logic in use cases - delegate to domain entities
- ❌ Never access external services directly - use repository interfaces

### 4. Python Best Practices

#### Type Hints - Mandatory
```python
# ✅ ALWAYS do this
def train_model(X: np.ndarray, y: np.ndarray) -> ModelMetrics:
    ...

# ❌ NEVER do this
def train_model(X, y):
    ...
```

#### Pydantic for Validation
- ✅ Use Pydantic for ALL API request/response DTOs
- ✅ Add validators for business rules
- ✅ Provide examples in schema

#### Error Handling
- ✅ Use domain-specific exceptions (inherit from `DomainException`)
- ✅ Catch domain exceptions in presentation layer, convert to HTTP errors
- ❌ Never catch generic `Exception` in domain/application layers
- ❌ Never raise HTTP exceptions from domain/application layers

#### Code Comments - Clean Code Style
- ✅ Document the business flow in the **docstring** (e.g., "Business flow: 1. Validate, 2. Process, 3. Return")
- ✅ Add comments ONLY when code intent is not obvious from variable/method names
- ❌ **NEVER add numbered step-by-step inline comments** like `# 1. Do this`, `# 2. Do that`
- ❌ Never add obvious comments that just restate what the code does

**Example:**
```python
# ✅ GOOD - Flow in docstring, clean code
def execute(self, model_id: str) -> dict:
    """
    Execute prediction use case.

    Business flow:
    1. Retrieve model
    2. Validate it's trained
    3. Make prediction
    4. Return results
    """
    model = self._repository.find_by_id(model_id)
    model.ensure_trained()
    result = self._ml_service.predict(model, X)
    return result.to_dict()

# ❌ BAD - Numbered inline comments
def execute(self, model_id: str) -> dict:
    # 1. Retrieve model
    model = self._repository.find_by_id(model_id)
    # 2. Validate it's trained
    model.ensure_trained()
    # 3. Make prediction
    result = self._ml_service.predict(model, X)
    # 4. Return results
    return result.to_dict()
```

**The code should be self-documenting through clear naming. Comments are for WHY, not WHAT.**

### 5. Naming Conventions

#### Files and Modules
- `snake_case` for files: `train_model.py`, `model_repository.py`
- `PascalCase` for classes: `TrainModelUseCase`, `ModelRepository`
- `UPPER_CASE` for constants: `MIN_SAMPLES`, `DEFAULT_TIMEOUT`

#### Domain Language
- Use business terminology, not technical jargon
- ✅ `Model`, `TrainingSession`, `PredictionResult`
- ❌ `SklearnWrapper`, `MLHelper`, `DataProcessor`

### 6. Adding New Features

**When adding a new ML model type:**
1. Add to `domain/value_objects/model_type.py` enum
2. Add factory method in `infrastructure/ml_models/sklearn_service.py`
3. NO changes needed in domain, application, or presentation layers

**When adding a new use case:**
1. Create in `application/use_cases/`
2. Define DTOs in `application/dto/`
3. Add route in `presentation/api/routes/`
4. Wire up in `presentation/dependencies.py`

**When adding a new repository:**
1. Define interface in `domain/repositories/`
2. Implement in `infrastructure/repositories/`
3. Inject via `presentation/dependencies.py`

### 7. Testing Requirements

**Before committing ANY code:**
- [ ] All type hints are present
- [ ] No violations of layer boundaries
- [ ] SOLID principles followed
- [ ] Docstrings for public methods
- [ ] No business logic in presentation layer
- [ ] No infrastructure details in domain layer
- [ ] Using dependency injection (not direct instantiation)
- [ ] Domain exceptions for business rule violations

### 8. Code Review Triggers

**STOP and reconsider if you see:**
- ❌ Import from outer layer to inner layer
- ❌ Direct instantiation of concrete classes in use cases
- ❌ HTTP concerns in domain/application layers
- ❌ Business logic in controllers/routes
- ❌ Multiple responsibilities in one class
- ❌ Missing type hints
- ❌ Generic exception handling

### 9. Documentation

**Every new file must have:**
- Module-level docstring explaining purpose
- Class-level docstrings
- Method docstrings for public methods (Google style)
- Type hints for ALL parameters and return values

### 10. Refactoring Guidelines

**When refactoring:**
- ✅ Extract methods/classes that violate SRP
- ✅ Introduce abstractions for dependencies
- ✅ Make value objects immutable
- ✅ Move business logic from use cases to domain entities
- ❌ Never break existing tests
- ❌ Never change layer responsibilities

## Quick Reference

### Layer Responsibilities

| Layer | Responsibility | Can Import From | Examples |
|-------|---------------|-----------------|----------|
| **Domain** | Business rules, entities, value objects, interfaces | Nothing (pure domain) | `Model`, `IModelRepository` |
| **Application** | Use cases, orchestration, DTOs | Domain only | `TrainModelUseCase` |
| **Infrastructure** | External services, DB, ML libraries | Domain (implements interfaces) | `SklearnMLService` |
| **Presentation** | HTTP, routing, request/response | Application, Domain | FastAPI routes |

### Dependency Injection Pattern

```python
# 1. Domain defines interface
class IModelRepository(ABC):
    @abstractmethod
    def save(self, model: Model) -> None: pass

# 2. Infrastructure implements
class JsonModelRepository(IModelRepository):
    def save(self, model: Model) -> None:
        # implementation

# 3. Application uses interface
class TrainModelUseCase:
    def __init__(self, repository: IModelRepository):  # ← Interface!
        self._repository = repository

# 4. Presentation injects concrete implementation
def get_use_case(repo: IModelRepository = Depends(get_repo)):
    return TrainModelUseCase(repository=repo)
```

## Remember

> "The domain layer is the heart of the software. Keep it pure, keep it focused, keep it independent."

Every line of code in this project should demonstrate:
1. **Clarity** - Easy to understand intent
2. **Maintainability** - Easy to change without breaking
3. **Testability** - Easy to test in isolation
4. **Extensibility** - Easy to add features without modification

**When in doubt, refer to [DEVELOPMENT_GUIDELINES.md](../DEVELOPMENT_GUIDELINES.md) for detailed examples.**

---

**These are not suggestions - they are requirements for this codebase.**
