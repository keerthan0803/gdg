import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLead, getLeadActions, processLead, enrichLead, scoreLead } from '../api';
import { ArrowLeft, RefreshCw, Play, Mail, Calendar, TrendingUp } from 'lucide-react';

const LeadDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: lead, isLoading } = useQuery({
    queryKey: ['lead', id],
    queryFn: () => getLead(Number(id)),
  });

  const { data: actions } = useQuery({
    queryKey: ['lead-actions', id],
    queryFn: () => getLeadActions(Number(id)),
  });

  const processMutation = useMutation({
    mutationFn: () => processLead(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
      queryClient.invalidateQueries({ queryKey: ['lead-actions', id] });
    },
  });

  const enrichMutation = useMutation({
    mutationFn: () => enrichLead(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
    },
  });

  const scoreMutation = useMutation({
    mutationFn: () => scoreLead(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!lead) {
    return <div>Lead not found</div>;
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-gray-100 text-gray-800',
      qualified: 'bg-green-100 text-green-800',
      nurture: 'bg-yellow-100 text-yellow-800',
      disqualified: 'bg-red-100 text-red-800',
      contacted: 'bg-blue-100 text-blue-800',
      scheduled: 'bg-purple-100 text-purple-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/leads')}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {lead.first_name} {lead.last_name}
            </h2>
            <p className="mt-1 text-sm text-gray-500">{lead.email}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => enrichMutation.mutate()}
            disabled={enrichMutation.isPending}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${enrichMutation.isPending ? 'animate-spin' : ''}`} />
            Enrich
          </button>
          <button
            onClick={() => scoreMutation.mutate()}
            disabled={scoreMutation.isPending}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Re-Score
          </button>
          <button
            onClick={() => processMutation.mutate()}
            disabled={processMutation.isPending}
            className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
          >
            <Play className={`w-4 h-4 mr-2 ${processMutation.isPending ? 'animate-spin' : ''}`} />
            Process
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Lead Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Lead Details */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="text-sm font-medium text-gray-900">{lead.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="text-sm font-medium text-gray-900">{lead.phone || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Job Title</p>
                <p className="text-sm font-medium text-gray-900">{lead.job_title || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Company</p>
                <p className="text-sm font-medium text-gray-900">{lead.company_name || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Company Size</p>
                <p className="text-sm font-medium text-gray-900">
                  {lead.company_size ? `${lead.company_size} employees` : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Industry</p>
                <p className="text-sm font-medium text-gray-900">{lead.company_industry || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Location</p>
                <p className="text-sm font-medium text-gray-900">{lead.company_location || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Source</p>
                <p className="text-sm font-medium text-gray-900">{lead.source.replace('_', ' ')}</p>
              </div>
            </div>
            {lead.notes && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Notes</p>
                <p className="text-sm text-gray-900 mt-1">{lead.notes}</p>
              </div>
            )}
          </div>

          {/* AI Reasoning */}
          {lead.ai_reasoning && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">AI Analysis</h3>
              <div className="prose prose-sm max-w-none">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {lead.ai_reasoning}
                </pre>
              </div>
            </div>
          )}

          {/* Agent Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Actions</h3>
            {actions && actions.length > 0 ? (
              <div className="space-y-4">
                {actions.map((action) => (
                  <div key={action.id} className="border-l-4 border-primary-500 pl-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">
                        {action.action_type.replace('_', ' ').toUpperCase()}
                      </p>
                      <span className={`text-xs px-2 py-1 rounded ${
                        action.status === 'completed' ? 'bg-green-100 text-green-800' :
                        action.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {action.status}
                      </span>
                    </div>
                    {action.action_description && (
                      <p className="text-sm text-gray-500 mt-1">{action.action_description}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(action.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No actions yet</p>
            )}
          </div>
        </div>

        {/* Right Column - Scoring */}
        <div className="space-y-6">
          {/* Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Status</h3>
            <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${getStatusColor(lead.status)}`}>
              {lead.status}
            </span>
            {lead.recommended_action && (
              <div className="mt-4">
                <p className="text-sm text-gray-500">Recommended Action</p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {lead.recommended_action.replace('_', ' ').toUpperCase()}
                </p>
              </div>
            )}
          </div>

          {/* Scores */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Scoring</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-sm text-gray-500">Overall Score</p>
                  <p className={`text-2xl font-bold ${getScoreColor(lead.lead_score)}`}>
                    {lead.lead_score.toFixed(1)}
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${lead.lead_score}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-sm text-gray-500">ICP Fit</p>
                  <p className="text-sm font-medium">{lead.icp_fit_score.toFixed(1)}</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${lead.icp_fit_score}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-sm text-gray-500">Intent</p>
                  <p className="text-sm font-medium">{lead.intent_score.toFixed(1)}</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-600 h-2 rounded-full"
                    style={{ width: `${lead.intent_score}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-sm text-gray-500">Engagement</p>
                  <p className="text-sm font-medium">{lead.engagement_score.toFixed(1)}</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${lead.engagement_score}%` }}
                  />
                </div>
              </div>
            </div>

            {lead.sales_stage && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-500">Sales Stage</p>
                <p className="text-sm font-medium text-gray-900 mt-1">{lead.sales_stage}</p>
              </div>
            )}

            {lead.buying_intent && (
              <div className="mt-2">
                <p className="text-sm text-gray-500">Buying Intent</p>
                <p className="text-sm font-medium text-gray-900 mt-1">{lead.buying_intent}</p>
              </div>
            )}
          </div>

          {/* CRM Sync */}
          {lead.crm_id && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">CRM Integration</h3>
              <div>
                <p className="text-sm text-gray-500">CRM ID</p>
                <p className="text-sm font-medium text-gray-900">{lead.crm_id}</p>
              </div>
              {lead.crm_synced_at && (
                <div className="mt-2">
                  <p className="text-sm text-gray-500">Last Synced</p>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(lead.crm_synced_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeadDetail;
