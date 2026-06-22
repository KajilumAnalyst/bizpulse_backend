from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.models import User, Store
from app.schemas.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Debug logs for Railway
    print(f"Password length: {len(body.password)}")
    print(f"Password bytes: {len(body.password.encode('utf-8'))}")

    # Validate password length before bcrypt hashing
    if len(body.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be 72 characters or fewer"
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        business_name=body.business_name,
        business_type=body.business_type,
        country=body.country or "NG",
        phone=body.phone,
        plan=body.plan or "basic",
    )

    db.add(user)
    db.flush()  # get user.id before commit

    # Auto-create a default store
    default_store = Store(
        owner_id=user.id,
        name=f"{body.business_name} — Main",
        type=body.business_type,
    )
    db.add(default_store)

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        business_name=user.business_name,
        plan=user.plan,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(
        body.password,
        user.hashed_password or ""
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        business_name=user.business_name,
        plan=user.plan,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user
