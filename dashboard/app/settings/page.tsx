'use client';

import { useState, useEffect, useCallback } from 'react';
import { PageShell } from '@/components/layout/page-shell';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
import { getUserFromToken } from '@/lib/auth';
import { getUsers, createUser, updateUser, changeMyPassword } from '@/lib/api';
import { User, UserCreate } from '@/lib/types';
import {
  Package, Lock, Users, Plus, CheckCircle, XCircle,
} from 'lucide-react';

const ROLE_OPTIONS = [
  { value: 'viewer', label: 'Observateur' },
  { value: 'operator', label: 'Opérateur' },
  { value: 'admin', label: 'Administrateur' },
];

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrateur',
  operator: 'Opérateur',
  viewer: 'Observateur',
};

const ROLE_VARIANTS: Record<string, 'success' | 'warning' | 'default'> = {
  admin: 'success',
  operator: 'warning',
  viewer: 'default',
};

// ─── Composant interne : formulaire de changement de mot de passe ────────────

function PasswordSection() {
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((p) => ({ ...p, [field]: e.target.value }));
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.current_password) { setError('Mot de passe actuel requis.'); return; }
    if (form.new_password.length < 6) { setError('Le nouveau mot de passe doit contenir au moins 6 caractères.'); return; }
    if (form.new_password !== form.confirm) { setError('Les mots de passe ne correspondent pas.'); return; }

    setLoading(true);
    try {
      const res = await changeMyPassword({
        current_password: form.current_password,
        new_password: form.new_password,
      });
      setSuccess(res.message || 'Mot de passe mis à jour avec succès.');
      setForm({ current_password: '', new_password: '', confirm: '' });
    } catch (e: any) {
      setError(e.message || 'Erreur lors du changement de mot de passe.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Mot de passe actuel"
        type="password"
        value={form.current_password}
        onChange={handleChange('current_password')}
      />
      <Input
        label="Nouveau mot de passe"
        type="password"
        value={form.new_password}
        onChange={handleChange('new_password')}
      />
      <Input
        label="Confirmer le nouveau mot de passe"
        type="password"
        value={form.confirm}
        onChange={handleChange('confirm')}
      />
      {error && (
        <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg flex items-center gap-2">
          <XCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </p>
      )}
      {success && (
        <p className="text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          {success}
        </p>
      )}
      <div className="flex justify-end">
        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Mise à jour...' : 'Changer le mot de passe'}
        </Button>
      </div>
    </form>
  );
}

// ─── Composant interne : gestion des utilisateurs (admin) ────────────────────

function UsersSection() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [togglingId, setTogglingId] = useState<string | null>(null);
  const [form, setForm] = useState<UserCreate & { confirm: string }>({
    email: '', password: '', confirm: '', full_name: '', role: 'viewer',
  });
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setUsers(await getUsers());
    } catch (e: any) {
      setError(e.message || 'Impossible de charger les utilisateurs.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleFormChange = (field: string) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((p: any) => ({ ...p, [field]: e.target.value }));
    setFormError('');
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email.trim()) { setFormError("L'email est obligatoire."); return; }
    if (form.password.length < 6) { setFormError('Le mot de passe doit contenir au moins 6 caractères.'); return; }
    if (form.password !== form.confirm) { setFormError('Les mots de passe ne correspondent pas.'); return; }

    setSubmitting(true);
    try {
      await createUser({ email: form.email.trim(), password: form.password, full_name: form.full_name, role: form.role });
      setShowModal(false);
      setForm({ email: '', password: '', confirm: '', full_name: '', role: 'viewer' });
      await load();
    } catch (e: any) {
      setFormError(e.message || 'Erreur lors de la création.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggle = async (user: User) => {
    setTogglingId(user.id);
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      await load();
    } catch {
      // silencieux
    } finally {
      setTogglingId(null);
    }
  };

  const handleRoleChange = async (user: User, role: string) => {
    try {
      await updateUser(user.id, { role });
      await load();
    } catch {
      // silencieux
    }
  };

  if (loading) return <p className="text-sm text-gray-500">Chargement des utilisateurs…</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-600">{users.length} utilisateur{users.length > 1 ? 's' : ''}</p>
        <Button variant="primary" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvel utilisateur
        </Button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rôle</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actif</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{u.full_name || '—'}</td>
                <td className="px-4 py-3 text-gray-600">{u.email}</td>
                <td className="px-4 py-3">
                  <select
                    value={u.role}
                    onChange={(e) => handleRoleChange(u, e.target.value)}
                    className="text-xs border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {ROLE_OPTIONS.map((r) => (
                      <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={u.is_active ? 'success' : 'default'}>
                    {u.is_active ? 'Actif' : 'Inactif'}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggle(u)}
                    disabled={togglingId === u.id}
                    className={`relative inline-flex h-5 w-10 items-center rounded-full transition-colors ${
                      u.is_active ? 'bg-green-500' : 'bg-gray-300'
                    } ${togglingId === u.id ? 'opacity-50' : 'cursor-pointer'}`}
                  >
                    <span
                      className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                        u.is_active ? 'translate-x-5' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => { setShowModal(false); setFormError(''); }}
        title="Nouvel utilisateur"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Input label="Email *" type="email" value={form.email} onChange={handleFormChange('email')} />
          <Input label="Nom complet" type="text" value={form.full_name} onChange={handleFormChange('full_name')} />
          <Select label="Rôle" options={ROLE_OPTIONS} value={form.role} onChange={handleFormChange('role')} />
          <Input label="Mot de passe *" type="password" value={form.password} onChange={handleFormChange('password')} />
          <Input label="Confirmer le mot de passe *" type="password" value={form.confirm} onChange={handleFormChange('confirm')} />
          {formError && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{formError}</p>
          )}
          <div className="flex justify-end gap-3 pt-1">
            <Button type="button" variant="secondary" onClick={() => setShowModal(false)}>Annuler</Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? 'Création...' : 'Créer'}
            </Button>
          </div>
        </form>
      </Modal>
    </>
  );
}

// ─── Page principale ──────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [user, setUser] = useState<Partial<User> | null>(null);
  useEffect(() => { setUser(getUserFromToken()); }, []);

  const isAdmin = user?.role === 'admin';

  return (
    <PageShell title="Paramètres">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">Paramètres du système</h2>
        <p className="text-gray-500">Gérez votre compte et la configuration de la plateforme</p>
      </div>

      <div className="max-w-2xl space-y-6">

        {/* Profil */}
        <Card header={
          <div className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-gray-500" />
            <h3 className="font-semibold text-gray-900">Mon profil</h3>
          </div>
        }>
          <div className="space-y-3 mb-5">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Nom</span>
              <span className="font-medium text-gray-900">{user?.full_name || '—'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Email</span>
              <span className="font-medium text-gray-900">{user?.email || '—'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Rôle</span>
              <Badge variant={ROLE_VARIANTS[user?.role ?? 'viewer'] ?? 'default'}>
                {ROLE_LABELS[user?.role ?? ''] ?? user?.role ?? '—'}
              </Badge>
            </div>
          </div>
          <div className="border-t border-gray-100 pt-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Changer le mot de passe</p>
            <PasswordSection />
          </div>
        </Card>

        {/* Gestion utilisateurs (admin) */}
        {isAdmin && (
          <Card header={
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-gray-500" />
              <h3 className="font-semibold text-gray-900">Gestion des utilisateurs</h3>
            </div>
          }>
            <UsersSection />
          </Card>
        )}

        {/* Infos système */}
        <Card header={
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-gray-500" />
            <h3 className="font-semibold text-gray-900">Informations système</h3>
          </div>
        }>
          <div className="space-y-3 text-sm">
            {[
              ['Application', 'SEN TRAFIC AI'],
              ['Version', '1.0.0 MVP'],
              ['Environnement', 'Développement'],
              ['Backend', 'FastAPI 0.110+'],
              ['Base de données', 'PostgreSQL 14'],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between">
                <span className="text-gray-500">{label}</span>
                <span className="font-mono text-gray-900">{value}</span>
              </div>
            ))}
          </div>
        </Card>

      </div>
    </PageShell>
  );
}
