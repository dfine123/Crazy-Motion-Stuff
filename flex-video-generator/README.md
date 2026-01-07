# Flex Video Generator

A full-stack admin platform for mass-generating Instagram "money/info flex" videos.

## Features

- **Creator Management**: Store creator profiles with brand voice, style preferences, and content guidelines
- **Audio Library**: Manage audio tracks with beat timestamps, mood context, and pacing guides
- **Clip Analysis**: Auto-analyze uploaded clips using Twelve Labs API for structured metadata
- **AI-Powered Generation**: Claude AI selects and orders clips based on audio beats and creator brand alignment
- **Caption Generation**: AI-generated optimized captions following Instagram best practices
- **Video Rendering**: FFmpeg-based rendering with audio sync and caption overlays

## Tech Stack

- **Frontend**: Next.js 14+ (App Router) + React + TailwindCSS + shadcn/ui
- **Backend**: Python FastAPI
- **Database**: PostgreSQL with JSON columns
- **Video Processing**: FFmpeg + MoviePy
- **AI Integration**: Anthropic Claude API + Twelve Labs API
- **ORM**: SQLAlchemy

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- FFmpeg installed locally (for development)

### Quick Start

1. Clone the repository and navigate to the project:
   ```bash
   cd flex-video-generator
   ```

2. Copy the environment file and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your ANTHROPIC_API_KEY and TWELVE_LABS_API_KEY
   ```

3. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Initialize the database:
   ```bash
   cd backend && python scripts/init_db.py
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Setup (without Docker)

1. Start PostgreSQL locally or use Docker for just the database:
   ```bash
   docker-compose up -d db
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Project Structure

```
/flex-video-generator
├── /frontend                    # Next.js application
│   ├── /app                     # App Router pages
│   ├── /components              # React components
│   └── /lib                     # Utilities and types
├── /backend                     # FastAPI application
│   ├── /app
│   │   ├── /api/routes          # API endpoints
│   │   ├── /models              # SQLAlchemy models
│   │   ├── /schemas             # Pydantic schemas
│   │   ├── /services            # Business logic
│   │   └── /core                # Configuration
│   └── requirements.txt
├── /storage                     # File storage
│   ├── /audio                   # Audio files
│   ├── /clips                   # Video clips by creator
│   ├── /exports                 # Generated videos
│   └── /temp                    # Processing workspace
├── /scripts                     # Utility scripts
├── docker-compose.yml
└── .env.example
```

## API Endpoints

- `POST /api/creators` - Create creator
- `GET /api/creators` - List all creators
- `GET /api/creators/{id}` - Get creator details
- `PUT /api/creators/{id}` - Update creator
- `DELETE /api/creators/{id}` - Delete creator
- `POST /api/audio` - Upload audio
- `GET /api/audio` - List audio tracks
- `PUT /api/audio/{id}/timestamps` - Update beat timestamps
- `POST /api/clips/upload` - Upload clips (triggers Twelve Labs analysis)
- `POST /api/clips/import` - Import from spreadsheet
- `GET /api/clips` - List clips for creator
- `POST /api/generate` - Start video generation
- `GET /api/generate/{id}` - Get generation status
- `GET /api/generate/history` - List past generations

## License

Private - Internal use only.
