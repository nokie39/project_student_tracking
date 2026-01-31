from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session # <--- Import ເພີ່ມ
import random
import database, models # <--- Import ເພີ່ມ (ເພື່ອດຶງຂໍ້ມູນ User ID ຈາກ Database)
import os

# Secret Key
SECRET_KEY = os.environ.get("SECRET_KEY", "laos_student_tracking_secret_key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # ອາຍຸ 7 ມື້ (ຕົວຢ່າງ)

# ໃຊ້ HTTPBearer ເພື່ອໃຫ້ວາງ Token ໄດ້ງ່າຍໆ
security = HTTPBearer()

# 1. ສ້າງ OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# 2. ສ້າງ JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 3. ຟັງຊັນກວດສອບ Token (ອັບເດດໃຫ້ Return User ID)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(database.get_db) # <--- Inject Database ເຂົ້າມາ
):
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # --- ສ່ວນທີ່ເພີ່ມໃໝ່: ດຶງຂໍ້ມູນ User ຈາກ Database ---
    # ເຮົາຕ້ອງດຶງຈາກ DB ເພື່ອເອົາ ID ຂອງ User ໄປໃຊ້ໃນຕາຕະລາງອື່ນ (ເຊັ່ນ: ການສົ່ງວຽກ)
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    # Return ຂໍ້ມູນຄົບຖ້ວນ (ID, Email, Role)
    return {
        "id": user.id, 
        "email": user.email, 
        "role": user.role,
        "full_name": user.full_name
    }