from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.eligibility import router as eligibility_router

app = FastAPI(
    title="Tulong AI",
    description="Filipino Social Services Eligibility API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eligibility_router, prefix="/api/eligibility", tags=["eligibility"])


@app.get("/")
async def root():
    return {
        "message": "Tulong AI — Filipino Social Services Eligibility System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}