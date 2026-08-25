from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel


app = FastAPI(title="Cloud Journey State Service")
db = firestore.Client()


def now():
    return datetime.now(timezone.utc).isoformat()


class CreateJourneyRequest(BaseModel):
    journey_id: str
    apm_id: str
    requested_by: str


class TransitionRequest(BaseModel):
    expected_state: str
    next_state: str
    actor: str = "cloud-workflows"


class CallbackRequest(BaseModel):
    callback_url: str


class StateConflict(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/journeys")
def create_journey(req: CreateJourneyRequest):
    ref = db.collection("journeys").document(req.journey_id)

    if ref.get().exists:
        raise HTTPException(
            status_code=409,
            detail="Journey already exists"
        )

    timestamp = now()

    document = {
        "journey_id": req.journey_id,
        "apm_id": req.apm_id,
        "requested_by": req.requested_by,
        "status": "CREATED",
        "current_step": "created",
        "callback_url": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    ref.set(document)

    ref.collection("events").document().set({
        "type": "JOURNEY_CREATED",
        "to": "CREATED",
        "actor": req.requested_by,
        "timestamp": timestamp,
    })

    return document


@app.get("/journeys/{journey_id}")
def get_journey(journey_id: str):
    ref = db.collection("journeys").document(journey_id)
    snapshot = ref.get()

    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="Journey not found")

    return snapshot.to_dict()


@firestore.transactional
def transition_transaction(
    transaction,
    journey_ref,
    event_ref,
    expected_state,
    next_state,
    actor,
):
    snapshot = journey_ref.get(transaction=transaction)

    if not snapshot.exists:
        raise KeyError("Journey not found")

    data = snapshot.to_dict()
    actual_state = data.get("status")

    if actual_state != expected_state:
        raise StateConflict(expected_state, actual_state)

    timestamp = now()

    transaction.update(
        journey_ref,
        {
            "status": next_state,
            "current_step": next_state.lower(),
            "updated_at": timestamp,
        },
    )

    transaction.set(
        event_ref,
        {
            "type": "STATE_TRANSITION",
            "from": expected_state,
            "to": next_state,
            "actor": actor,
            "timestamp": timestamp,
        },
    )

    return {
        "journey_id": journey_ref.id,
        "previous_state": expected_state,
        "status": next_state,
    }


@app.post("/journeys/{journey_id}/transition")
def transition(journey_id: str, req: TransitionRequest):
    journey_ref = db.collection("journeys").document(journey_id)
    event_ref = journey_ref.collection("events").document()

    transaction = db.transaction()

    try:
        return transition_transaction(
            transaction,
            journey_ref,
            event_ref,
            req.expected_state,
            req.next_state,
            req.actor,
        )

    except StateConflict as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Invalid state transition",
                "expected": exc.expected,
                "actual": exc.actual,
            },
        )

    except KeyError:
        raise HTTPException(status_code=404, detail="Journey not found")


@firestore.transactional
def callback_transaction(
    transaction,
    journey_ref,
    event_ref,
    callback_url,
):
    snapshot = journey_ref.get(transaction=transaction)

    if not snapshot.exists:
        raise KeyError("Journey not found")

    data = snapshot.to_dict()
    actual_state = data.get("status")

    if actual_state != "PLAN_READY":
        raise StateConflict("PLAN_READY", actual_state)

    timestamp = now()

    transaction.update(
        journey_ref,
        {
            "status": "WAITING_FOR_APPROVAL",
            "current_step": "waiting_for_approval",
            "callback_url": callback_url,
            "updated_at": timestamp,
        },
    )

    transaction.set(
        event_ref,
        {
            "type": "WAITING_FOR_APPROVAL",
            "from": "PLAN_READY",
            "to": "WAITING_FOR_APPROVAL",
            "actor": "cloud-workflows",
            "timestamp": timestamp,
        },
    )

    return {
        "journey_id": journey_ref.id,
        "status": "WAITING_FOR_APPROVAL",
    }


@app.post("/journeys/{journey_id}/callback")
def register_callback(journey_id: str, req: CallbackRequest):
    journey_ref = db.collection("journeys").document(journey_id)
    event_ref = journey_ref.collection("events").document()

    transaction = db.transaction()

    try:
        return callback_transaction(
            transaction,
            journey_ref,
            event_ref,
            req.callback_url,
        )

    except StateConflict as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Cannot register callback",
                "expected": exc.expected,
                "actual": exc.actual,
            },
        )

    except KeyError:
        raise HTTPException(status_code=404, detail="Journey not found")
