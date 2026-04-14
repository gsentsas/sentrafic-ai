import { AlertCircle } from 'lucide-react';
import { Button } from './button';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorState = ({ message, onRetry }: ErrorStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 bg-red-50 rounded-lg border border-red-200 p-6">
      <AlertCircle className="h-12 w-12 text-danger mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Une erreur est survenue</h3>
      <p className="text-gray-600 text-center max-w-sm mb-6">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Réessayer
        </Button>
      )}
    </div>
  );
};
