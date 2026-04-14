import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  padding?: 'sm' | 'md' | 'lg';
}

const paddingStyles = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card = ({
  children,
  className,
  style,
  header,
  footer,
  padding = 'md',
}: CardProps) => {
  return (
    <div className={clsx('card-base', className)} style={style}>
      {header && (
        <div className={clsx('border-b border-gray-200', paddingStyles[padding])}>
          {header}
        </div>
      )}
      <div className={paddingStyles[padding]}>{children}</div>
      {footer && (
        <div className={clsx('border-t border-gray-200', paddingStyles[padding])}>
          {footer}
        </div>
      )}
    </div>
  );
};
