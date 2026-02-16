from typing import Optional, List
from sqlalchemy.orm import Session 
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def block_user(self, db: Session, *, db_obj: User, reason: str, admin_id: int) -> User:
        # Update user status
        db_obj.is_blocked = True
        db_obj.block_reason = reason
        db.add(db_obj)
        
        # Create audit log
        audit = AuditLog(
            action="BLOCK_USER",
            target_type="USER",
            target_id=str(db_obj.id),
            details=f"Reason: {reason}",
            actor_id=admin_id
        )
        db.add(audit)
        
        db.commit()
        db.refresh(db_obj)
        
        # Mock Email Notification
        print(f"MOCK EMAIL: Sending block notification to {db_obj.email}. Reason: {reason}")
        
        return db_obj

    def delete(self, db: Session, *, id: int, admin_id: int) -> Optional[User]:
        """Delete a user by ID."""
        user = db.query(User).filter(User.id == id).first()
        if not user:
            return None
        
        # Create audit log before deletion
        audit = AuditLog(
            action="DELETE_USER",
            target_type="USER",
            target_id=str(id),
            details=f"Deleted user: {user.email}",
            actor_id=admin_id
        )
        db.add(audit)
        
        db.delete(user)
        db.commit()
        return user

user = CRUDUser()
