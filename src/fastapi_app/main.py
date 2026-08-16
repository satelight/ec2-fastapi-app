from fastapi import FastAPI, Depends, HTTPException, UploadFile, File as FastAPIFile
import os
import tempfile
from sqlalchemy.orm import Session
from .database import engine, get_db, Base, SessionLocal
from . import models, schemas
from .s3_utils import upload_to_s3

# エイリアス定義（CRUD で使用）
Item = schemas.Item
ItemCreate = schemas.ItemCreate
ItemUpdate = schemas.ItemUpdate
ItemModel = models.Item

Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/items", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/api/items", response_model=list[Item])
def read_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).all()

@app.get("/api/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}


@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    item_id: int | None = None
):
    """ファイルを S3 にアップロード"""
    try:
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        # S3 キーを作成（item_id がある場合は item フォルダを使う）
        if item_id:
            s3_key = f"items/{item_id}/{file.filename}"
        else:
            s3_key = f"uploads/{file.filename}"

        # S3 にアップロード
        success = upload_to_s3(temp_path, s3_key)
        if not success:
            return {"error": "Failed to upload to S3"}

        # PostgreSQL にメタデータを記録
        db = SessionLocal()
        try:
            file_record = models.File(  # ← 元のままでOK
                filename=file.filename,
                s3_key=s3_key,
                file_size=len(contents),
                item_id=item_id
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)
            return schemas.File.model_validate(file_record)  # ← 元のままでOK
        finally:
            db.close()
            os.unlink(temp_path)  # 一時ファイル削除
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/files")
def list_files(item_id: int | None = None, db: Session = Depends(get_db)):
    """ファイル一覧を取得"""
    query = db.query(models.File)
    if item_id:
        query = query.filter(models.File.item_id == item_id)
    files = query.all()
    return [schemas.File.model_validate(f) for f in files]


@app.delete("/api/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """ファイルを削除（S3 + PostgreSQL）"""
    file_record = db.query(models.File).filter(models.File.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # S3 から削除
    from .s3_utils import delete_from_s3
    success = delete_from_s3(file_record.s3_key)
    
    # PostgreSQL から削除
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted", "file_id": file_id}
