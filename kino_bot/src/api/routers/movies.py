"""
Movies REST API endpoints.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.middleware.auth import get_auth
from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.repositories.movie_repo import MovieRepository

router = APIRouter(prefix="/movies", tags=["Movies"])


class MovieSchema(BaseModel):
    id: int
    code: str
    title: str
    title_uz: Optional[str]
    title_ru: Optional[str]
    title_en: Optional[str]
    year: int
    genres: Optional[List[str]]
    director: Optional[str]
    country: Optional[str]
    language: Optional[str]
    rating: float
    duration: Optional[str]
    view_count: int
    is_active: bool

    model_config = {"from_attributes": True}


class MovieCreateSchema(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    title: str = Field(..., min_length=1, max_length=256)
    title_uz: Optional[str] = None
    title_ru: Optional[str] = None
    title_en: Optional[str] = None
    year: int = Field(..., ge=1900, le=2100)
    genres: Optional[List[str]] = None
    director: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    duration: Optional[str] = None
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None
    description_en: Optional[str] = None
    watch_url: Optional[str] = None
    trailer_url: Optional[str] = None
    poster_url: Optional[str] = None
    tags: Optional[List[str]] = None


class PaginatedMovies(BaseModel):
    items: List[MovieSchema]
    total: int
    page: int
    per_page: int


@router.get("/", response_model=PaginatedMovies)
async def list_movies(
    page: int = Query(0, ge=0),
    per_page: int = Query(10, ge=1, le=100),
    auth=Depends(get_auth),
):
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).get_all(page=page, per_page=per_page)
    return PaginatedMovies(
        items=[MovieSchema.model_validate(m) for m in movies],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/search", response_model=PaginatedMovies)
async def search_movies(
    q: str = Query(..., min_length=2, max_length=100),
    page: int = Query(0, ge=0),
    auth=Depends(get_auth),
):
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).smart_search(q, page=page)
    return PaginatedMovies(
        items=[MovieSchema.model_validate(m) for m in movies],
        total=total,
        page=page,
        per_page=settings.movies_per_page,
    )


@router.get("/top/{period}", response_model=List[MovieSchema])
async def top_movies(
    period: str,
    limit: int = Query(10, ge=1, le=100),
    auth=Depends(get_auth),
):
    if period not in ("weekly", "monthly", "yearly", "alltime"):
        raise HTTPException(status_code=400, detail="Invalid period")
    async with AsyncSessionFactory() as session:
        movies = await MovieRepository(session).get_top_movies(period=period, limit=limit)
    return [MovieSchema.model_validate(m) for m in movies]


@router.get("/recent", response_model=PaginatedMovies)
async def recent_movies(
    page: int = Query(0, ge=0),
    auth=Depends(get_auth),
):
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).get_recent(page=page)
    return PaginatedMovies(
        items=[MovieSchema.model_validate(m) for m in movies],
        total=total,
        page=page,
        per_page=settings.movies_per_page,
    )


@router.get("/{movie_id}", response_model=MovieSchema)
async def get_movie(movie_id: int, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        movie = await MovieRepository(session).get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieSchema.model_validate(movie)


@router.post("/", response_model=MovieSchema, status_code=status.HTTP_201_CREATED)
async def create_movie(payload: MovieCreateSchema, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        repo = MovieRepository(session)
        existing = await repo.get_by_code(payload.code)
        if existing:
            raise HTTPException(status_code=400, detail="Movie with this code already exists")
        movie = await repo.create(**payload.model_dump())
        await session.commit()
    return MovieSchema.model_validate(movie)


@router.put("/{movie_id}", response_model=MovieSchema)
async def update_movie(movie_id: int, payload: MovieCreateSchema, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        movie = await MovieRepository(session).update(movie_id, **payload.model_dump(exclude_unset=True))
        await session.commit()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieSchema.model_validate(movie)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, auth=Depends(get_auth)):
    async with AsyncSessionFactory() as session:
        success = await MovieRepository(session).soft_delete(movie_id)
        await session.commit()
    if not success:
        raise HTTPException(status_code=404, detail="Movie not found")
