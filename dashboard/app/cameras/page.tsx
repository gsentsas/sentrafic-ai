'use client';

import { useState } from 'react';
import { Plus, Camera as CameraIcon } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Modal } from '@/components/ui/modal';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { CamerasTable } from '@/components/tables/cameras-table';
import { useCameras } from '@/hooks/use-cameras';
import { useSites } from '@/hooks/use-sites';
import { createCamera } from '@/lib/api';

interface CameraForm {
  site_id: string;
  name: string;
  stream_url: string;
  location_description: string;
}

const EMPTY_FORM: CameraForm = {
  site_id: '',
  name: '',
  stream_url: '',
  location_description: '',
};

export default function CamerasPage() {
  const [selectedSite, setSelectedSite] = useState('');
  const { cameras, loading, error, refetch } = useCameras(selectedSite || undefined);
  const { sites } = useSites();

  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<CameraForm>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const siteOptions = sites.map((s) => ({ value: s.id, label: s.name }));

  const handleChange =
    (field: keyof CameraForm) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
      setFormError('');
    };

  const validate = (): string => {
    if (!form.site_id) return 'Veuillez sélectionner un site.';
    if (!form.name.trim()) return 'Le nom de la caméra est obligatoire.';
    if (!form.stream_url.trim()) return "L'URL du flux est obligatoire.";
    return '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) { setFormError(err); return; }

    setSubmitting(true);
    setFormError('');
    try {
      await createCamera({
        site_id: form.site_id,
        name: form.name.trim(),
        stream_url: form.stream_url.trim(),
        location_description: form.location_description.trim() || undefined,
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

  if (loading) return <PageShell title="Caméras"><LoadingState /></PageShell>;
  if (error) return (
    <PageShell title="Caméras">
      <ErrorState
        message="Impossible de charger les caméras. Vérifiez votre connexion au backend."
        onRetry={refetch}
      />
    </PageShell>
  );

  return (
    <PageShell title="Caméras">
      {/* En-tête */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {cameras.length} {cameras.length === 1 ? 'Caméra' : 'Caméras'}
          </h2>
          <p className="text-gray-500">Gérez et surveillez vos caméras de trafic</p>
        </div>
        <Button variant="primary" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle caméra
        </Button>
      </div>

      {/* Filtre par site */}
      <div className="mb-6 max-w-xs">
        <Select
          label="Filtrer par site"
          options={[{ value: '', label: 'Tous les sites' }, ...siteOptions]}
          value={selectedSite}
          onChange={(e) => setSelectedSite(e.target.value)}
        />
      </div>

      {cameras.length > 0 ? (
        <CamerasTable cameras={cameras} onRefetch={refetch} />
      ) : (
        <Card>
          <EmptyState
            icon={CameraIcon}
            title={selectedSite ? 'Aucune caméra sur ce site' : 'Aucune caméra configurée'}
            description={
              selectedSite
                ? 'Ajoutez une caméra à ce site ou changez le filtre.'
                : 'Ajoutez une caméra pour commencer la surveillance.'
            }
            actionLabel="Ajouter une caméra"
          />
        </Card>
      )}

      {/* Modal création */}
      <Modal
        isOpen={showModal}
        onClose={() => { setShowModal(false); setForm(EMPTY_FORM); setFormError(''); }}
        title="Nouvelle caméra"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Site *"
            options={[{ value: '', label: 'Sélectionner un site…' }, ...siteOptions]}
            value={form.site_id}
            onChange={handleChange('site_id')}
          />
          <Input
            label="Nom de la caméra *"
            type="text"
            placeholder="Ex : CAM-NATION-01"
            value={form.name}
            onChange={handleChange('name')}
          />
          <Input
            label="URL du flux *"
            type="text"
            placeholder="rtsp://192.168.1.10/stream"
            value={form.stream_url}
            onChange={handleChange('stream_url')}
          />
          <Input
            label="Description de l'emplacement"
            type="text"
            placeholder="Ex : Entrée nord, vue carrefour"
            value={form.location_description}
            onChange={handleChange('location_description')}
          />

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
              {submitting ? 'Création...' : 'Créer la caméra'}
            </Button>
          </div>
        </form>
      </Modal>
    </PageShell>
  );
}
