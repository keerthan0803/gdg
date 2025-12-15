# Frontend Documentation

## Overview

The frontend is a React application built with TypeScript, Vite, and TailwindCSS. It provides a dashboard for managing leads and monitoring autonomous agent actions.

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── LeadsList.tsx
│   │   ├── LeadDetail.tsx
│   │   └── CreateLead.tsx
│   ├── api.ts          # API client and type definitions
│   ├── App.tsx         # Main app component with routing
│   ├── main.tsx        # Application entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
├── tailwind.config.js  # TailwindCSS configuration
└── postcss.config.js   # PostCSS configuration
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment (Optional)

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

If not specified, defaults to `http://localhost:8000`.

### 3. Run Development Server

```bash
npm run dev
```

Application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

Production files will be in `dist/` directory.

## Features

### Dashboard (`/`)

Overview of lead qualification pipeline:

- **Stats Cards**: Total leads, qualified, nurture, average score
- **Charts**: 
  - Pie chart: Leads by status distribution
  - Bar chart: Leads by source
- **Quick Stats**: Recent conversions, disqualified leads, qualification rate

### Leads List (`/leads`)

Manage all leads:

- **Filters**: Status, minimum score, source
- **Pagination**: Navigate through large datasets
- **Actions**: View lead details
- **Display**: Lead info, company, score, status, source, created date

### Lead Detail (`/leads/:id`)

Detailed lead information:

- **Lead Information**: Contact details, company info
- **AI Analysis**: Complete reasoning and insights
- **Agent Actions**: Audit trail of all actions taken
- **Scoring**: Visual representation of all scores
  - Overall score
  - ICP fit
  - Intent
  - Engagement
- **Status**: Current status and recommended action
- **CRM Integration**: Sync status and CRM ID
- **Actions**: 
  - Enrich: Manually trigger enrichment
  - Re-Score: Recalculate scores
  - Process: Run autonomous agent

### Create Lead (`/leads/create`)

Add new leads:

- **Form Fields**:
  - Email (required)
  - First name
  - Last name
  - Phone
  - Job title
  - Company name
  - Company domain
  - Source
  - Notes
- **Auto-Processing**: Lead is automatically processed on creation

## API Integration

### API Client (`src/api.ts`)

Centralized API client using Axios:

```typescript
import { getLeads, createLead, getLead } from './api';

// Get paginated leads
const leads = await getLeads({ page: 1, page_size: 20 });

// Create new lead
const lead = await createLead({
  email: 'john@company.com',
  first_name: 'John',
  source: 'website_form'
});

// Get specific lead
const lead = await getLead(1);
```

### Type Definitions

All API types are defined in `api.ts`:

```typescript
interface Lead {
  id: number;
  email: string;
  first_name?: string;
  lead_score: number;
  status: string;
  // ... more fields
}
```

### React Query Integration

Data fetching with caching:

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['leads', page],
  queryFn: () => getLeads({ page }),
});
```

Mutations for data updates:

```typescript
const createMutation = useMutation({
  mutationFn: createLead,
  onSuccess: (data) => {
    // Handle success
  },
});
```

## Components

### Dashboard Stats

Displays key metrics using cards and charts:

```tsx
<DashboardStats
  totalLeads={150}
  qualifiedLeads={45}
  averageScore={62.5}
/>
```

### Lead List Table

Sortable, filterable table:

```tsx
<LeadsList
  leads={leads}
  onLeadClick={(id) => navigate(`/leads/${id}`)}
/>
```

### Score Visualization

Visual representation of scores:

```tsx
<ScoreBar
  score={lead.lead_score}
  label="Overall Score"
  color="primary"
/>
```

## Styling

### TailwindCSS

Utility-first CSS framework:

```tsx
<div className="bg-white shadow rounded-lg p-6">
  <h3 className="text-lg font-medium text-gray-900">Title</h3>
</div>
```

### Color Scheme

Primary colors defined in `tailwind.config.js`:

```javascript
colors: {
  primary: {
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
  }
}
```

### Responsive Design

Mobile-first approach:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Responsive grid */}
</div>
```

## Routing

React Router v6 configuration:

```tsx
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/leads" element={<LeadsList />} />
  <Route path="/leads/create" element={<CreateLead />} />
  <Route path="/leads/:id" element={<LeadDetail />} />
</Routes>
```

## State Management

### Local State

Component-level state with `useState`:

```tsx
const [page, setPage] = useState(1);
const [filters, setFilters] = useState({ status: '' });
```

### Server State

React Query for server data:

```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['leads'],
  queryFn: getLeads,
});
```

## Icons

Lucide React icons:

```tsx
import { Home, Users, Plus } from 'lucide-react';

<Home className="w-5 h-5" />
```

## Charts

Recharts library for visualizations:

```tsx
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

<BarChart data={data}>
  <Bar dataKey="value" fill="#0ea5e9" />
</BarChart>
```

## Error Handling

Graceful error states:

```tsx
if (isLoading) {
  return <LoadingSpinner />;
}

if (error) {
  return <ErrorMessage message="Failed to load data" />;
}
```

## Performance Optimization

1. **Code Splitting**: React.lazy for route-based splitting
2. **Memoization**: useMemo and useCallback for expensive operations
3. **Query Caching**: React Query automatic caching
4. **Image Optimization**: Lazy loading for images

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Tips

### Hot Module Replacement

Vite provides instant HMR:

```bash
npm run dev
# Changes reflect immediately without full reload
```

### TypeScript

Type checking:

```bash
npx tsc --noEmit
```

### Linting

ESLint configuration:

```bash
npm run lint
```

## Building for Production

### Build Process

```bash
npm run build
```

Optimizations:
- Minification
- Tree shaking
- Code splitting
- Asset optimization

### Preview Production Build

```bash
npm run preview
```

## Deployment

### Static Hosting

Deploy `dist/` folder to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Environment Variables

Set `VITE_API_URL` to production backend URL.

## Troubleshooting

### Port 3000 Already in Use

Change port in `vite.config.ts`:

```typescript
server: {
  port: 3001
}
```

### API Connection Issues

1. Check backend is running
2. Verify CORS settings
3. Check API URL in `.env`

### Build Errors

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear cache: `rm -rf node_modules/.vite`
3. Check TypeScript errors: `npx tsc --noEmit`

### Styling Issues

1. Ensure PostCSS is configured
2. Check TailwindCSS config
3. Verify `index.css` imports Tailwind directives

## Future Enhancements

- [ ] Real-time updates via WebSockets
- [ ] Advanced filtering and search
- [ ] Bulk actions
- [ ] Export functionality
- [ ] User authentication
- [ ] Role-based access control
- [ ] Dark mode
- [ ] Mobile app version
