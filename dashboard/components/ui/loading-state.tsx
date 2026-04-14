import { Loader } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState = ({ message = 'Chargement en cours…' }: LoadingStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader className="h-8 w-8 text-primary animate-spin mb-4" />
      <p className="text-gray-600">{message}</p>
    </div>
  );
};
