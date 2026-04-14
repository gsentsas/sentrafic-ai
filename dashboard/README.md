# SEN TRAFIC AI Dashboard

Professional B2B dashboard for computer vision traffic analysis in Senegal/Dakar.

## Features

- Real-time traffic monitoring across multiple camera sites
- Live camera feeds and traffic metrics
- Advanced analytics with vehicle classification
- Alert management and notifications
- Site and camera management
- Professional dark-themed interface
- Responsive design with Recharts visualizations

## Tech Stack

- **Framework**: Next.js 14.1.0
- **UI Library**: React 18.2.0
- **Charts**: Recharts 2.10.0
- **Styling**: Tailwind CSS 3.4.1
- **Icons**: Lucide React 0.312.0
- **Language**: TypeScript 5.3.3

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Environment Setup

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3001](http://localhost:3001) in your browser.

### Production Build

```bash
npm run build
npm run start
```

## Project Structure

```
dashboard/
├── app/                 # Next.js pages and routes
├── components/
│   ├── ui/             # Base UI components
│   ├── cards/          # Card components (KPI, status, alert)
│   ├── charts/         # Chart components
│   ├── tables/         # Table components
│   ├── layout/         # Layout components (sidebar, topbar)
│   └── live/           # Live view components
├── hooks/              # Custom React hooks
├── lib/                # Utilities and types
└── public/             # Static assets
```

## API Integration

The dashboard connects to a FastAPI backend at the URL specified by `NEXT_PUBLIC_API_URL`.

Key endpoints:
- `POST /api/auth/login` - User authentication
- `GET /api/dashboard/overview` - Dashboard metrics
- `GET /api/sites` - List of monitoring sites
- `GET /api/cameras` - List of cameras
- `GET /api/alerts` - Traffic alerts
- `GET /api/analytics/traffic` - Traffic data
- `GET /api/analytics/distribution` - Vehicle class distribution

## Authentication

The dashboard uses JWT token-based authentication. Tokens are stored in localStorage and automatically included in API requests.

## Design System

### Colors

- **Primary Blue**: #2563EB
- **Success Green**: #10B981
- **Warning Amber**: #F59E0B
- **Danger Red**: #EF4444
- **Sidebar Dark**: #0F172A
- **Background Light**: #FFFFFF

### Typography

- Font: Inter (system fallback)
- Responsive sizing for various breakpoints

## License

Proprietary - SEN TRAFIC AI
