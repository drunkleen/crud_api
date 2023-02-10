from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from .. import schemas, basemodel, oauth2
from ..db_connection import Session, get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.GetPost])
def get_all_posts(datab: Session = Depends(get_db)):
    posts = datab.query(basemodel.Post).all()

    return posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostCreate)
def create_post(n_post: schemas.PostCreate, datab: Session = Depends(get_db),
                current_user: id = Depends(oauth2.get_current_user)):

    new_post = basemodel.Post(**n_post.dict())
    datab.add(new_post)  # add the new post
    datab.commit()  # push the new changes into database
    datab.refresh(new_post)  # returning post from database

    return new_post


@router.get('/{post_id}', response_model=schemas.GetPost)
def get_post(post_id: int, datab: Session = Depends(get_db)):
    post = datab.query(basemodel.Post).filter(basemodel.Post.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"post with {post_id} doesn't exist.")

    return post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, datab: Session = Depends(get_db),
                current_user: id = Depends(oauth2.get_current_user)):

    deleted_post = datab.query(basemodel.Post).filter(basemodel.Post.id == post_id)
    if not deleted_post.first():  # check if there is not matched id
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"post with {post_id} doesn't exist.")
    deleted_post.delete(synchronize_session=False)
    datab.commit()  # push the new changes into database

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/{post_id}')
def update_post(post_id: int, post: schemas.PostCreate, datab: Session = Depends(get_db),
                current_user: id = Depends(oauth2.get_current_user)):
    post_query = datab.query(basemodel.Post).filter(basemodel.Post.id == post_id)
    updated_post = post_query.first()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {post_id} doesn't exist.")
    post_query.update(post.dict(), synchronize_session=False)
    datab.commit()  # push the new changes into database

    return post_query.first()
