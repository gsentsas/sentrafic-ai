'use client';

import { useState } from 'react';
import { Plus, MapPin } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Modal } from '@/components/ui/modal';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { SitesTable } from '@/components/tables/sites-table';
import { useSites } from '@/hooks/use-sites';
import { createSite } from '@/lib/api';

const SITE_TYPE_OPTIONS = [
  { value: 'intersection', label: 'Carrefour / Intersection' },
  { value: 'highway', label: 'Autoroute' },
  { value: 'parking', label: 'Parking' },
  { value: 'logistics', label: 'Zone logistique' },
  { value: 'bus_station', label: 'Gare routière' },
  { value: 'industrial', label: 'Zone industrielle' },
];

interface SiteForm {
  name: string;
  address: string;
  city: string;
  latitude: string;
  longitude: string;
  site_type: string;
}

const EMPTY_FORM: SiteForm = {
  name: '',
  address: '',
  city: 'Dakar',
  latitude: '',
  longitude: '',
  site_type: 'intersection',
};

export default function SitesPage() {
  const { sites, loading, error, refetch } = useSites();

  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<SiteForm>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const handleChange = (field: keyof SiteForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFormError('');
  };

  const validate = (): string => {
    if (!form.name.trim()) return 'Le nom du site est obligatoire.';
    if (!form.address.trim()) return "L'adresse est obligatoire.";
    if (!form.city.trim()) return 'La ville est obligatoire.';
    const lat = parseFloat(form.latitude);
    const lng = parseFloat(form.longitude);
    if (isNaN(lat) || lat < -90 || lat > 90) return 'Latitude invalide (entre -90 et 90).';
    if (isNaN(lng) || lng < -180 || lng > 180) return 'Longitude invalide (entre -180 et 180).';
    return '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) { setFormError(err); return; }

    setSubmitting(true);
    setFormError('');
    try {
      await createSite({
        name: form.name.trim(),
        address: form.address.trim(),
        city: form.city.trim(),
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        site_type: form.site_type,
      });
      setShowModal(false);
      setForm(EMPTY_FORM);
      await refetch();
    } catch (e: any) {
      setFormError(e.message || 'Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredSites = typeFilter
    ? sites.filter((s) => s.site_type === typeFilter)
    : sites;

  if (loading) return <PageShell title="Sites"><LoadingState /></PageShell>;
  if (error) return (
    <PageShell title="Sites">
      <ErrorState message="Impossible de charger les sites. Veuillez réessayer." onRetry={refetch} />
    </PageShell>
  );

  return (
    <PageShell title="Sites">
      {/* En-tête */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {sites.length} {sites.length === 1 ? 'Site' : 'Sites'}
          </h2>
          <p className="text-gray-500">Gérez vos sites de surveillance du trafic</p>
        </div>
        <Button variant="primary" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouveau site
        </Button>
      </div>

      {/* Filtre par type */}
      {sites.length > 0 && (
        <div className="mb-6 max-w-xs">
          <Select
            label="Filtrer par type"
            options={[
              { value: '', label: 'Tous les types' },
              ...SITE_TYPE_OPTIONS,
            ]}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          />
        </div>
      )}

      {filteredSites.length > 0 ? (
        <SitesTable sites={filteredSites} />
      ) : (
        <Card>
          <EmptyState
            icon={MapPin}
            title={typeFilter ? 'Aucun site pour ce type' : 'Aucun site configuré'}
            description={
              typeFilter
                ? 'Essayez un autre filtre ou créez un site de ce type.'
                : 'Créez votre premier site de surveillance pour commencer.'
            }
            actionLabel="Créer un site"
          />
        </Card>
      )}

      {/* Modal création */}
      <Modal
        isOpen={showModal}
        onClose={() => { setShowModal(false); setForm(EMPTY_FORM); setFormError(''); }}
        title="Nouveau site de surveillance"
        maxWidth="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nom du site *"
            type="text"
            placeholder="Ex : Carrefour Malick Sy"
            value={form.name}
            onChange={handleChange('name')}
          />
          <Input
            label="Adresse *"
            type="text"
            placeholder="Ex : Rue Carnot, Plateau"
            value={form.address}
            onChange={handleChange('address')}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Ville *"
              type="text"
              placeholder="Dakar"
              value={form.city}
              onChange={handleChange('city')}
            />
            <Select
              label="Type de site"
              options={SITE_TYPE_OPTIONS}
              value={form.site_type}
              onChange={handleChange('site_type')}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Latitude *"
              type="number"
              step="0.000001"
              placeholder="14.6937"
              value={form.latitude}
              onChange={handleChange('latitude')}
            />
            <Input
              label="Longitude *"
              type="number"
              step="0.000001"
              placeholder="-17.4441"
              value={form.longitude}
              onChange={handleChange('longitude')}
            />
          </div>

          {formError && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{formError}</p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => { setShowModal(false); setForm(EMPTY_FORM); setFormError(''); }}
            >
              Annuler
            </Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? 'Création...' : 'Créer le site'}
            </Button>
          </div>
        </form>
      </Modal>
    </PageShell>
  );
}
