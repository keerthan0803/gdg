import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Lead {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  company_name?: string;
  company_domain?: string;
  company_size?: number;
  company_industry?: string;
  company_location?: string;
  source: string;
  status: string;
  lead_score: number;
  icp_fit_score: number;
  intent_score: number;
  engagement_score: number;
  buying_intent?: string;
  sales_stage?: string;
  recommended_action?: string;
  ai_reasoning?: string;
  enrichment_data?: any;
  technographic_data?: any;
  crm_id?: string;
  crm_synced_at?: string;
  created_at: string;
  updated_at: string;
  last_contacted_at?: string;
  notes?: string;
}

export interface CreateLead {
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  company_name?: string;
  company_domain?: string;
  source?: string;
  notes?: string;
}

export interface LeadListResponse {
  total: number;
  page: number;
  page_size: number;
  leads: Lead[];
}

export interface DashboardStats {
  total_leads: number;
  qualified_leads: number;
  nurture_leads: number;
  disqualified_leads: number;
  average_score: number;
  leads_by_status: Record<string, number>;
  leads_by_source: Record<string, number>;
  recent_conversions: number;
}

export interface AgentAction {
  id: number;
  lead_id: number;
  action_type: string;
  action_description?: string;
  action_input?: any;
  action_output?: any;
  reasoning?: string;
  confidence?: number;
  status: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface Conversation {
  id: number;
  lead_id: number;
  sender: string;
  message: string;
  channel?: string;
  metadata?: any;
  created_at: string;
}

// Lead APIs
export const getLeads = async (params?: {
  page?: number;
  page_size?: number;
  status?: string;
  min_score?: number;
  source?: string;
}): Promise<LeadListResponse> => {
  const response = await api.get('/api/leads', { params });
  return response.data;
};

export const getLead = async (id: number): Promise<Lead> => {
  const response = await api.get(`/api/leads/${id}`);
  return response.data;
};

export const createLead = async (lead: CreateLead): Promise<Lead> => {
  const response = await api.post('/api/leads', lead);
  return response.data;
};

export const updateLead = async (id: number, data: Partial<Lead>): Promise<Lead> => {
  const response = await api.patch(`/api/leads/${id}`, data);
  return response.data;
};

export const deleteLead = async (id: number): Promise<void> => {
  await api.delete(`/api/leads/${id}`);
};

// Enrichment APIs
export const enrichLead = async (id: number): Promise<any> => {
  const response = await api.post(`/api/leads/${id}/enrich`);
  return response.data;
};

// Scoring APIs
export const scoreLead = async (id: number): Promise<any> => {
  const response = await api.post(`/api/leads/${id}/score`);
  return response.data;
};

// Agent APIs
export const processLead = async (id: number): Promise<any> => {
  const response = await api.post(`/api/leads/${id}/process`);
  return response.data;
};

export const getLeadActions = async (id: number): Promise<AgentAction[]> => {
  const response = await api.get(`/api/leads/${id}/actions`);
  return response.data;
};

// Conversation APIs
export const getLeadConversations = async (id: number): Promise<Conversation[]> => {
  const response = await api.get(`/api/leads/${id}/conversations`);
  return response.data;
};

// Dashboard APIs
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/api/dashboard/stats');
  return response.data;
};

export default api;
