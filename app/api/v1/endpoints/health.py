from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['health'])


@router.get('', response_model=bool)
async def health() -> bool:
    return True
