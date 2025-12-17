# Order Management System - Architecture

## 🎯 Project Overview

Event-driven Order Management System built with Django & DRF, focusing on SOLID principles, state machines, and domain events.

## 🏗️ Architecture Principles

### SOLID Principles Application

1. **Single Responsibility**: Each service handles one domain concern
2. **Open/Closed**: Extensible event handlers without modifying core
3. **Liskov Substitution**: Event handlers are interchangeable
4. **Interface Segregation**: Specific interfaces for event publishers/subscribers
5. **Dependency Inversion**: Depend on abstractions (protocols), not implementations

### Design Patterns

- **State Machine**: Order state transitions
- **Event Sourcing (Light)**: Event history as source of truth
- **Command Pattern**: State transitions as commands
- **Observer Pattern**: Event handlers react to domain events
- **Strategy Pattern**: Payment/shipping strategies
- **Repository Pattern**: Data access abstraction

## 📦 Project Structure

```
order_management_system/
├── core/                           # Django project settings
├── apps/
│   ├── orders/                     # Order domain
│   │   ├── models.py              # Order, OrderItem
│   │   ├── state_machine.py      # State transitions & validations
│   │   ├── services.py            # OrderService (business logic)
│   │   ├── commands.py            # Command pattern for operations
│   │   ├── api/                   # REST API
│   │   │   ├── v1/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   └── urls.py
│   │   └── tests/
│   │
│   ├── events/                     # Event system (reusable)
│   │   ├── models.py              # EventStore
│   │   ├── base.py                # DomainEvent, EventPublisher
│   │   ├── handlers.py            # EventHandler protocol
│   │   ├── registry.py            # Handler registry
│   │   ├── dispatcher.py          # Event dispatcher
│   │   ├── retry.py               # Retry mechanism
│   │   └── decorators.py          # @event_handler decorator
│   │
│   ├── payments/                   # Payment domain
│   │   ├── models.py              # Payment
│   │   ├── services.py            # PaymentService
│   │   ├── handlers.py            # Event handlers
│   │   └── strategies.py          # Payment strategies
│   │
│   ├── shipping/                   # Shipping domain
│   │   ├── models.py              # Shipment
│   │   ├── services.py            # ShippingService
│   │   └── handlers.py            # Event handlers
│   │
│   └── webhooks/                   # Webhook simulator
│       ├── models.py              # WebhookLog
│       ├── simulator.py           # External service simulator
│       └── views.py               # Webhook endpoints
│
├── shared/                         # Shared utilities
│   ├── exceptions.py              # Custom exceptions
│   ├── protocols.py               # Python protocols (interfaces)
│   └── utils.py
│
└── tests/
    └── integration/               # Integration tests
```

## 🔄 State Machine

### Order States

```python
PENDING    → Order created, awaiting payment
PAID       → Payment confirmed
PROCESSING → Being prepared
SHIPPED    → In transit
DELIVERED  → Completed successfully
CANCELLED  → Cancelled (from PENDING or PAID only)
FAILED     → Payment failed
```

### Valid Transitions

```
PENDING → PAID | CANCELLED | FAILED
PAID → PROCESSING | CANCELLED
PROCESSING → SHIPPED
SHIPPED → DELIVERED
DELIVERED → (terminal)
CANCELLED → (terminal)
FAILED → (terminal)
```

## 📨 Domain Events

### Event Types

1. **OrderCreated** - New order placed
2. **OrderPaid** - Payment successful
3. **OrderCancelled** - Order cancelled
4. **OrderShipped** - Order shipped
5. **OrderDelivered** - Order delivered
6. **PaymentFailed** - Payment failed
7. **PaymentRequested** - Payment initiated
8. **ShipmentRequested** - Shipping initiated

### Event Structure

```python
{
    "event_id": "uuid",
    "event_type": "OrderPaid",
    "aggregate_id": "order_uuid",
    "aggregate_type": "Order",
    "payload": {...},
    "metadata": {
        "user_id": "...",
        "timestamp": "...",
        "version": 1
    },
    "idempotency_key": "unique_key",
    "occurred_at": "timestamp"
}
```

## 🔐 Idempotency Strategy

- Each operation accepts `idempotency_key`
- Store processed keys in `EventStore`
- Return cached result if key exists
- Prevents duplicate processing

## 📊 CQRS Light

### Write Side (Commands)
- `OrderService.create_order()`
- `OrderService.pay_order()`
- `OrderService.cancel_order()`
- `OrderService.ship_order()`

### Read Side (Queries)
- Optimized read models
- Event projections
- Separate endpoints for queries
- Cached aggregations

## 🔄 Event Flow Example

```
1. User creates order
   → OrderService.create_order()
   → Order.state = PENDING
   → Publish OrderCreated event
   
2. PaymentHandler receives OrderCreated
   → PaymentService.request_payment()
   → Publish PaymentRequested event
   
3. Webhook simulates payment confirmation
   → OrderService.confirm_payment()
   → Order.state = PAID
   → Publish OrderPaid event
   
4. ShippingHandler receives OrderPaid
   → ShippingService.create_shipment()
   → Publish ShipmentRequested event
   
5. Webhook simulates shipping update
   → OrderService.mark_shipped()
   → Order.state = SHIPPED
   → Publish OrderShipped event
```

## 🔧 Technology Stack

- **Framework**: Django 5.0 + DRF 3.14
- **Database**: PostgreSQL (production) / SQLite (dev)
- **Async Tasks**: Django Q or Celery (for event retry)
- **API Versioning**: URL-based (`/api/v1/`)
- **Testing**: pytest + pytest-django
- **Code Quality**: black, flake8, mypy

## 🚀 API Endpoints

### v1 API

```
POST   /api/v1/orders/                  # Create order
GET    /api/v1/orders/                  # List orders
GET    /api/v1/orders/{id}/             # Get order detail
POST   /api/v1/orders/{id}/pay/         # Pay order
POST   /api/v1/orders/{id}/cancel/      # Cancel order
POST   /api/v1/orders/{id}/ship/        # Ship order
GET    /api/v1/orders/{id}/events/      # Get order events
GET    /api/v1/orders/{id}/history/     # Get state history

POST   /api/v1/webhooks/payment/        # Payment webhook (simulator)
POST   /api/v1/webhooks/shipping/       # Shipping webhook (simulator)
```

## 🧪 Testing Strategy

1. **Unit Tests**: Services, state machine, validators
2. **Integration Tests**: Full event flow
3. **API Tests**: DRF test client
4. **State Transition Tests**: All valid/invalid transitions
5. **Idempotency Tests**: Duplicate operations
6. **Event Handler Tests**: Handler isolation

## 📝 Key Implementation Details

### Event Handler Registration

```python
@event_handler(OrderCreated)
class PaymentRequestHandler:
    def handle(self, event: DomainEvent) -> None:
        # Process event
        pass
```

### State Machine Validation

```python
class OrderStateMachine:
    def can_transition(self, from_state, to_state) -> bool:
        return to_state in self.TRANSITIONS.get(from_state, [])
    
    def transition(self, order, to_state, reason=None):
        if not self.can_transition(order.state, to_state):
            raise InvalidStateTransition(...)
        # Perform transition + publish event
```

### Event Retry

- Exponential backoff
- Max 3 retries
- Dead letter queue for failures
- Manual retry endpoint

## 🎯 Learning Outcomes

1. ✅ SOLID principles in real Django app
2. ✅ Event-driven architecture
3. ✅ State machine implementation
4. ✅ Domain-driven design concepts
5. ✅ Idempotency handling
6. ✅ CQRS pattern
7. ✅ Advanced DRF techniques
8. ✅ Testing complex systems
9. ✅ API versioning
10. ✅ Webhook handling

## 🔜 Next Steps

1. Set up Django apps structure
2. Implement event system core
3. Build state machine
4. Create order models & services
5. Implement DRF API
6. Add event handlers
7. Build webhook simulator
8. Write comprehensive tests
9. Add retry mechanism
10. Document & polish

